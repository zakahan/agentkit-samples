# QueryClueInfo 接口完整参数说明

本文档详细说明市场洞察 Agent 的 QueryClueInfo 接口的请求参数、响应参数、ClueText 数据模型和使用注意事项。

---

## 接口概述

QueryClueInfo 接口用于查询指定时间范围内的商机信息。返回的每条商机包含结构化的 AI 分析数据（ACOR 评估、公司画像、竞争分析、解决方案映射等），以 JSON 字符串形式存储在 `ClueText` 字段中。

- **接口名称**：QueryClueInfo
- **接口中文名**：商机信息查询
- **HTTP 方法**：GET（带 JSON Body）
- **URL**：`{ARK_SKILL_API_BASE}/?Action=QueryClueInfo&Version=2025-09-05`
- **鉴权**：Bearer Token（API Key）
- **服务版本**：`2025-09-05`
- **QPS 限制**：200（账号默认 100）
- **超时**：3000ms

> **注意**：此接口使用 GET 方法但携带 JSON Body，使用 `urllib` 时需通过 `req.get_method = lambda: "GET"` 强制覆盖。

---

## 请求参数

JSON Body 字段名为 PascalCase。

| JSON 字段名 | 类型 | 是否必填 | 说明 | 示例 |
|------------|------|---------|------|------|
| `StartTime` | str | **是** | 起始时间 | `"2026-03-18 00:00:00"` |
| `EndTime` | str | **是** | 结束时间 | `"2026-03-18 23:00:00"` |
| `MaxResults` | int | 否 | 每页最大返回结果数 | `10` |
| `NextToken` | str | 否 | 分页游标，首次不传，后续使用响应中返回的值 | `"1773782470"` |

### 时间格式

`StartTime` 和 `EndTime` 格式均为 `"YYYY-MM-DD HH:MM:SS"`。

### NextToken 说明

- 首次请求不传 `NextToken`
- 后续请求使用上一次响应中的 `NextToken` 值
- `NextToken` 的值为**时间戳字符串**（如 `"1773782470"`），不可解析或自行构造

### 与其他接口的参数区别

| 维度 | QueryClueInfo | PullPost | ListCustomSubsTask |
|------|--------------|----------|-------------------|
| 每页条数 | `MaxResults` | `Size` | `PageSize` |
| 分页游标 | `NextToken` | `PageToken` | `PageNum`（页码） |
| 任务 ID | **无** | `TaskID` | **无** |
| 名称搜索 | **无** | **无** | `TaskName` |

> **注意**：绝不可混用参数。QueryClueInfo 没有 `TaskID`、`Size`、`PageToken`、`PageNum`、`PageSize` 参数，传了也会被忽略。

---

## 响应参数

### Result 字段

| JSON 字段名 | 类型 | 说明 |
|------------|------|------|
| `ClueList` | Array[Clue] | 商机列表 |
| `NextToken` | str | 下一页游标（为空时表示没有更多数据） |
| `ResultCnt` | int | 当前页返回的结果总数 |

---

## Clue 对象字段说明

`ClueList` 数组中每个对象代表一条商机信息。

| JSON 字段名 | 类型 | 说明 |
|------------|------|------|
| `ClueID` | str | 商机唯一标识（如 `"10007614978"`） |
| `ClueText` | str | **商机内容 — JSON 字符串**，包含完整的结构化商机分析数据 |
| `CreateTime` | str | 创建时间（毫秒级时间戳字符串） |

> **重要**：`ClueText` 不是普通文本，而是一个 **嵌套 JSON 字符串**。必须先用 `json.loads(clue["ClueText"])` 解析后才能使用。

---

## ClueText JSON 完整结构

`ClueText` 经 `json.loads()` 解析后为一个 dict，包含以下 7 个顶层模块：

```
ClueText (JSON 字符串)
├── opportunity_briefing      — 商机简报
├── company_profile           — 公司画像
├── acorn_assessment          — ACOR 四维评估
├── competitive_analysis      — 竞争分析（数组）
├── deep_dive_analysis        — 深度分析
├── solution_mapping_and_value_proposition — 解决方案映射（数组）
└── triggering_event          — 触发事件
```

### 1. `opportunity_briefing` — 商机简报

商机的核心摘要信息，通常用于快速判断商机价值。

| 字段 | 类型 | 说明 |
|------|------|------|
| `title` | str | 商机标题（如 `"xxx公司 | 高质量数据集管理服务与数据标注平台建设"`） |
| `priority_level` | str | 优先级（如 `"A"`、`"B"`、`"C"`），A 为最高 |
| `executive_summary` | str | 执行摘要，简述商机核心内容和建议 |
| `key_opportunity_facts` | dict | 关键商机事实（子字段见下） |

