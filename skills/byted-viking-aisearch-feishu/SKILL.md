---
name: byted-viking-aisearch-feishu
description: |
  基于飞书开放平台 API 的文档搜索和内容读取工具。
  使用场景：在飞书中搜索文档、读取文档内容。
  Also activates for: 飞书搜索、Feishu search docs、Lark docs search、搜索飞书文档
metadata:
  openclaw:
    identity:
    - type: oauth
      provider: viking_feishu_oauth_provider
      env:
      - LARK_USER_ACCESS_TOKEN
      required: true
---

# Viking AISearch Feishu Skill

你是一个专注于飞书文档搜索和内容读取的智能助手。你的目标是基于用户授权，安全、准确地从飞书中检索文档并读取内容。

## 🎯 核心功能

本 Skill 提供以下核心能力：

- **文档搜索**：聚合搜索飞书文档与 wiki 节点
- **内容读取**：读取文档（doc/docx/wiki）的原始内容

## 🚦 场景路由

根据用户意图，匹配相应功能：

| 用户意图示例                      | 匹配场景       | 主要方法                  | 产出                       |
| :-------------------------- | :--------- | :-------------------- | :----------------------- |
| "在飞书里搜一下'项目计划'""找一下关于Q4的文档" | **文档搜索**   | `search_docs()` / `search_wiki_nodes()` | 返回文档列表（标题、类型、token、空间等） |
| "读取这个文档的内容""看看这份周报写了什么"     | **读取文档内容** | `fetch_raw_content()` | 返回 doc/docx 的纯文本内容       |

## 📚 主要接口使用方法

### 1. 初始化工具类

```python
from scripts.feishu_search import FeishuDocSearch

# 方式一：使用环境变量（推荐）
tool = FeishuDocSearch()

# 方式二：显式传入 access_token
tool = FeishuDocSearch(access_token="u-xxx")
```

***

### 2. 搜索文档 - `search_docs()`

**功能**：聚合飞书文档搜索与 wiki 节点搜索，统一返回可直接读取的文档列表

**参数说明**：

| 参数名          | 类型          | 必填 | 默认值              | 说明                           |
| :----------- | :---------- | :- | :--------------- | :--------------------------- |
| `search_key` | `str`       | 是  | -                | 搜索关键词                        |
| `count`      | `int`       | 否  | `None`           | 返回数量，范围 \[0, 50]             |
| `offset`     | `int`       | 否  | `None`           | 偏移量，需满足 offset + count < 200 |
| `owner_ids`  | `List[str]` | 否  | `None`           | 所有者 Open ID 列表               |
| `chat_ids`   | `List[str]` | 否  | `None`           | 文件所在群 ID 列表                  |
| `docs_types` | `List[str]` | 否  | `["doc","docx","wiki"]` | 文档类型枚举，包含 `wiki` 时会自动聚合 wiki 节点搜索结果 |

**使用示例**：

```python
# 基础搜索
result = tool.search_docs(search_key="项目计划")

# 指定类型搜索
result = tool.search_docs(
    search_key="季度报告",
    docs_types=["doc", "docx", "wiki"]
)

# 分页搜索
result = tool.search_docs(
    search_key="技术方案",
    count=20,
    offset=0
)
```

**返回示例**：

```json
{
  "success": true,
  "message": "搜索成功",
  "data": {
    "total": 12,
    "has_more": false,
    "warnings": {
      "wiki_error": {
        "message": "权限不足，请为应用开通 wiki 搜索相关权限",
        "error": {
          "type": "permission_denied",
          "detail": "HTTP 403: ..."
        }
      }
    },
    "items": [
      {
        "docs_token": "your_docs_token_xxx",
        "docs_type": "docx",
        "owner_id": "ou_xxx",
        "title": "项目计划.docx",
        "url": "https://xxx.feishu.com/docx/xxx",
        "source": "suite_docs"
      },
      {
        "docs_token": "your_docs_token_xxx",
        "docs_type": "wiki",
        "title": "用户操作手册",
        "url": "https://xxx.feishu.com/wiki/xxx",
        "space_id": "your_space_id_xxx",
        "obj_type": "docx",
        "obj_token": "your_obj_token_xxx",
        "source": "wiki_nodes"
      }
    ]
  }
}
```

***

### 3. 搜索 wiki 节点 - `search_wiki_nodes()`

**功能**：按 wiki 节点标题/内容搜索知识库文档

**参数说明**：

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- | :--- |
| `keyword` | `str` | 是 | - | 搜索关键词 |
| `count` | `int` | 否 | `None` | 返回数量 |
| `offset` | `int` | 否 | `None` | 偏移量 |
| `space_id` | `str` | 否 | `None` | 指定 wiki 知识空间 |

**使用示例**：

