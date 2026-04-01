import json
import os
import requests
from typing import Any, Dict, List, Optional


class FeishuDocSearch:
    """
    基于飞书开放平台的文档搜索和内容读取工具
    
    主要功能：
    - 文档搜索：search_docs() - 按关键词搜索飞书文档
    - 内容读取：fetch_raw_content() - 读取文档内容
    
    API: https://open.feishu.cn/open-apis/suite/docs-api/search/object (POST)
    认证: Authorization: Bearer <user_access_token>
    """

    def __init__(
        self,
        access_token: Optional[str] = None,
        endpoint: str = "https://open.feishu.cn/open-apis/suite/docs-api/search/object",
        timeout: int = 30,
    ) -> None:
        self.access_token = access_token or os.getenv("LARK_USER_ACCESS_TOKEN")
        self.endpoint = endpoint
        self.timeout = timeout

    def _ok(self, data: Any = None, message: str = "成功") -> Dict[str, Any]:
        res: Dict[str, Any] = {"success": True, "message": message}
        if data is not None:
            res["data"] = data
        return res

    def _error(self, message: str, detail: Any = None) -> Dict[str, Any]:
        res: Dict[str, Any] = {"success": False, "message": message}
        if detail is not None:
            res["error"] = detail
        return res

    def _headers(self) -> Dict[str, str]:
        if not self.access_token:
            raise ValueError("缺少访问凭证: 请设置 LARK_USER_ACCESS_TOKEN 或在初始化时传入 access_token")
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json; charset=utf-8",
        }

    def _request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = requests.post(self.endpoint, headers=self._headers(), json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            text = e.response.text if e.response is not None else ""
            raise RuntimeError(f"HTTP {status}: {text}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(str(e))

    def _post_json(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = requests.post(url, headers=self._headers(), json=payload, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "unknown"
            text = e.response.text if e.response is not None else ""
            raise RuntimeError(f"HTTP {status}: {text}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(str(e))

    def _get_json(self, url: str) -> Dict[str, Any]:
        if not self.access_token:
            raise ValueError("缺少访问凭证: 请设置 LARK_USER_ACCESS_TOKEN")
        headers = {"Authorization": f"Bearer {self.access_token}"}
        resp = requests.get(url, headers=headers, timeout=self.timeout)
        try:
            data = resp.json()
        except Exception:
            data = {"status": resp.status_code, "text": resp.text}
        if resp.status_code >= 400:
            return {"http_status": resp.status_code, "error": data}
        return data

    def _normalize_suite_docs_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        normalized = dict(item)
        normalized["source"] = "suite_docs"
        return normalized

    def _normalize_wiki_obj_type(self, obj_type: Any) -> str:
        mapping = {
            "1": "doc",
            "2": "sheet",
            "3": "mindnote",
            "5": "file",
            "8": "docx",
            "11": "slides",
        }
        key = str(obj_type)
        return mapping.get(key, str(obj_type or ""))

    def _normalize_wiki_node_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        obj_type = self._normalize_wiki_obj_type(item.get("obj_type"))
        node_token = item.get("node_id") or item.get("node_token")
        return {
            "docs_token": node_token,
            "docs_type": "wiki",
            "title": item.get("title"),
            "url": item.get("url"),
            "space_id": item.get("space_id"),
            "node_token": node_token,
            "obj_type": obj_type,
            "obj_token": item.get("obj_token"),
            "parent_id": item.get("parent_id"),
            "sort_id": item.get("sort_id"),
            "source": "wiki_nodes",
        }

    def _dedupe_keys(self, item: Dict[str, Any]) -> List[str]:
        keys = []
        docs_type = (item.get("docs_type") or "").lower()
        docs_token = item.get("docs_token")
        if docs_type and docs_token:
            keys.append(f"{docs_type}:{docs_token}")
        obj_type = (item.get("obj_type") or "").lower()
        obj_token = item.get("obj_token")
        if obj_type and obj_token:
            keys.append(f"{obj_type}:{obj_token}")
        return keys

    def _merge_search_items(
        self,
        wiki_items: List[Dict[str, Any]],
        suite_items: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        merged: List[Dict[str, Any]] = []
        seen = set()
        for item in wiki_items + suite_items:
            keys = self._dedupe_keys(item)
            if keys and any(key in seen for key in keys):
                continue
            merged.append(item)
            for key in keys:
                seen.add(key)
        return merged

    def _search_suite_docs(
        self,
        search_key: str,
        count: Optional[int] = None,
        offset: Optional[int] = None,
        owner_ids: Optional[List[str]] = None,
        chat_ids: Optional[List[str]] = None,
        docs_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {"search_key": search_key}
        if count is not None:
            body["count"] = count
        if offset is not None:
            body["offset"] = offset
        if owner_ids:
            body["owner_ids"] = owner_ids
        if chat_ids:
            body["chat_ids"] = chat_ids
        if docs_types:
            body["docs_types"] = docs_types
        raw = self._request(body)
        code = raw.get("code", -1)
        if code != 0:
            raise RuntimeError(json.dumps(raw, ensure_ascii=False))
        data = raw.get("data") or {}
        items = [self._normalize_suite_docs_item(item) for item in data.get("docs_entities") or []]
        return {
            "total": data.get("total", len(items)),
            "has_more": data.get("has_more", False),
            "items": items,
        }

    def search_wiki_nodes(
        self,
        keyword: str,
        count: Optional[int] = None,
        offset: Optional[int] = None,
        space_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        搜索 wiki 节点

        按 wiki 节点标题/内容在知识库中搜索文档。
        """
        if not keyword or not keyword.strip():
            return self._error("keyword 不能为空")
        body: Dict[str, Any] = {"query": keyword}
        if count is not None:
            body["count"] = count
        if offset is not None:
            body["offset"] = offset
        if space_id:
            body["space_id"] = space_id
        try:
            raw = self._post_json("https://open.feishu.cn/open-apis/wiki/v2/nodes/search", body)
            code = raw.get("code", -1)
            if code != 0:
                return self._error("飞书 wiki 搜索接口返回错误", raw)
            data = raw.get("data") or {}
            items = [self._normalize_wiki_node_item(item) for item in data.get("items") or []]
            normalized = {
                "total": data.get("total", len(items)),
                "has_more": data.get("has_more", False),
                "items": items,
            }
            return self._ok(normalized, "搜索成功")
        except Exception as e:
            msg = str(e)
            if "401" in msg or "Unauthorized" in msg:
                return self._error("认证失败，请检查 access_token 是否有效或已过期", {"type": "auth_error", "detail": msg})
            if "403" in msg or "Forbidden" in msg:
                return self._error("权限不足，请为应用开通 wiki 搜索相关权限", {"type": "permission_denied", "detail": msg})
            if "timeout" in msg.lower():
                return self._error("请求超时，请稍后重试", {"type": "timeout", "detail": msg})
            return self._error("wiki 搜索失败", {"type": "api_error", "detail": msg})

    def search_docs(
        self,
        search_key: str,
        count: Optional[int] = None,
        offset: Optional[int] = None,
        owner_ids: Optional[List[str]] = None,
        chat_ids: Optional[List[str]] = None,
        docs_types: Optional[List[str]] = ["doc", "docx", "wiki"],
    ) -> Dict[str, Any]:
        """
        文档搜索
        
        在飞书中按关键词搜索文档
        
        Args:
            search_key: 搜索关键词，必填
            count: 返回数量，范围 [0, 50]，默认不指定
            offset: 偏移量，需满足 offset + count < 200，默认不指定
            owner_ids: 所有者 Open ID 列表，用于按所有者筛选
            chat_ids: 文件所在群 ID 列表，用于按群筛选
            docs_types: 文档类型枚举，默认 ["doc", "docx", "wiki"]
                        可选值: doc, docx, wiki
        
        Returns:
            {
              "success": true,
              "message": "搜索成功",
              "data": {
                "total": 2,
                "has_more": false,
                "items": [
                  {
                    "docs_token": "...", 
                    "docs_type": "doc", 
                    "title": "xxx", 
                    "owner_id": "ou_..."
                  }
                ]
              }
            }
        
        错误返回示例:
            {
              "success": false,
              "message": "认证失败，请检查 access_token 是否有效或已过期",
              "error": {"type": "auth_error", "detail": "..."}
            }
        """
        if not search_key or not search_key.strip():
            return self._error("search_key 不能为空")
        requested_count = count if count is not None else 10
        requested_offset = offset if offset is not None else 0
        suite_fetch_count = min(50, max(requested_count + requested_offset, requested_count))
        try:
            requested_types = [doc_type.lower() for doc_type in (docs_types or ["doc", "docx", "wiki"])]
            include_wiki = "wiki" in requested_types or "iwiki" in requested_types
            suite_types = [doc_type for doc_type in requested_types if doc_type not in ("wiki", "iwiki")]
            if not suite_types and not include_wiki:
                suite_types = ["doc", "docx"]

            wiki_result = {"total": 0, "has_more": False, "items": []}
            wiki_error: Optional[Dict[str, Any]] = None
            if include_wiki:
                wiki_search_result = self.search_wiki_nodes(
                    keyword=search_key,
                    count=suite_fetch_count,
                    offset=0,
                )
                if not wiki_search_result.get("success"):
                    if not suite_types:
                        return wiki_search_result
                    wiki_error = {
                        "message": wiki_search_result.get("message"),
                        "error": wiki_search_result.get("error"),
                    }
                else:
                    wiki_result = wiki_search_result.get("data") or wiki_result

            suite_result = {"total": 0, "has_more": False, "items": []}
            if suite_types:
                suite_result = self._search_suite_docs(
                    search_key=search_key,
                    count=suite_fetch_count,
                    offset=0,
                    owner_ids=owner_ids,
                    chat_ids=chat_ids,
                    docs_types=suite_types,
                )

            merged_items = self._merge_search_items(
                wiki_items=wiki_result.get("items") or [],
                suite_items=suite_result.get("items") or [],
            )
            paged_items = merged_items[requested_offset:requested_offset + requested_count]
            normalized = {
                "total": len(merged_items),
                "has_more": (
                    (requested_offset + requested_count) < len(merged_items)
                    or suite_result.get("has_more", False)
                    or wiki_result.get("has_more", False)
                ),
                "items": paged_items,
                "source_totals": {
                    "suite_docs": suite_result.get("total", 0),
                    "wiki_nodes": wiki_result.get("total", 0),
                },
            }
            if wiki_error is not None:
                normalized["warnings"] = {"wiki_error": wiki_error}
            return self._ok(normalized, "搜索成功")
        except Exception as e:
            msg = str(e)
            if "401" in msg or "Unauthorized" in msg:
                return self._error("认证失败，请检查 access_token 是否有效或已过期", {"type": "auth_error", "detail": msg})
            if "403" in msg or "Forbidden" in msg:
                return self._error("权限不足，请为应用开通云文档搜索相关权限", {"type": "permission_denied", "detail": msg})
            if "timeout" in msg.lower():
                return self._error("请求超时，请稍后重试", {"type": "timeout", "detail": msg})
            return self._error("搜索失败", {"type": "api_error", "detail": msg})

    def get_docx_raw_content(self, document_id: str) -> Dict[str, Any]:
        """
        获取新版飞书文档（docx）的原始内容
        
        Args:
            document_id: 新版文档的 token，如 doxcnbU8xxx
        
        Returns:
            {
              "success": true,
              "message": "获取成功",
              "data": {"content": "文档内容..."}
            }
        """
        try:
            url = f"https://open.feishu.cn/open-apis/docx/v1/documents/{document_id}/raw_content"
            data = self._get_json(url)
            if "http_status" in data:
                return self._error("获取 docx 原文失败", data)
            code = data.get("code", -1)
            if code == 0:
                return self._ok({"content": data.get("data", {}).get("content", "")}, "获取成功")
            return self._error("获取 docx 原文失败", data)
        except Exception as e:
            return self._error("获取 docx 原文失败", {"detail": str(e)})

    def get_doc_raw_content(self, document_id: str) -> Dict[str, Any]:
        """
        获取旧版飞书文档（doc）的原始内容
        
        Args:
            document_id: 旧版文档的 token，如 doxcnbxxxxx
        
        Returns:
            {
              "success": true,
              "message": "获取成功",
              "data": {"content": "文档内容..."}
            }
        """
        try:
            url = f"https://open.feishu.cn/open-apis/docs/v2/documents/{document_id}/raw_content"
            data = self._get_json(url)
            if "http_status" in data:
                return self._error("获取 doc 原文失败", data)
            code = data.get("code", -1)
            if code == 0:
                return self._ok({"content": data.get("data", {}).get("content", "")}, "获取成功")
            return self._error("获取 doc 原文失败", data)
        except Exception as e:
            return self._error("获取 doc 原文失败", {"detail": str(e)})

    def get_wiki_node(self, node_token: str) -> Dict[str, Any]:
        """
        获取 wiki 节点信息
        
        Args:
            node_token: wiki 节点的 token，如 wikinbxxxxx
        
        Returns:
            {
              "success": true,
              "message": "获取成功",
              "data": {
                "node_token": "...",
                "title": "...",
                "obj_type": "docx",
                "obj_token": "..."
              }
            }
        """
        try:
            url = f"https://open.feishu.cn/open-apis/wiki/v2/spaces/get_node?token={node_token}"
            data = self._get_json(url)
            if "http_status" in data:
                return self._error("获取 wiki 节点失败", data)
            code = data.get("code", -1)
            if code == 0:
                node = data.get("data", {}).get("node", {})
                return self._ok({
                    "node_token": node.get("node_token"),
                    "title": node.get("title"),
                    "obj_type": node.get("obj_type"),
                    "obj_token": node.get("obj_token"),
                    "node_type": node.get("node_type"),
                    "space_id": node.get("space_id"),
                    "creator": node.get("creator"),
                    "owner": node.get("owner")
                }, "获取成功")
            return self._error("获取 wiki 节点失败", data)
        except Exception as e:
            return self._error("获取 wiki 节点失败", {"detail": str(e)})
    
    def get_wiki_content(self, node_token: str) -> Dict[str, Any]:
        """
        获取 wiki 文档内容
        
        如果 wiki 节点关联了 doc/docx 文档，则读取关联文档的内容
        否则返回 wiki 节点信息
        
        Args:
            node_token: wiki 节点的 token
        
        Returns:
            {
              "success": true,
              "message": "获取成功",
              "data": {"content": "..."}
            }
        """
        # 先获取 wiki 节点信息
        node_result = self.get_wiki_node(node_token)
        if not node_result.get("success"):
            return node_result
        
        node_data = node_result.get("data", {})
        obj_type = self._normalize_wiki_obj_type(node_data.get("obj_type"))
        obj_token = node_data.get("obj_token")
        
        # 如果关联了 doc 或 docx 文档，读取关联文档内容
        if obj_type in ("doc", "docx") and obj_token:
            return self.fetch_raw_content(docs_type=obj_type, docs_token=obj_token)
        
        # 否则返回 wiki 节点信息作为内容
        title = node_data.get("title", "")
        content = f"Wiki 节点: {title}\n\n节点信息:\n{json.dumps(node_data, ensure_ascii=False, indent=2)}"
        return self._ok({"content": content}, "获取 wiki 节点信息成功")
    
    def fetch_raw_content(self, docs_type: str, docs_token: str) -> Dict[str, Any]:
        """
        统一的文档内容读取接口，根据文档类型分发到具体方法
        
        支持的 docs_type:
        - doc/docx: 读取文档内容
        - wiki/iwiki: 读取 wiki 文档内容
        
        Args:
            docs_type: 文档类型，必填
            docs_token: 文档 token，必填
        
        Returns:
            {
              "success": true,
              "message": "获取成功",
              "data": {"content": "..."}
            }
        """
        t = (docs_type or "").lower()
        if t in ("docx", "doc"):
            if t == "docx":
                return self.get_docx_raw_content(docs_token)
            return self.get_doc_raw_content(docs_token)
        if t in ("wiki", "iwiki"):
            return self.get_wiki_content(docs_token)
        return self._error("不支持的 docs_type，仅支持 doc、docx、wiki 和 iwiki")