#### `key_opportunity_facts` 子字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `target_company_profile` | str | 目标公司概况（行业、规模、资质等） |
| `identified_ai_need` | str | 已识别的 AI 需求 |
| `estimated_opportunity_scale` | str | 预估商机规模（金额、项目范围等） |
| `project_readiness` | str | 项目准备程度（如"已中标，处于实施阶段"） |
| `primary_competitor_signal` | str | 主要竞品信号 |

### 2. `company_profile` — 公司画像

目标公司的基本信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| `legal_name` | str | 公司法定名称 |
| `address` | str | 公司地址 |
| `business_category` | str | 业务类别（如 `"通用AI工具及SaaS服务"`） |
| `credit_code` | str | 统一社会信用代码 |
| `email` | str | 联系邮箱 |
| `phone` | str | 联系电话 |
| `official_website` | str/null | 官网地址（可能为 null） |

### 3. `acorn_assessment` — ACOR 四维评估

基于 ACOR 模型的商机多维度评估。

| 字段 | 类型 | 说明 |
|------|------|------|
| `radar_data` | dict | 雷达图评分数据 |
| `detailed_analysis` | list | 各维度详细分析列表 |

#### `radar_data` — 评分维度

| 键 | 全称 | 含义 | 分值范围 |
|----|------|------|---------|
| `A` | Account（客户画像） | 客户资质、规模、行业匹配度 | 1-5 |
| `C` | Core need（核心需求） | 需求明确度、迫切性、与产品契合度 | 1-5 |
| `O` | Opportunity（商机价值） | 项目金额、规模、复制潜力 | 1-5 |
| `R` | Readiness（时机与关系） | 项目阶段、竞品介入、切入时机 | 1-5 |

#### `detailed_analysis` 数组元素

每个维度一条详细分析记录：

| 字段 | 类型 | 说明 |
|------|------|------|
| `dimension` | str | 评估维度（如 `"A - 客户画像"`、`"C - 核心需求"`、`"O - 商机价值"`、`"R - 时机与关系"`） |
| `score` | float | 该维度评分（1-5） |
| `analyst_insight` | str | 分析师洞察，对该维度的专业分析 |
| `key_objective_facts` | list | 关键客观事实列表 |

#### `key_objective_facts` 数组元素

| 字段 | 类型 | 说明 |
|------|------|------|
| `fact` | str | 事实描述 |
| `source_url` | str/null | 来源链接（可能为 null） |

### 4. `competitive_analysis` — 竞争分析

数组，每个元素代表一个竞争对手的分析。

| 字段 | 类型 | 说明 |
|------|------|------|
| `competitor_name` | str | 竞品名称（如 `"科大讯飞"`） |
| `relationship_type` | str | 关系类型（如 `"已合作"`、`"潜在竞品"`） |
| `evidence` | dict | 竞品证据，含 `fact`（事实描述）和 `source_url`（来源链接） |
| `ve_counter_strategy` | str | 火山引擎应对策略建议 |

### 5. `deep_dive_analysis` — 深度分析

对触发事件的深入分析。

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_summary` | str | 事件摘要（完整的事件描述和背景） |
| `event_meta` | dict | 事件元数据（子字段见下） |

#### `event_meta` 子字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_date` | str | 事件日期（如 `"2026-03-17"`） |
| `source_quote` | str | 来源原文引用 |
| `source_url` | str | 来源链接 |

### 6. `solution_mapping_and_value_proposition` — 解决方案映射

数组，每个元素代表一组痛点-方案映射。

| 字段 | 类型 | 说明 |
|------|------|------|
| `opportunity_title` | str | 机会标题 |
| `customer_pain_point` | str | 客户痛点描述 |
| `ve_value_proposition` | dict | 火山引擎价值主张（子字段见下） |

#### `ve_value_proposition` 子字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `solution` | str | 推荐解决方案 |
| `value` | list[str] | 价值点列表 |

### 7. `triggering_event` — 触发事件

识别到该商机的触发事件信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| `event_description` | str | 事件描述 |
| `source_quote` | str | 来源原文引用 |
| `source_url` | str | 来源链接 |

---

## Demo 请求与响应

### 请求示例

```json
{
    "StartTime": "2026-03-18 00:00:00",
    "EndTime": "2026-03-18 23:00:00",
    "MaxResults": 1,
    "NextToken": "1773782470"
}
```

### 响应示例（结构简化）

```json
{
    "ResponseMetadata": {
        "Action": "QueryClue",
        "RequestId": "..."
    },
    "Result": {
        "ClueList": [
            {
                "ClueID": "10007614978",
                "ClueText": "{\"opportunity_briefing\":{...},\"company_profile\":{...},\"acorn_assessment\":{...},...}",
                "CreateTime": "1773782513022"
            }
        ],
        "NextToken": "1773782513",
        "ResultCnt": 1
    }
}
```