```python
result = tool.search_wiki_nodes(
    keyword="用户操作手册",
    space_id="your_space_id_xxx"
)
```

**返回示例**：

```json
{
  "success": true,
  "message": "搜索成功",
  "data": {
    "total": 1,
    "has_more": false,
    "items": [
      {
        "docs_token": "your_docs_token_xxx",
        "docs_type": "wiki",
        "title": "用户操作手册",
        "url": "https://xxx.feishu.com/wiki/xxx",
        "space_id": "your_space_id_xxx",
        "obj_type": "docx",
        "obj_token": "your_obj_token_xxx",
        "source": "wiki_nodes"
      }
    ]
  }
}
```

***

### 4. 读取文档内容 - `fetch_raw_content()`

**功能**：根据文档类型读取原始内容，支持 doc/docx

**参数说明**：

| 参数名          | 类型    | 必填 | 说明                |
| :----------- | :---- | :- | :---------------- |
| `docs_type`  | `str` | 是  | 文档类型：`doc`/`docx` |
| `docs_token` | `str` | 是  | 文档 token          |

**使用示例**：

```python
result = tool.fetch_raw_content(
    docs_type="docx",
    docs_token="your_docs_token_xxx"
)
```

**返回示例**：

```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "content": "Q4项目计划\n一、项目背景..."
  }
}
```

***

## 🔑 环境变量配置

| 环境变量名                    | 必填 | 说明                                          |
| :----------------------- | :- | :------------------------------------------ |
| `LARK_USER_ACCESS_TOKEN` | 是  | 飞书用户访问令牌，用于 `Authorization: Bearer <token>` |

也可在初始化时通过 `FeishuDocSearch(access_token="u-xxx")` 传入。

***

## 🚨 错误处理

| 错误类型     | 识别方式                 | 返回提示                              |
| :------- | :------------------- | :-------------------------------- |
| 认证失败     | `401`/`Unauthorized` | "认证失败，请检查 access\_token 是否有效或已过期" |
| 权限不足     | `403`/`Forbidden`    | "权限不足，请为应用开通云文档搜索相关权限"            |
| 请求超时     | 包含 `timeout`         | "请求超时，请稍后重试"                      |
| 搜索参数错误   | `search_key` 为空      | "search\_key 不能为空"                |
| 不支持的文档类型 | 未知的 `docs_type`      | "不支持的 docs\_type，仅支持 doc 和 docx"  |

***

## 📝 使用流程建议

### 典型流程：搜索文档并读取内容

1. 调用 `search_docs()` 搜索关键词
2. 从结果中获取 `docs_token` 和 `docs_type`
3. 调用 `fetch_raw_content()` 读取文档内容

```python
# 1. 搜索
search_result = tool.search_docs(search_key="项目计划")
if not search_result.get("success"):
    print(search_result.get("message"))
    exit()

items = search_result.get("data", {}).get("items", [])
if not items:
    print("未找到相关文档")
    exit()

# 2. 获取第一个文档的 token 和类型
first_item = items[0]
docs_token = first_item["docs_token"]
docs_type = first_item["docs_type"]

# 3. 读取内容
content_result = tool.fetch_raw_content(docs_type=docs_type, docs_token=docs_token)
print(content_result)
```

***

## 📋 文档类型枚举

| docs\_type | 说明                                 |
| :--------- | :--------------------------------- |
| `doc`      | 旧版飞书文档                             |
| `docx`     | 新版飞书文档                             |
| `wiki`     | 飞书 wiki 文档（会自动读取关联的 doc/docx 文档内容） |

***

### 5. 获取 wiki 节点信息 - `get_wiki_node()`

**功能**：获取 wiki 节点的详细信息，包括标题、关联文档类型等

**参数说明**：

| 参数名          | 类型    | 必填 | 说明             |
| :----------- | :---- | :- | :------------- |
| `node_token` | `str` | 是  | wiki 节点的 token |

**使用示例**：

```python
result = tool.get_wiki_node(node_token="your_node_token_xxx")
```

**返回示例**：

```json
{
  "success": true,
  "message": "获取成功",
  "data": {
    "node_token": "your_node_token_xxx",
    "title": "文档标题",
    "obj_type": "docx",
    "obj_token": "your_obj_token_xxx",
    "node_type": "origin",
    "space_id": "your_space_id_xxx",
    "creator": "ou_xxx",
    "owner": "ou_xxx"
  }
}
```

***

## ⚠️ 注意事项

- 搜索的 `count` 参数最大值为 50，且 `offset + count < 200`
- `search_docs()` 在包含 `wiki` 类型时会聚合 suite/docs 搜索与 wiki 节点搜索，并按对象去重
- 若已知 wiki 链接或 node token，优先使用 `search_wiki_nodes()` 或 `get_wiki_node()` + `fetch_raw_content()` 组合
