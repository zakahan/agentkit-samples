
import json
import hashlib
import hmac
import datetime
import urllib.request
import urllib.error
import urllib.parse
import re
import base64
import os
from typing import Any, Dict, Optional


class DBWClient:
    def __init__(
        self,
        region: Optional[str] = None,
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        host: Optional[str] = None,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        database: Optional[str] = None,
    ):
        self.region = region or os.environ.get("VOLCENGINE_REGION", "cn-beijing")
        self.ak = ak or os.environ.get("VOLCENGINE_ACCESS_KEY")
        self.sk = sk or os.environ.get("VOLCENGINE_SECRET_KEY")
        self.host = host
        self.instance_id = instance_id or os.environ.get("VOLCENGINE_INSTANCE_ID")
        self.instance_type = instance_type or os.environ.get("VOLCENGINE_INSTANCE_TYPE")
        self.database = database or os.environ.get("VOLCENGINE_DATABASE")

        # Load from .env if still missing
        if not self.ak or not self.sk:
            try:
                env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env")
                if os.path.exists(env_path):
                    with open(env_path, "r") as f:
                        for line in f:
                            if line.startswith("export VOLCENGINE_ACCESS_KEY="):
                                self.ak = line.split("=")[1].strip().strip('"')
                            elif line.startswith("export VOLCENGINE_SECRET_KEY="):
                                self.sk = line.split("=")[1].strip().strip('"')
                            elif line.startswith("export VOLCENGINE_REGION="):
                                self.region = line.split("=")[1].strip().strip('"')
            except Exception:
                pass

    def _sign_request(
        self,
        ak: str,
        sk: str,
        region: str,
        service: str,
        method: str,
        uri: str,
        query_params: str,
        headers: Dict[str, str],
        body: str,
    ) -> str:
        canonical_headers = "\n".join([f"{k.lower()}:{v}" for k, v in sorted(headers.items())]) + "\n"
        signed_headers = ";".join([k.lower() for k in sorted(headers.keys())])
        hashed_payload = hashlib.sha256(body.encode("utf-8")).hexdigest()

        canonical_request = f"{method}\n{uri}\n{query_params}\n{canonical_headers}\n{signed_headers}\n{hashed_payload}"

        date = headers["X-Date"]
        credential_scope = f"{date[:8]}/{region}/{service}/request"
        hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
        string_to_sign = f"HMAC-SHA256\n{date}\n{credential_scope}\n{hashed_canonical_request}"
        # print(f"DEBUG: StringToSign:\n{string_to_sign}")

        if not sk:
            raise ValueError("Secret Key (SK) is missing. Please check your .env file.")

        k_date = hmac.new(sk.encode("utf-8"), date[:8].encode("utf-8"), hashlib.sha256).digest()
        k_region = hmac.new(k_date, region.encode("utf-8"), hashlib.sha256).digest()
        k_service = hmac.new(k_region, service.encode("utf-8"), hashlib.sha256).digest()
        k_signing = hmac.new(k_service, "request".encode("utf-8"), hashlib.sha256).digest()
        signature = hmac.new(k_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        authorization = f"HMAC-SHA256 Credential={ak}/{credential_scope}, SignedHeaders={signed_headers}, Signature={signature}"
        return authorization

    def _convert_pascal_to_snake(self, data: Any) -> Any:
        """递归转换 PascalCase 为 snake_case（正确处理连续大写字母）"""
        if not isinstance(data, dict):
            if isinstance(data, list):
                return [self._convert_pascal_to_snake(item) for item in data]
            return data
        converted = {}
        for key, value in data.items():
            # 处理连续大写字母: DBEngineVersion -> db_engine_version
            snake_key = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", key)
            snake_key = re.sub(r"([a-z])([A-Z])", r"\1_\2", snake_key)
            snake_key = snake_key.lower()
            converted[snake_key] = self._convert_pascal_to_snake(value)
        return converted

    def _call_api(self, action: str, body_args: Dict[str, Any]) -> Dict[str, Any]:
        service = "dbw"
        method = "POST"
        uri = "/"
        query_params = f"Action={action}&Version=2018-01-01"
        host = f"{service}.{self.region}.volcengineapi.com"
        url = f"https://{host}{uri}?{query_params}"

        # 这里的逻辑有问题，如果 body_args 的 key 已经是 PascalCase，_pascal_case 会把它弄乱
        # 例如 InstanceType -> Instancetype
        # 我们需要判断是否已经是 PascalCase
        
        body_dict = {}
        for k, v in body_args.items():
            if v is None:
                continue
            # 简单的 heuristic: 如果首字母大写且没有下划线，假设已经是 PascalCase，不处理
            if k[0].isupper() and "_" not in k:
                body_dict[k] = v
            else:
                body_dict[self._pascal_case(k)] = v
                
        body = json.dumps(body_dict)

        now = datetime.datetime.utcnow()
        x_date = now.strftime("%Y%m%dT%H%M%SZ")

        headers = {
            "Host": host,
            "Content-Type": "application/json",
            "X-Date": x_date,
        }

        if not self.ak:
            raise ValueError("Access Key (AK) is missing. Please check your .env file.")

        authorization = self._sign_request(
            self.ak, self.sk, self.region, service, method, uri, query_params, headers, body
        )
        headers["Authorization"] = authorization

        # Debug output (commented out by default)
        # print(f"DEBUG: Request URL: {url}")
        # print(f"DEBUG: Request Body: {body}")

        req = urllib.request.Request(url, data=body.encode("utf-8"), headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode("utf-8"))

        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise ValueError(f"HTTP {e.code}: {error_body}")

        if "ResponseMetadata" in result:
            meta = result["ResponseMetadata"]
            request_id = meta.get("RequestId", "Unknown")
            if meta.get("Error"):
                raise ValueError(f"API Error: {meta['Error']} (RequestId: {request_id})")

        if "Result" in result:
            res = result["Result"]
            if isinstance(res, dict):
                if "Results" in res:
                    return res
                return self._convert_pascal_to_snake(res)
            return res
        elif "ResponseMetadata" in result:
            meta = result["ResponseMetadata"]
            if meta.get("Error"):
                raise ValueError(f"API Error: {meta['Error']}")
        
        return result

    def _pascal_case(self, s: str) -> str:
        components = s.split("_")
        return "".join(x.title() for x in components)

    def nl2sql(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("GenerateSQLFromNL", args)

    def execute_sql(self, args: Dict[str, Any]) -> Dict[str, Any]:
        result = self._call_api("ExecuteSQL", args)
        if isinstance(result, dict):
            if "Results" in result or "results" in result:
                return result
        return result

    def list_databases(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("ListDatabases", args)

    def list_tables(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("ListTables", args)

    def get_table_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("GetTableInfo", args)

    def create_dml_sql_change_ticket(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("CreateDmlSqlChangeTicket", args)

    def create_ddl_sql_change_ticket(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("CreateDdlSqlChangeTicket", args)

    def describe_tickets(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTickets", args)

    def describe_ticket_detail(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTicketDetail", args)

    def describe_workflow(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeWorkflow", args)

    def describe_slow_logs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeSlowLogs", args)

    def describe_aggregate_slow_logs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeAggregateSlowLogs", args)

    def describe_slow_log_time_series_stats(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeSlowLogTimeSeriesStats", args)

    def describe_full_sql_detail(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeFullSQLDetail", args)

    def describe_instances(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeInstances", args)

    def get_metric_data(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("GetMetricData", args)

    def get_metric_items(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("GetMetricItems", args)

    def describe_table_metric(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTableMetric", args)

    def get_metric_data_predict(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("GetMetricDataPredict", args)

    def describe_session(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeSession", args)

    def kill_process(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("KillProcess", args)

    def describe_deadlock(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeDeadlock", args)

    def analyze_trx_and_lock(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("AnalyzeTrxAndLock", args)

    def describe_trx_and_locks(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTrxAndLocks", args)

    def create_trx_export_task(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("CreateTrxExportTask", args)

    def describe_trx_snapshots(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTrxSnapshots", args)

    def describe_err_logs(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeErrLogs", args)

    def describe_space_top(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeSpaceTop", args)

    def describe_table_space(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTableSpace", args)

    def describe_table_spaces(self, args: Dict[str, Any]) -> Dict[str, Any]:
        return self._call_api("DescribeTableSpaces", args)
