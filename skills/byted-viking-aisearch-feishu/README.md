# byted-viking-aisearch-feishu

基于飞书开放平台云文档搜索 API 的技能封装，用于在代理中搜索当前用户可见的飞书文档。

## 快速开始

1. 配置访问凭证（推荐用户访问令牌）：

```bash
export LARK_USER_ACCESS_TOKEN="u-xxxxxxxxxxxxxxxxxxxxxxxx"
```

2. 代码调用示例：

```python
from scripts import FeishuDocSearch

search = FeishuDocSearch()  # 或 FeishuDocSearch(access_token="u-xxx")
res = search.search_docs(
    search_key="项目",
    count=10,
    offset=0,
    docs_types=["doc", "docx"]
)
print(res)

# 读取首条结果原文/内容
items = res.get("data", {}).get("items", [])
if items:
    item = items[0]
    content = search.fetch_raw_content(item["docs_type"], item["docs_token"])
    print(content)
```

返回示例：

```json
{
  "success": true,
  "message": "搜索成功",
  "data": {
    "total": 59,
    "has_more": true,
    "items": [
      {"docs_token": "xxxx", "docs_type": "docx", "owner_id": "ou_xxx", "title": "项目进展周报"}
    ]
  }
}
```

## 权限与鉴权

- 通过 `Authorization: Bearer <user_access_token>` 访问
- 需要在应用控制台为开放接口开启「搜索云文档」等相关权限

## 获取 LARK_USER_ACCESS_TOKEN

- 准备：在开放平台为你的应用配置 OAuth 重定向（例如 `http://localhost:53623/callback`），并开通“搜索云文档”等权限
- 本地获取：

```bash
export LARK_APP_ID="cli_xxx"
export LARK_APP_SECRET="xxx"
python skills/byted-viking-aisearch-feishu/scripts/oauth_local.py --port 53623
# 打开输出的链接完成授权，终端将打印：
# LARK_USER_ACCESS_TOKEN=u-xxxxxxxxxxxxxxxx
```

将生成的 `LARK_USER_ACCESS_TOKEN` 写入环境变量后，运行 test.py 验证：

```bash
export LARK_USER_ACCESS_TOKEN="u-xxxxxxxxxxxxxxxx"
python skills/byted-viking-aisearch-feishu/test.py -q "项目" --count 1
```

## 接口参考

- Feishu: `POST /open-apis/suite/docs-api/search/object`
- Docx: `GET /open-apis/docx/v1/documents/:document_id/raw_content`
- Doc: `GET /open-apis/docs/v2/documents/:document_id/raw_content`
