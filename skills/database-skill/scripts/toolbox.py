"""
Database Toolbox - Python 工具封装

此模块提供 DatabaseToolbox 类，用于与火山引擎 Database Toolbox API 交互。
专为 AI Agent 设计，返回结构统一、易于理解和处理。

核心设计原则：
1. 所有方法返回统一的字典格式
2. 包含 success、message、data 字段
3. data 字段包含具体业务数据
4. AI Agent 可根据 success 字段判断是否成功
"""

import argparse
import json
import os
from typing import Any, Optional, List

from scripts.dbw_client import DBWClient


class DatabaseToolbox:
    """
    Database Toolbox 封装类

    提供对数据库的查询、分析、变更等操作。
    初始化时可传入配置参数，也可从环境变量读取：
        VOLCENGINE_REGION, VOLCENGINE_ACCESS_KEY, VOLCENGINE_SECRET_KEY,
        VOLCENGINE_INSTANCE_ID, VOLCENGINE_INSTANCE_TYPE, VOLCENGINE_DATABASE

    返回值统一格式:
        {
            "success": true/false,      # 操作是否成功
            "message": "描述信息",       # 成功或失败的描述
            "data": {...}               # 业务数据（成功时）
            "error": {...}              # 错误信息（失败时）
        }
    """

    def __init__(
        self,
        region: Optional[str] = None,
        ak: Optional[str] = None,
        sk: Optional[str] = None,
        host: Optional[str] = None,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        database: Optional[str] = None,
    ) -> None:
        self.client = DBWClient(
            region=region or os.getenv("VOLCENGINE_REGION"),
            ak=ak or os.getenv("VOLCENGINE_ACCESS_KEY"),
            sk=sk or os.getenv("VOLCENGINE_SECRET_KEY"),
            host=host or os.getenv("VOLCENGINE_ENDPOINT"),
            instance_id=instance_id or os.getenv("VOLCENGINE_INSTANCE_ID"),
            instance_type=instance_type or os.getenv("VOLCENGINE_INSTANCE_TYPE"),
            database=database or os.getenv("VOLCENGINE_DATABASE"),
        )

    def _required(self, value: Optional[str], fallback: Optional[str], message: str) -> str:
        resolved = value if value not in (None, "") else fallback
        if not resolved:
            raise ValueError(message)
        return resolved

    def _ok(self, data: Any = None, message: str = "成功") -> dict[str, Any]:
        """构建成功返回"""
        result = {"success": True, "message": message}
        if data is not None:
            result["data"] = data
        return result

    def _error(self, message: str, error_detail: Any = None) -> dict[str, Any]:
        """构建错误返回"""
        result = {"success": False, "message": message}
        if error_detail:
            result["error"] = error_detail
        return result

    def _to_result(self, data: Any, message: str = "操作成功") -> dict[str, Any]:
        """将原始数据转换为统一格式"""
        if data is None:
            return self._error("返回数据为空")
        if isinstance(data, dict):
            # 检查是否有错误
            if "error" in data or "Error" in data:
                error_info = data.get("error") or data.get("Error")
                return self._error(f"API错误: {error_info}", data)
            return self._ok(data, message)
        return self._ok(data, message)

    def _ticket_url(self, ticket_id: str, instance_type: str) -> str:
        region = getattr(self.client, "region", None) or "cn-beijing"
        return f"https://console.volcengine.com/dbw/region:dbw+{region}/ticket/detail?ticketId={ticket_id}&dsType={instance_type}"

    def nl2sql(
        self,
        query: str,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        database: Optional[str] = None,
        tables: Optional[List[str]] = None,
    ) -> dict[str, Any]:
        """
        自然语言转 SQL

        Args:
            query: 自然语言查询，例如 "查询最近一周的销售额"
            instance_id: 数据库实例ID
            instance_type: 实例类型 (MySQL/VeDBMySQL/Postgres)
            database: 数据库名称
            tables: 涉及的表名列表

        Returns:
            {
                "success": true,
                "message": "成功",
                "data": {
                    "query": "原始问题",
                    "sql": "生成的SQL",
                    "sql_type": "SELECT|INSERT|UPDATE|DELETE"
                }
            }

        AI Agent 使用指南:
            - 此方法生成 SQL 但不执行，需要确认后再执行
            - sql_type 为 SELECT 可直接执行
            - sql_type 为 INSERT/UPDATE/DELETE 建议创建工单
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            database = self._required(database, self.client.database, "database is required")
            if not query:
                return self._error("query 参数不能为空")

            req = {
                "instance_id": instance_id,
                "instance_type": instance_type,
                "database": database,
                "query": query,
            }
            if tables:
                req["tables"] = tables

            result = self.client.nl2sql(req)
            return self._to_result(result, "SQL生成成功")
        except Exception as e:
            return self._error(f"nl2sql失败: {str(e)}")

    def execute_sql(
        self,
        commands: str,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        database: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        执行 SQL 查询

        Args:
            commands: SQL 语句，一次只能执行一条
            instance_id: 数据库实例ID
            instance_type: 实例类型
            database: 数据库名称

        Returns:
            成功时:
            {
                "success": true,
                "message": "查询成功",
                "data": {
                    "command_str": "SQL语句",
                    "state": "success|failed",
                    "row_count": 10,
                    "columns": ["id", "name"],
                    "rows": [{"id": 1, "name": "张三"}],
                    "execution_time_ms": 50
                }
            }
            失败时:
            {
                "success": false,
                "message": "SQL执行失败",
                "error": {
                    "state": "failed",
                    "reason_detail": "错误原因"
                }
            }

        AI Agent 使用指南:
            - SELECT: columns 和 rows 有数据，row_count 为返回行数
            - INSERT/UPDATE/DELETE: row_count 为影响行数，rows 为空
            - state=failed 时检查 error.reason_detail
            - 被安全拦截时需创建工单
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            database = self._required(database, self.client.database, "database is required")
            if not commands:
                return self._error("commands 参数不能为空")

            req = {
                "instance_id": instance_id,
                "instance_type": instance_type,
                "database": database,
                "commands": commands,
                "time_out_seconds": 60,
            }

            result = self.client.execute_sql(req)
            
            # 统一处理返回值
            if isinstance(result, dict):
                # 适配 Result 直接返回的情况（非 snake_case 转换）
                if "Results" in result and isinstance(result["Results"], list) and len(result["Results"]) > 0:
                    first_result = result["Results"][0]
                    state = first_result.get("State", "")
                    if state == "Success":
                        return self._ok({
                            "command_str": first_result.get("CommandStr", commands),
                            "state": state,
                            "row_count": first_result.get("RowCount", 0),
                            "columns": first_result.get("ColumnNames", []),
                            "rows": first_result.get("Rows", []),
                        }, "查询成功")
                    else:
                        return self._error(
                            first_result.get("ReasonDetail", "SQL执行失败"),
                            {"state": state, "reason_detail": first_result.get("ReasonDetail")}
                        )

                # 兼容 snake_case 转换后的情况
                if "results" in result and isinstance(result["results"], list) and len(result["results"]) > 0:
                    first_result = result["results"][0]
                    state = first_result.get("state", "")
                    if state == "Success":
                        return self._ok({
                            "command_str": first_result.get("command_str", commands),
                            "state": state,
                            "row_count": first_result.get("row_count", 0),
                            "columns": first_result.get("column_names", []),
                            "rows": first_result.get("rows", []),
                        }, "查询成功")
                    else:
                        return self._error(
                            first_result.get("reason_detail", "SQL执行失败"),
                            {"state": state, "reason_detail": first_result.get("reason_detail")}
                        )

                # 兼容旧逻辑
                state = result.get("state", "")
                if state == "success":
                    return self._ok({
                        "command_str": result.get("command_str", commands),
                        "state": state,
                        "row_count": result.get("row_count", 0),
                        "columns": result.get("column_names", []),
                        "rows": result.get("rows", []),
                    }, "查询成功")
                else:
                    return self._error(
                        result.get("reason_detail", "SQL执行失败"),
                        {"state": state, "reason_detail": result.get("reason_detail")}
                    )
            return self._to_result(result, "执行完成")
        except Exception as e:
            return self._error(f"execute_sql失败: {str(e)}")

    def query_sql(
        self,
        sql: str,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        database: Optional[str] = None,
    ) -> "pd.DataFrame":
        """
        执行查询并返回 Pandas DataFrame（仅支持 SELECT 查询）

        Args:
            sql: SQL 语句（仅支持 SELECT）

        Returns:
            pandas.DataFrame

        Raises:
            ValueError: 非 SELECT 语句或查询失败
        """
        sql = sql.strip()
        if not sql.upper().startswith("SELECT") and not sql.upper().startswith("SHOW"):
            raise ValueError("query_sql() 仅支持 SELECT/SHOW 查询，请使用 execute_sql() 执行 INSERT/UPDATE/DELETE")
        result = self.execute_sql(
            commands=sql,
            instance_id=instance_id,
            instance_type=instance_type,
            database=database,
        )

        if not result.get("success"):
            # 返回空 DataFrame 并附带错误信息（如果有必要，或者直接抛出异常）
            print(f"Query failed: {result.get('message')}")
            try:
                import pandas as pd
                return pd.DataFrame()
            except ImportError:
                 return result

        try:
            import pandas as pd
        except ImportError:
            # 如果没有 pandas，直接返回字典结果
            return result.get("data", {})

        data = result.get("data", {})
        columns = data.get("columns", [])
        rows_data = data.get("rows", [])
        
        # 提取 Cells 数据
        # 假设 rows_data 是 [{'Cells': ['val1', 'val2']}, ...]
        cleaned_rows = []
        for row in rows_data:
            if isinstance(row, dict) and "Cells" in row:
                cleaned_rows.append(row["Cells"])
            elif isinstance(row, dict) and "cells" in row:
                cleaned_rows.append(row["cells"])
            else:
                cleaned_rows.append(row)

        return pd.DataFrame(cleaned_rows, columns=columns)

    def list_databases(
        self,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        page_number: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ) -> dict[str, Any]:
        """
        列出数据库

        Returns:
            {
                "success": true,
                "data": {
                    "total": 10,
                    "page": 1,
                    "databases": [
                        {
                            "name": "company",
                            "charset": "utf8mb4",
                            "collation": "utf8mb4_unicode_ci",
                            "is_system": false,
                            "description": "主数据库"
                        }
                    ]
                }
            }
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")

            req = {
                "instance_id": instance_id,
                "instance_type": instance_type,
                "page_number": page_number or 1,
                "page_size": page_size or 10,
            }

            result = self.client.list_databases(req)
            
            if isinstance(result, dict):
                items = result.get("items", [])
                databases = []
                for item in items:
                    databases.append({
                        "name": item.get("name", ""),
                        "charset": item.get("character_set_name", ""),
                        "collation": item.get("collation_name", ""),
                        "is_system": item.get("is_system_db", False),
                        "description": item.get("description", ""),
                    })
                return self._ok({
                    "total": result.get("total", 0),
                    "page": page_number or 1,
                    "databases": databases,
                }, f"共 {len(databases)} 个数据库")
            
            return self._to_result(result)
        except Exception as e:
            return self._error(f"list_databases失败: {str(e)}")

    def list_tables(
        self,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        page_number: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ) -> dict[str, Any]:
        """
        列出数据库中的表

        Args:
            schema: 数据库模式 (PostgreSQL 需要指定，如 public)

        Returns:
            {
                "success": true,
                "data": {
                    "total": 50,
                    "page": 1,
                    "tables": ["users", "orders", "products"]
                }
            }
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            database = self._required(database, self.client.database, "database is required")

            req = {
                "instance_id": instance_id,
                "instance_type": instance_type,
                "database": database,
                "page_number": page_number or 1,
                "page_size": page_size or 10,
            }
            
            if schema:
                req["schema"] = schema

            result = self.client.list_tables(req)
            
            if isinstance(result, dict):
                return self._ok({
                    "total": result.get("total", 0),
                    "page": page_number or 1,
                    "database": database,
                    "schema": schema,
                    "tables": result.get("items", []),
                }, f"共 {len(result.get('items', []))} 张表")
            
            return self._to_result(result)
        except Exception as e:
            return self._error(f"list_tables失败: {str(e)}")

    def get_table_info(
        self,
        table: str,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        获取表结构

        Args:
            schema: 数据库模式 (PostgreSQL 需要指定，如 public)

        Returns:
            {
                "success": true,
                "data": {
                    "name": "users",
                    "engine": "InnoDB",
                    "charset": "utf8mb4",
                    "columns": [
                        {
                            "name": "id",
                            "type": "bigint",
                            "nullable": false,
                            "primary_key": true,
                            "auto_increment": true,
                            "comment": "用户ID"
                        }
                    ]
                }
            }
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            database = self._required(database, self.client.database, "database is required")
            if not table:
                return self._error("table 参数不能为空")

            req = {
                "instance_id": instance_id,
                "instance_type": instance_type,
                "database": database,
                "table": table,
            }
            
            if schema:
                req["schema"] = schema

            result = self.client.get_table_info(req)
            
            if isinstance(result, dict):
                columns = result.get("columns", [])
                normalized_columns = []
                for col in columns:
                    normalized_columns.append({
                        "name": col.get("name", ""),
                        "type": col.get("type", ""),
                        "length": col.get("length", ""),
                        "nullable": col.get("allow_be_null", True),
                        "primary_key": col.get("is_primary_key", False),
                        "auto_increment": col.get("is_auto_increment", False),
                        "default": col.get("default_value"),
                        "comment": col.get("comment", ""),
                    })
                return self._ok({
                    "name": result.get("name", table),
                    "engine": result.get("engine", ""),
                    "charset": result.get("character_set", ""),
                    "definition": result.get("definition", ""),
                    "columns": normalized_columns,
                }, f"表 {table} 结构获取成功")
            
            return self._to_result(result)
        except Exception as e:
            return self._error(f"get_table_info失败: {str(e)}")

    def create_dml_sql_change_ticket(
        self,
        sql_text: str,
        ticket_execute_type: str = "Auto",
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        database: Optional[str] = None,
        exec_start_time: Optional[int] = None,
        exec_end_time: Optional[int] = None,
        title: Optional[str] = None,
        memo: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        创建 DML 工单（数据变更）

        Returns:
            成功时:
            {
                "success": true,
                "message": "工单创建成功，等待审批",
                "data": {
                    "ticket_id": "dml-xxx",
                    "status": "TicketExamine",  # TicketPreCheck/TicketExamine/TicketFinished
                    "status_text": "审批中",
                    "approver": {"name": "审批人A", "id": "user-001"},
                    "ticket_url": "https://...",
                    "sql": "INSERT...",
                    "database": "company"
                }
            }
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            database = self._required(database, self.client.database, "database is required")
            if not sql_text:
                return self._error("sql_text 参数不能为空")

            req = {
                "instance_id": instance_id,
                "instance_type": instance_type,
                "database_name": database,
                "sql_text": sql_text,
                "ticket_execute_type": ticket_execute_type or "Auto",
            }
            if exec_start_time:
                req["exec_start_time"] = exec_start_time
            if exec_end_time:
                req["exec_end_time"] = exec_end_time
            if title:
                req["title"] = title
            if memo:
                req["memo"] = memo

            result = self.client.create_dml_sql_change_ticket(req)
            
            if isinstance(result, dict):
                ticket_id = result.get("ticket_id", "")
                status = result.get("ticket_status", "")
                status_text = self._status_text(status)
                current_user = result.get("current_user", {})
                
                return self._ok({
                    "ticket_id": ticket_id,
                    "status": status,
                    "status_text": status_text,
                    "approver": current_user,
                    "ticket_url": self._ticket_url(ticket_id, instance_type),
                    "sql": sql_text,
                    "database": database,
                }, f"工单 {ticket_id} 创建成功，状态: {status_text}")
            
            return self._to_result(result, "工单创建成功")
        except Exception as e:
            return self._error(f"create_dml_sql_change_ticket失败: {str(e)}")

    def create_ddl_sql_change_ticket(
        self,
        sql_text: str,
        ticket_execute_type: str = "Auto",
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        database: Optional[str] = None,
        exec_start_time: Optional[int] = None,
        exec_end_time: Optional[int] = None,
        title: Optional[str] = None,
        memo: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        创建 DDL 工单（结构变更）

        Returns: 同 create_dml_sql_change_ticket
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            database = self._required(database, self.client.database, "database is required")
            if not sql_text:
                return self._error("sql_text 参数不能为空")

            req = {
                "instance_id": instance_id,
                "instance_type": instance_type,
                "database_name": database,
                "sql_text": sql_text,
                "ticket_execute_type": ticket_execute_type or "Auto",
            }
            if exec_start_time:
                req["exec_start_time"] = exec_start_time
            if exec_end_time:
                req["exec_end_time"] = exec_end_time
            if title:
                req["title"] = title
            if memo:
                req["memo"] = memo

            result = self.client.create_ddl_sql_change_ticket(req)
            
            if isinstance(result, dict):
                ticket_id = result.get("ticket_id", "")
                status = result.get("ticket_status", "")
                status_text = self._status_text(status)
                current_user = result.get("current_user", {})
                
                return self._ok({
                    "ticket_id": ticket_id,
                    "status": status,
                    "status_text": status_text,
                    "approver": current_user,
                    "ticket_url": self._ticket_url(ticket_id, instance_type),
                    "sql": sql_text,
                    "database": database,
                }, f"DDL工单 {ticket_id} 创建成功，状态: {status_text}")
            
            return self._to_result(result, "工单创建成功")
        except Exception as e:
            return self._error(f"create_ddl_sql_change_ticket失败: {str(e)}")

    def _status_text(self, status: str) -> str:
        """工单状态码转中文"""
        status_map = {
            "TicketUndo": "未开始",
            "TicketPreCheck": "预检查中",
            "TicketPreCheckError": "预检查失败",
            "TicketExamine": "审批中",
            "TicketCancel": "已取消",
            "TicketReject": "已拒绝",
            "TicketWaitExecute": "等待执行",
            "TicketExecute": "执行中",
            "TicketFinished": "已完成",
            "TicketError": "执行失败",
        }
        return status_map.get(status, status)

    def describe_tickets(
        self,
        list_type: str,
        order_by: Optional[str] = None,
        sort_by: Optional[str] = "ASC",
        page_number: Optional[int] = 1,
        page_size: Optional[int] = 10,
    ) -> dict[str, Any]:
        """
        查询工单列表

        Args:
            list_type: All | CreatedByMe | ApprovedByMe

        Returns:
            {
                "success": true,
                "data": {
                    "total": 10,
                    "tickets": [
                        {
                            "id": "dml-xxx",
                            "title": "工单标题",
                            "status": "TicketFinished",
                            "status_text": "已完成",
                            "type": "DML|DDL",
                            "url": "https://..."
                        }
                    ]
                }
            }
        """
        try:
            if not list_type:
                return self._error("list_type 参数不能为空")

            req = {
                "list_type": list_type,
                "sort_by": sort_by or "ASC",
                "page_number": page_number or 1,
                "page_size": page_size or 10,
            }
            if order_by:
                req["order_by"] = order_by

            result = self.client.describe_tickets(req)
            
            if isinstance(result, dict):
                tickets = result.get("tickets", [])
                normalized_tickets = []
                for t in tickets:
                    ticket_id = t.get("ticket_id", "")
                    status = t.get("ticket_status", "")
                    normalized_tickets.append({
                        "id": ticket_id,
                        "title": t.get("title", ""),
                        "status": status,
                        "status_text": self._status_text(status),
                        "type": "DML" if "dml" in ticket_id.lower() else "DDL",
                        "create_time": t.get("create_time", ""),
                        "creator": t.get("create_user", {}),
                        "approver": t.get("current_user", {}),
                        "url": self._ticket_url(ticket_id, t.get("instance_type", "")),
                    })
                return self._ok({
                    "total": result.get("total", 0),
                    "tickets": normalized_tickets,
                }, f"共 {len(normalized_tickets)} 个工单")
            
            return self._to_result(result)
        except Exception as e:
            return self._error(f"describe_tickets失败: {str(e)}")

    def describe_ticket_detail(self, ticket_id: str) -> dict[str, Any]:
        """
        查询工单详情

        Returns:
            {
                "success": true,
                "data": {
                    "id": "dml-xxx",
                    "title": "标题",
                    "status": "TicketFinished",
                    "status_text": "已完成",
                    "sql": "执行的SQL",
                    "result": "执行结果或错误信息",
                    "create_time": "创建时间",
                    "update_time": "更新时间",
                    "creator": {...},
                    "approver": {...},
                    "url": "https://..."
                }
            }
        """
        try:
            if not ticket_id:
                return self._error("ticket_id 参数不能为空")

            result = self.client.describe_ticket_detail({"ticket_id": ticket_id})
            
            if isinstance(result, dict):
                status = result.get("ticket_status", "")
                return self._ok({
                    "id": ticket_id,
                    "title": result.get("title", ""),
                    "memo": result.get("memo", ""),
                    "status": status,
                    "status_text": self._status_text(status),
                    "sql": result.get("sql_text", ""),
                    "result": result.get("description", ""),
                    "create_time": result.get("create_time", ""),
                    "update_time": result.get("update_time", ""),
                    "creator": result.get("create_user", {}),
                    "approver": result.get("current_user", {}),
                    "url": self._ticket_url(ticket_id, result.get("instance_type", "")),
                }, f"工单 {ticket_id} 详情获取成功")
            
            return self._to_result(result)
        except Exception as e:
            return self._error(f"describe_ticket_detail失败: {str(e)}")

    def describe_workflow(self, ticket_id: str) -> dict[str, Any]:
        """
        查询审批流程

        Returns:
            {
                "success": true,
                "data": {
                    "ticket_id": "dml-xxx",
                    "nodes": [
                        {
                            "name": "部门审批",
                            "approver": "审批人A",
                            "status": "Pass",  # Pass/Reject/Undo/Approval
                            "status_text": "已通过"
                        }
                    ]
                }
            }
        """
        try:
            if not ticket_id:
                return self._error("ticket_id 参数不能为空")

            result = self.client.describe_workflow({"ticket_id": ticket_id})
            
            if isinstance(result, dict):
                flow_nodes = result.get("flow_nodes", [])
                nodes = []
                for node in flow_nodes:
                    status = node.get("status", "")
                    nodes.append({
                        "name": node.get("node_name", ""),
                        "approver": node.get("operator", ""),
                        "status": status,
                        "status_text": "已通过" if status == "Pass" else ("审批中" if status == "Approval" else ("已拒绝" if status == "Reject" else "未开始")),
                    })
                return self._ok({
                    "ticket_id": ticket_id,
                    "nodes": nodes,
                }, f"共 {len(nodes)} 个审批节点")
            
            return self._to_result(result)
        except Exception as e:
            return self._error(f"describe_workflow失败: {str(e)}")

    def describe_slow_logs(
        self,
        start_time: int,
        end_time: int,
        page_number: int = 1,
        page_size: int = 10,
        order_by: str = "QueryTime",
        sort_by: str = "DESC",
        node_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        查询慢查询日志

        Returns:
            {
                "success": true,
                "data": {
                    "total": 100,
                    "logs": [
                        {
                            "sql": "SELECT * FROM ...",
                            "query_time": 2.5,
                            "lock_time": 0.1,
                            "rows_scanned": 10000,
                            "rows_sent": 100,
                            "timestamp": 1704067200,
                            "user": "app_user",
                            "ip": "x.x.x.x"
                        }
                    ]
                }
            }
        """
        try:
            if not start_time or not end_time:
                return self._error("start_time 和 end_time 不能为空")

            args = {
                "start_time": start_time,
                "end_time": end_time,
                "page_number": page_number,
                "page_size": page_size,
                "order_by": order_by,
                "sort_by": sort_by,
            }
            if node_id:
                args["node_id"] = node_id

            result = self.client.describe_slow_logs(args)
            
            if isinstance(result, dict):
                slow_logs = result.get("slow_logs", [])
                logs = []
                for log in slow_logs:
                    logs.append({
                        "sql": log.get("sql_text", ""),
                        "template": log.get("sql_template", ""),
                        "query_time": log.get("query_time", 0),
                        "lock_time": log.get("lock_time", 0),
                        "rows_scanned": log.get("rows_examined", 0),
                        "rows_sent": log.get("rows_sent", 0),
                        "timestamp": log.get("timestamp", 0),
                        "user": log.get("user", ""),
                        "ip": log.get("source_ip", ""),
                        "database": log.get("db", ""),
                    })
                return self._ok({
                    "total": result.get("total", 0),
                    "logs": logs,
                }, f"共 {len(logs)} 条慢查询")
            
            return self._to_result(result)
        except Exception as e:
            return self._error(f"describe_slow_logs失败: {str(e)}")

    def describe_aggregate_slow_logs(
        self,
        start_time: int,
        end_time: int,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 10,
        order_by: str = "TotalQueryTime",
        sort_by: str = "DESC",
        search_param: Optional[dict] = None,
        node_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        查询慢查询聚合统计

        Returns:
            {
                "success": true,
                "data": {
                    "total": 100,
                    "logs": [
                        {
                            "sql_template": "SELECT * FROM orders WHERE...",
                            "db": "shop_db",
                            "user": "app_user",
                            "source_ip": "x.x.x.x",
                            "execute_count": 50,
                            "execute_count_ratio": 0.25,
                            "query_time_ratio": 0.8,
                            "query_time_stats": {
                                "total": 100.5,
                                "min": 0.5,
                                "max": 5.0,
                                "average": 2.01
                            },
                            "lock_time_stats": {...},
                            "rows_sent_stats": {...},
                            "rows_examined_stats": {...},
                            "first_appear_time": 1704067200,
                            "last_appear_time": 1704070800,
                            "sql_fingerprint": "SELECT * FROM orders WHERE order_id = ?"
                        }
                    ]
                }
            }
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")

            if not start_time or not end_time:
                return self._error("start_time 和 end_time 不能为空")

            args = {
                "instance_id": instance_id,
                "instance_type": instance_type,
                "start_time": start_time,
                "end_time": end_time,
                "page_number": page_number,
                "page_size": page_size,
                "order_by": order_by,
                "sort_by": sort_by,
            }
            if node_id:
                args["node_id"] = node_id
            if search_param:
                args["search_param"] = search_param

            result = self.client.describe_aggregate_slow_logs(args)

            if isinstance(result, dict):
                slow_logs = result.get("aggregate_slow_logs", [])
                logs = []
                for log in slow_logs:
                    logs.append({
                        "sql_template": log.get("sql_template", ""),
                        "db": log.get("db", ""),
                        "user": log.get("user", ""),
                        "source_ip": log.get("source_ip", ""),
                        "execute_count": log.get("execute_count", 0),
                        "execute_count_ratio": log.get("execute_count_ratio", 0),
                        "query_time_ratio": log.get("query_time_ratio", 0),
                        "lock_time_ratio": log.get("lock_time_ratio", 0),
                        "rows_sent_ratio": log.get("rows_sent_ratio", 0),
                        "rows_examined_ratio": log.get("rows_examined_ratio", 0),
                        "query_time_stats": log.get("query_time_stats", {}),
                        "lock_time_stats": log.get("lock_time_stats", {}),
                        "rows_sent_stats": log.get("rows_sent_stats", {}),
                        "rows_examined_stats": log.get("rows_examined_stats", {}),
                        "first_appear_time": log.get("first_appear_time", 0),
                        "last_appear_time": log.get("last_appear_time", 0),
                        "sql_fingerprint": log.get("sql_fingerprint", ""),
                        "sql_method": log.get("sql_method", ""),
                        "table": log.get("table", ""),
                    })
                return self._ok({
                    "total": result.get("total", 0),
                    "logs": logs,
                }, f"共 {len(logs)} 条聚合慢查询")

            return self._to_result(result)
        except Exception as e:
            return self._error(f"describe_aggregate_slow_logs失败: {str(e)}")

    def describe_slow_log_time_series_stats(
        self,
        start_time: int,
        end_time: int,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        interval: int = 300,
        search_param: Optional[dict] = None,
        node_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        查询慢查询时间序列趋势

        Args:
            instance_type: MySQL | Postgres | Mongo | Redis | VeDBMySQL 等

        Returns:
            {
                "success": true,
                "data": {
                    "slow_log_count_stats": [
                        {"timestamp": 1704067200, "count": 10},
                        {"timestamp": 1704067500, "count": 15}
                    ],
                    "cpu_usage_stats": [
                        {
                            "node_id": "node-1",
                            "role_type": "Master",
                            "cpu_list": [
                                {"timestamp": 1704067200, "value": 50.5, "unit": "%"}
                            ]
                        }
                    ],
                    "interval": 300
                }
            }
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")

            if not start_time or not end_time or not instance_type:
                return self._error("start_time, end_time, instance_type 不能为空")

            args = {
                "instance_id": instance_id,
                "instance_type": instance_type,
                "start_time": start_time,
                "end_time": end_time,
                "interval": interval,
            }
            if node_id:
                args["node_id"] = node_id
            if search_param:
                args["search_param"] = search_param

            result = self.client.describe_slow_log_time_series_stats(args)

            if isinstance(result, dict):
                return self._ok({
                    "slow_log_count_stats": result.get("slow_log_count_stats", []),
                    "cpu_usage_stats": result.get("cpu_usage_stats", []),
                    "interval": result.get("interval", interval),
                }, f"获取 {len(result.get('slow_log_count_stats', []))} 个时间点的慢查询统计")

            return self._to_result(result)
        except Exception as e:
            return self._error(f"describe_slow_log_time_series_stats失败: {str(e)}")

    def describe_full_sql_detail(
        self,
        start_time: int,
        end_time: int,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        page_size: int = 10,
        search_param: Optional[dict] = None,
        context: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        查询完整 SQL 历史详情

        Args:
            instance_type: MySQL | Postgres | Mongo | Redis | VeDBMySQL 等

        Returns:
            {
                "success": true,
                "data": {
                    "total": 1000,
                    "list_over": false,
                    "sql_list": [
                        {
                            "db_name": "shop_db",
                            "session_id": "12345",
                            "sql_type": "SELECT",
                            "query_string": "SELECT * FROM orders WHERE...",
                            "exec_plan": [...],
                            "start_timestamp": "1704067200000",
                            "end_timestamp": "1704067202000",
                            "exec_time": 2.0,
                            "cpu_time": 1.5,
                            "row_lock_wait_time": 0.1,
                            "rows_examined": 10000,
                            "rows_sent": 100,
                            "user_name": "app_user",
                            "client_ip": "x.x.x.x",
                            "sql_fingerprint": "SELECT * FROM orders WHERE order_id = ?",
                            "sql_table": "orders",
                            "node_id": "node-1"
                        }
                    ]
                }
            }
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")

            if not start_time or not end_time or not instance_type:
                return self._error("start_time, end_time, instance_type 不能为空")

            args = {
                "instance_id": instance_id,
                "instance_type": instance_type,
                "start_time": start_time,
                "end_time": end_time,
                "page_size": page_size,
            }
            if search_param:
                args["search_param"] = search_param
            if context:
                args["context"] = context

            result = self.client.describe_full_sql_detail(args)

            if isinstance(result, dict):
                sql_list = result.get("describe_full_sql_detail_rows", [])
                normalized = []
                for sql in sql_list:
                    normalized.append({
                        "db_name": sql.get("db_name", ""),
                        "session_id": sql.get("session_id", ""),
                        "sql_type": sql.get("sql_type", ""),
                        "query_string": sql.get("query_string", ""),
                        "exec_plan": sql.get("exec_plan", []),
                        "start_timestamp": sql.get("start_timestamp", ""),
                        "end_timestamp": sql.get("end_timestamp", ""),
                        "exec_time": sql.get("exec_time", 0),
                        "cpu_time": sql.get("cpu_time", 0),
                        "row_lock_wait_time": sql.get("rowlock_wait_time", 0),
                        "rows_examined": sql.get("rows_examined", 0),
                        "rows_sent": sql.get("rows_sent", 0),
                        "user_name": sql.get("user_name", ""),
                        "client_ip": sql.get("client_ip", ""),
                        "sql_fingerprint": sql.get("sql_fingerprint", ""),
                        "sql_table": sql.get("sql_table", ""),
                        "node_id": sql.get("node_id", ""),
                        "sql_template": sql.get("sql_template", ""),
                    })
                return self._ok({
                    "total": result.get("total", 0),
                    "list_over": result.get("list_over", False),
                    "context": result.get("context", ""),
                    "sql_list": normalized,
                }, f"共 {len(normalized)} 条 SQL 详情")

            return self._to_result(result)
        except Exception as e:
            return self._error(f"describe_full_sql_detail失败: {str(e)}")

    def list_instances(
        self,
        ds_type: Optional[str] = None,
        region_id: Optional[str] = None,
        instance_name: Optional[str] = None,
        instance_id: Optional[str] = None,
        instance_status: Optional[str] = None,
        query: Optional[str] = None,
        project_name: str = "default",
        dbw_status: str = "Normal",
        instances_version: str = "v2",
        page_number: int = 1,
        page_size: int = 10,
        order_by: str = "CreateTime",
        sort_by: str = "DESC",
    ) -> dict[str, Any]:
        """
        查询数据源列表（数据库实例）

        Args:
            ds_type: 数据库类型 (MySQL/Postgres/Mongo/Redis/VeDBMySQL/MSSQL...)
            region_id: 区域 ID
            instance_name: 实例名称
            instance_id: 实例 ID
            instance_status: 实例状态
            query: 查询关键字
            project_name: 项目名称
            dbw_status: DBW 状态 (Normal/SyncError/All)
            instances_version: 实例版本 (v1/v2)
            page_number: 页码
            page_size: 每页数量
            order_by: 排序字段
            sort_by: 排序方式

        Returns:
            {
                "success": true,
                "data": {
                    "total": 10,
                    "instances": [...]
                }
            }
        """
        try:
            args = {
                "PageNumber": page_number,
                "PageSize": page_size,
                "OrderBy": order_by,
                "SortBy": sort_by,
            }
            if ds_type:
                args["DSType"] = ds_type
            if region_id:
                args["RegionId"] = region_id
            if instance_name:
                args["InstanceName"] = instance_name
            if instance_id:
                args["InstanceId"] = instance_id
            if instance_status:
                args["InstanceStatus"] = instance_status
            if query:
                args["Query"] = query
            if project_name:
                args["ProjectName"] = project_name
            if dbw_status:
                args["DbwStatus"] = dbw_status
            if instances_version:
                args["InstancesVersion"] = instances_version

            result = self.client.describe_instances(args)

            if isinstance(result, dict):
                instances = result.get("instances", [])
                normalized = []
                for inst in instances:
                    spec = inst.get("instance_spec", {})
                    normalized.append({
                        "id": inst.get("instance_id", ""),
                        "name": inst.get("instance_name", ""),
                        "status": inst.get("instance_status", ""),
                        "type": inst.get("instance_type", ""),
                        "version": inst.get("db_engine_version", ""),
                        "region": inst.get("region_id", ""),
                        "zone": inst.get("zone", ""),
                        "endpoint": inst.get("internal_address", ""),
                        "port": 3306,
                        "charset": "utf8mb4",
                        "cpu": spec.get("cpu_num", 0),
                        "memory": spec.get("mem_in_gi_b", 0),
                        "storage": spec.get("storage", 0),
                        "create_time": inst.get("create_time", ""),
                    })
                return self._ok({
                    "total": result.get("total", 0),
                    "instances": normalized,
                }, f"共 {len(normalized)} 个实例")

            return self._to_result(result)
        except Exception as e:
            return self._error(f"describe_instances失败: {str(e)}")

    def get_metric_data(
        self,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        metric_name: str = "",
        period: int = 60,
        start_time: int = 0,
        end_time: int = 0,
        node_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        获取监控指标数据

        Args:
            metric_name: 监控指标名称
            period: 聚合周期(秒)
            start_time: 开始时间戳(秒)
            end_time: 结束时间戳(秒)
            node_id: 节点ID(可选)
        """
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            
            if not metric_name or not start_time or not end_time:
                return self._error("metric_name, start_time, end_time 不能为空")

            req = {
                "InstanceType": instance_type,
                "MetricName": metric_name,
                "Period": period,
                "StartTime": start_time,
                "EndTime": end_time,
                "Filters": [{"InstanceId": instance_id}]
            }
            if node_id:
                req["Filters"][0]["NodeId"] = node_id

            result = self.client.get_metric_data(req)
            return self._to_result(result, "获取监控数据成功")
        except Exception as e:
            return self._error(f"get_metric_data失败: {str(e)}")

    def get_metric_items(
        self,
        instance_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """获取可用的监控指标项"""
        try:
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            result = self.client.get_metric_items({"InstanceType": instance_type})
            return self._to_result(result, "获取监控指标项成功")
        except Exception as e:
            return self._error(f"get_metric_items失败: {str(e)}")

    def describe_table_metric(
        self,
        item_type: str,
        db_name: str,
        table: str,
        start_time: int,
        end_time: int,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """获取表级别监控指标"""
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            
            req = {
                "InstanceId": instance_id,
                "InstanceType": instance_type,
                "ItemType": item_type,
                "DbName": db_name,
                "Table": table,
                "StartTime": start_time,
                "EndTime": end_time,
            }
            result = self.client.describe_table_metric(req)
            return self._to_result(result, "获取表监控成功")
        except Exception as e:
            return self._error(f"describe_table_metric失败: {str(e)}")

    def get_metric_data_predict(
        self,
        metric_name: str,
        period: int,
        start_time: int,
        end_time: int,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """获取监控数据预测"""
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            
            req = {
                "InstanceID": instance_id,
                "InstanceType": instance_type,
                "MetricName": metric_name,
                "Period": period,
                "StartTime": start_time,
                "EndTime": end_time,
                "Filters": [{"InstanceId": instance_id}]
            }
            result = self.client.get_metric_data_predict(req)
            return self._to_result(result, "获取监控预测数据成功")
        except Exception as e:
            return self._error(f"get_metric_data_predict失败: {str(e)}")

    def describe_session(self, session_id: str) -> dict[str, Any]:
        """查询会话详情"""
        try:
            if not session_id:
                return self._error("session_id 不能为空")
            result = self.client.describe_session({"SessionId": session_id})
            return self._to_result(result, "查询会话成功")
        except Exception as e:
            return self._error(f"describe_session失败: {str(e)}")

    def kill_process(
        self,
        process_ids: List[str],
        node_id: str,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        shard_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """终止进程"""
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            
            process_info = {"ProcessIDs": process_ids, "NodeId": node_id}
            if shard_id:
                process_info["ShardId"] = shard_id

            req = {
                "InstanceId": instance_id,
                "DSType": instance_type,
                "ProcessInfo": [process_info]
            }
            result = self.client.kill_process(req)
            return self._to_result(result, "终止进程操作完成")
        except Exception as e:
            return self._error(f"kill_process失败: {str(e)}")

    def describe_deadlock(
        self,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        region_id: Optional[str] = None,
    ) -> dict[str, Any]:
        """查询死锁信息"""
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            
            req = {
                "InstanceId": instance_id,
                "DSType": instance_type,
            }
            if region_id:
                req["RegionId"] = region_id
                
            result = self.client.describe_deadlock(req)
            return self._to_result(result, "查询死锁信息成功")
        except Exception as e:
            return self._error(f"describe_deadlock失败: {str(e)}")

    def describe_trx_and_locks(
        self,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """查询事务和锁列表"""
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            
            req = {
                "InstanceId": instance_id,
                "DSType": instance_type,
                "PageNumber": page_number,
                "PageSize": page_size,
            }
            result = self.client.describe_trx_and_locks(req)
            return self._to_result(result, "查询事务和锁列表成功")
        except Exception as e:
            return self._error(f"describe_trx_and_locks失败: {str(e)}")

    def create_trx_export_task(
        self,
        start_time: int,
        end_time: int,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
    ) -> dict[str, Any]:
        """创建事务导出任务"""
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            
            req = {
                "InstanceId": instance_id,
                "InstanceType": instance_type,
                "StartTime": start_time,
                "EndTime": end_time,
            }
            result = self.client.create_trx_export_task(req)
            return self._to_result(result, "创建事务导出任务成功")
        except Exception as e:
            return self._error(f"create_trx_export_task失败: {str(e)}")

    def describe_trx_snapshots(
        self,
        start_time: int,
        end_time: int,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """查询事务快照"""
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            
            req = {
                "InstanceId": instance_id,
                "InstanceType": instance_type,
                "StartTime": start_time,
                "EndTime": end_time,
                "PageNumber": page_number,
                "PageSize": page_size,
            }
            result = self.client.describe_trx_snapshots(req)
            return self._to_result(result, "查询事务快照成功")
        except Exception as e:
            return self._error(f"describe_trx_snapshots失败: {str(e)}")

    def describe_err_logs(
        self,
        start_time: int,
        end_time: int,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
    ) -> dict[str, Any]:
        """查询错误日志"""
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            
            req = {
                "InstanceId": instance_id,
                "InstanceType": instance_type,
                "StartTime": start_time,
                "EndTime": end_time,
                "PageNumber": page_number,
                "PageSize": page_size,
            }
            if keyword:
                req["SearchParam"] = {"Keyword": keyword}
                
            result = self.client.describe_err_logs(req)
            return self._to_result(result, "查询错误日志成功")
        except Exception as e:
            return self._error(f"describe_err_logs失败: {str(e)}")

    def describe_table_space(
        self,
        instance_id: Optional[str] = None,
        instance_type: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 10,
        database: Optional[str] = None,
        table_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """查询表空间详情"""
        try:
            instance_id = self._required(instance_id, self.client.instance_id, "instance_id is required")
            instance_type = self._required(instance_type, self.client.instance_type, "instance_type is required")
            
            req = {
                "InstanceId": instance_id,
                "InstanceType": instance_type,
                "PageNumber": page_number,
                "PageSize": page_size,
            }
            if database:
                req["Database"] = database
            if table_name:
                req["TableName"] = table_name
                
            result = self.client.describe_table_space(req)
            return self._to_result(result, "查询表空间详情成功")
        except Exception as e:
            return self._error(f"describe_table_space失败: {str(e)}")

    def describe_table_spaces(
        self,
        session_id: str,
        page_number: int = 1,
        page_size: int = 10,
        query: Optional[str] = None,
    ) -> dict[str, Any]:
        """查询表空间列表"""
        try:
            if not session_id:
                return self._error("session_id 不能为空")
                
            req = {
                "SessionId": session_id,
                "PageNumber": page_number,
                "PageSize": page_size,
            }
            if query:
                req["Query"] = query
                
            result = self.client.describe_table_spaces(req)
            return self._to_result(result, "查询表空间列表成功")
        except Exception as e:
            return self._error(f"describe_table_spaces失败: {str(e)}")



def main() -> None:
    """命令行入口"""
    parser = argparse.ArgumentParser(description="Database Toolbox CLI")
    parser.add_argument("action", help="方法名")
    parser.add_argument("--data", default="{}", help="JSON参数")
    args = parser.parse_args()

    toolbox = DatabaseToolbox()
    if not hasattr(toolbox, args.action):
        print(json.dumps({"success": False, "message": f"不支持的方法: {args.action}"}))
        return

    try:
        payload = json.loads(args.data)
        result = getattr(toolbox, args.action)(**payload)
        
        # 处理 pandas DataFrame
        if hasattr(result, "to_json"):
             print(result.to_json(orient="records", force_ascii=False))
        else:
             print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"success": False, "message": str(e)}))


if __name__ == "__main__":
    main()