> 注意：`ClueText` 在实际响应中是一个完整的 JSON 字符串（此处省略），需要 `json.loads()` 解析。`CreateTime` 为毫秒级时间戳字符串。

---

## 错误码与限流

### 鉴权错误
| HTTP 状态码 | 说明 |
|-----------|------|
| 401 | API Key 无效或已过期 |
| 403 | 无权访问该接口 |

### 限流错误码
| 错误码 | 说明 |
|-------|------|
| `Throttling` | 请求被限流 |
| `RequestLimitExceeded` | 请求超出限制 |

### 限流处理建议

1. 遵守 API 的 QPS 限制（200 QPS，账号默认 100）
2. 循环查询时在请求间加入适当延时（如 `time.sleep(0.1)`）
3. 收到限流错误时采用**指数退避策略**重试

---

## 分页逻辑详解

```
┌─────────────────────────────────────┐
│ 1. 构造首次请求                      │
│    StartTime + EndTime              │
│    + MaxResults (不带 NextToken)     │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 2. 发送 GET 请求，获取响应           │
│    → ClueList (商机列表)             │
│    → ResultCnt (当前页数量)           │
│    → NextToken (下页游标)            │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 3. 处理当前页 ClueList               │
│    对每条 clue：                     │
│    json.loads(clue["ClueText"])     │
│    → 提取结构化商机数据               │
└──────────────┬──────────────────────┘
               ▼
     ┌────────────────────┐
     │ NextToken 非空？    │
     │ ClueList 非空？     │
     └────────┬───────────┘
        yes   │   no
     ┌────────┴────────┐
     ▼                 ▼
┌────────────┐  ┌──────────┐
│ 设置        │  │ 结束循环  │
│ NextToken   │  └──────────┘
│ = 响应的     │
│ NextToken   │
│ 回到步骤 2  │
└────────────┘
```

---

## 正确调用示例（HTTP API + Bearer Token）

```python
import json
import os
import time
import urllib.request

api_host = os.getenv("ARK_SKILL_API_BASE")
api_key = os.getenv("ARK_SKILL_API_KEY")
url = f"{api_host}/?Action=QueryClueInfo&Version=2025-09-05"

headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {api_key}",
    "ServiceName": "insight",
}

payload = {
    "StartTime": "2026-03-18 00:00:00",
    "EndTime": "2026-03-18 23:00:00",
    "MaxResults": 10,
}

all_clues = []
while True:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers)
    req.get_method = lambda: "GET"  # 强制 GET + JSON Body

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())["Result"]

    clues = result.get("ClueList", [])
    for clue in clues:
        clue_data = json.loads(clue["ClueText"])  # 必须 json.loads 解析

        # 商机简报
        briefing = clue_data["opportunity_briefing"]
        print(f"[{clue['ClueID']}] [{briefing['priority_level']}] {briefing['title']}")
        print(f"  摘要: {briefing['executive_summary'][:120]}")

        # 公司画像
        company = clue_data["company_profile"]
        print(f"  公司: {company['legal_name']} ({company['business_category']})")

        # ACOR 评分
        radar = clue_data["acorn_assessment"]["radar_data"]
        print(f"  ACOR: A={radar['A']} C={radar['C']} O={radar['O']} R={radar['R']}")

        # 竞争分析
        for comp in clue_data.get("competitive_analysis", []):
            print(f"  竞品: {comp['competitor_name']} ({comp['relationship_type']})")

        all_clues.append(clue_data)

    # 检查是否有下一页
    next_token = result.get("NextToken")
    if not next_token or not clues:
        break
    payload["NextToken"] = next_token
    time.sleep(0.1)

print(f"共获取 {len(all_clues)} 条商机")
```

---

## 常见错误

### 错误 1：参数混用

```python
# ❌ 错误：使用了 PullPost / ListCustomSubsTask 的参数
payload = {
    "TaskID": 1509,       # ❌ QueryClueInfo 没有 TaskID
    "Size": 50,           # ❌ 应为 MaxResults
    "PageToken": "...",   # ❌ 应为 NextToken
}

# ✅ 正确
payload = {
    "StartTime": "2026-03-18 00:00:00",
    "EndTime": "2026-03-18 23:00:00",
    "MaxResults": 10,
}
```

### 错误 2：未解析 ClueText

```python
# ❌ ClueText 是字符串，不能直接当 dict 用
title = clue["ClueText"]["opportunity_briefing"]["title"]

# ✅ 正确：必须先 json.loads
clue_data = json.loads(clue["ClueText"])
title = clue_data["opportunity_briefing"]["title"]
```

### 错误 3：HTTP 方法错误

```python
# ❌ 错误：使用 POST 方法
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

# ✅ 正确：强制 GET + JSON Body
req = urllib.request.Request(url, data=data, headers=headers)
req.get_method = lambda: "GET"
```
