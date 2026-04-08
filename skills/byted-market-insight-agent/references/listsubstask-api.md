# ListCustomSubsTask 接口完整参数说明

本文档详细说明市场洞察 Agent 的 ListCustomSubsTask 接口的请求参数、响应参数、数据模型和使用注意事项。

---

## 接口概述

ListCustomSubsTask 接口用于分页查询当前账号下的所有监控/订阅任务列表信息，支持按状态过滤和任务名称模糊搜索。

- **接口名称**：ListCustomSubsTask
- **HTTP 方法**：GET（带 JSON Body）
- **URL**：`{ARK_SKILL_API_BASE}/?Action=ListCustomSubsTask&Version=2025-09-05`
- **鉴权**：Bearer Token（API Key）
- **服务版本**：`2025-09-05`
- **QPS 限制**：100
- **超时**：30 秒

> **注意**：此接口使用 GET 方法但携带 JSON Body，使用 `urllib` 时需通过 `req.get_method = lambda: "GET"` 强制覆盖。

---

## 请求参数

所有参数均为可选。JSON Body 字段名为 PascalCase。

| JSON 字段名 | 类型 | 是否必填 | 说明 | 示例 |
|------------|------|---------|------|------|
| `Status` | int | 否 | 任务状态过滤：`1`=运行中，`2`=全部状态 | `1` |
| `TaskName` | str | 否 | 任务名称模糊搜索 | `"测试任务"` |
| `PageNum` | int | 否 | 分页页码，从 1 开始 | `1` |
| `PageSize` | int | 否 | 分页大小（每页返回的任务条数） | `10` |

### Status — 任务状态过滤

| 值 | 含义 | 说明 |
|---|------|------|
| `1` | 运行中 | 只返回当前正在运行的任务 |
| `2` | 全部 | 返回所有状态的任务 |

### TaskName — 任务名称模糊搜索

传入关键词进行模糊搜索。可用于在大量任务中快速定位特定任务。不传则不过滤。

### 分页说明

- `PageNum` 从 1 开始计数
- 如果需要获取所有任务，从 PageNum=1 开始逐页递增，直到 `PageNum * PageSize >= Total`
- 默认 PageSize 建议使用 10

---

## 响应参数

JSON 响应外层包装在 `Result` 字段中，实际数据结构如下：

### Result 字段

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `InsightSaasTaskList` | Array[Task] | 当前页的任务列表 |
| `Total` | int | 符合筛选条件的任务总数 |

---

## Task 对象字段说明

`InsightSaasTaskList` 数组中每个对象代表一个订阅/监控任务。

> **注意**：JSON 响应中字段名为 PascalCase。部分字段类型为 str（非 int）。

### 基础信息

| 字段名 | 类型 | 说明 | 备注 |
|-------|------|------|------|
| `TaskID` | int | 任务唯一标识符 | **关键字段**，可直接用于 PullPost 接口的 `TaskID` 参数 |
| `Name` | str | 任务名称 | 用户在创建任务时设定的名称 |
| `Aim` | str | 用户意图 | 描述该监测任务的目标/意图 |
| `AccountID` | str | 用户 ID | 创建该任务的账号 ID |

### 策略配置

| 字段名 | 类型 | 说明 | 备注 |
|-------|------|------|------|
| `Recall` | str | 初筛策略 | AI 初步筛选的策略配置 |
| `Precise` | str | 精筛策略 | AI 精准筛选的策略配置 |
| `Judge` | str | 研判策略 | AI 风险研判的策略配置 |
| `Dsl` | str | 规则引擎 DSL | 规则引擎的领域特定语言表达式 |

### 状态与时间

| 字段名 | 类型 | 说明 | 备注 |
|-------|------|------|------|
| `Status` | **str** | 任务状态：`"0"`=已关闭, `"1"`=运行中 | 类型为 str，比较时注意类型转换 |
| `PushStatus` | **str** | 推送状态：`"1"`=开启, `"0"`=关闭 | 类型为 str |
| `CreateTime` | **str** | 任务创建时间 | 类型为 str |
| `ModifyTime` | int | 任务最后修改时间（Unix 时间戳，秒） | - |

### 关联信息

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `DialogID` | str | 会话 ID |
| `PreviewList` | Array[Preview] | 发文预览列表 |

---

## PreviewList 对象字段说明

`PreviewList` 数组中每个对象是该任务最近命中的一条数据的简要信息。

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `PostID` | str | 发文 ID（与 PullPost 返回的 `PostID` 对应） |
| `Title` | str | 发文标题 |

---

## 错误码

### 接口专属错误码
| 错误码 | HTTP 状态码 | 说明 |
|-------|-----------|------|
| `InvalidParameter` | 400 | 参数错误 |

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

---

## 分页逻辑详解

```
┌─────────────────────────────────────┐
│ 1. 构造首次请求                      │
│    Status + TaskName (可选)          │
│    PageNum=1, PageSize=10           │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 2. 发送请求，获取响应                 │
│    → InsightSaasTaskList (任务列表)  │
│    → Total (总任务数)                │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 3. 处理当前页 InsightSaasTaskList    │
└──────────────┬──────────────────────┘
               ▼
     ┌──────────────────┐
     │ 还有更多页？       │
     │ PageNum *         │
     │ PageSize < Total  │
     └────────┬─────────┘
        yes   │   no
     ┌────────┴────────┐
     ▼                 ▼
┌────────────┐  ┌──────────┐
│ PageNum    │  │ 结束循环  │
│ += 1       │  └──────────┘
│ 回到步骤 2  │
└────────────┘
```

---

## 与 PullPost 的关系

ListCustomSubsTask 和 PullPost 是市场洞察产品最常用的两个接口，通常配合使用：

1. **先调用 ListCustomSubsTask** — 获取当前账号下所有订阅任务的 `TaskID` 和基本信息
2. **再调用 PullPost** — 使用获取到的 `TaskID`，拉取该任务的 AI 精筛数据

---

## 正确调用示例（HTTP API + Bearer Token）

```python
import json
import os
import urllib.request

api_host = os.getenv("ARK_SKILL_API_BASE")
api_key = os.getenv("ARK_SKILL_API_KEY")
url = f"{api_host}/?Action=ListCustomSubsTask&Version=2025-09-05"

payload = {
    "Status": 2,
    "PageNum": 1,
    "PageSize": 10,
    "TaskName": "品牌监测",  # 可选
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {api_key}",
    "ServiceName": "insight",
})
req.get_method = lambda: "GET"  # 强制 GET + JSON Body

with urllib.request.urlopen(req, timeout=30) as resp:
    result = json.loads(resp.read())["Result"]
    tasks = result.get("InsightSaasTaskList", [])
    total = result.get("Total", 0)

    for t in tasks:
        # 注意：Status 和 PushStatus 为 str 类型
        print(f"[{t['TaskID']}] {t['Name']} (状态: {t['Status']}) — {t.get('Aim', '')}")
```

---

## 常见错误

```python
# ❌ 错误：Status 为 str 类型，不能直接与 int 比较
if task["Status"] == 1:  # 永远不匹配
    ...

# ✅ 正确：使用字符串比较
if str(task["Status"]) == "1":
    ...

# ❌ 错误：使用 POST 方法（此接口要求 GET）
req = urllib.request.Request(url, data=data, headers=headers, method="POST")

# ✅ 正确：强制 GET + JSON Body
req = urllib.request.Request(url, data=data, headers=headers)
req.get_method = lambda: "GET"
```
