# PullPost 接口完整参数说明

本文档详细说明市场洞察 Agent 的 PullPost 接口的请求参数、响应参数、数据模型和使用注意事项。

官方文档：https://www.volcengine.com/docs/83600/1174737

---

## 接口概述

PullPost 接口用于拉取指定监测任务在特定时间范围内经过 AI 精筛后的帖子/内容数据。

- **接口名称**：PullPost
- **HTTP 方法**：POST
- **URL**：`{ARK_SKILL_API_BASE}/?Action=PullPost&Version=2025-09-05`
- **鉴权**：Bearer Token（API Key）
- **服务版本**：`2025-09-05`

---

## 请求参数

JSON Body 字段名为 PascalCase。

| 字段名 | 类型 | 是否必填 | 说明 | 约束 |
|-------|------|---------|------|------|
| `TaskID` | Integer | **是** | 订阅任务 ID。从监测任务管理页面 URL 中获取（如 `.../risk/1509`，TaskID 为 1509） | 必须为有效的任务 ID |
| `StartTime` | String | **首次必填** | 数据拉取起始时间。**仅首次请求（不携带 PageToken）时生效** | 格式: `"YYYY-MM-DD HH:MM:SS"` |
| `EndTime` | String | **首次必填** | 数据拉取结束时间 | 格式同 StartTime |
| `Size` | Integer | 否 | 每页返回的数据条数 | 默认 20，最大 100 |
| `PageToken` | String | 否 | 分页游标。首次请求不传，后续使用上次响应的 `NextPageToken` | 不透明字符串，不可解析或构造 |

### 关键行为说明

1. **StartTime 语义**：`StartTime` 仅在首次请求（不携带 `PageToken`）时生效。分页开始后，`StartTime` 和 `EndTime` 均被忽略。如需更改时间范围，必须发起一个全新的请求（不带 `PageToken`）。

2. **数据快照**：首次请求会对匹配数据生成快照。分页期间新产生的数据不会出现在当前分页结果中。数据默认按 `UpdateTime` 降序排列。

---

## 响应参数

### Result 字段

| 字段名 | 类型 | 说明 |
|-------|------|------|
| `ItemDocs` | Array[Post] | 当前页的数据列表 |
| `HasMore` | Boolean | `true` 表示有后续页，需继续分页 |
| `NextPageToken` | String | 下一页的分页游标 |

---

## Post 对象字段说明

`ItemDocs` 数组中每个对象代表一条独立的内容数据。

### 基础信息

| 字段名 | 类型 | 说明 | 备注 |
|-------|------|------|------|
| `PostID` | String | 数据的唯一标识符 | 如 `"12132132132132"`，可用作幂等键去重 |
| `Title` | String | 数据标题 | - |
| `Content` | String | 数据正文 | **大字段**，内容可能很长，注意内存消耗 |
| `Summary` | String | 数据摘要 | - |
| `URL` / `Url` | String | 原始数据链接 | 可用于跳转到原始来源 |
| `PublishTime` | String | 数据发布时间 | 格式 `"YYYY-MM-DD HH:MM:SS"` |
| `UpdateTime` | String | 数据入库或更新时间 | 可用于增量同步 |

### 多模态内容

| 字段名 | 类型 | 说明 | 备注 |
|-------|------|------|------|
| `Ocr` | String | 图片 OCR 提取的文本内容 | **大字段**，来自图片文字识别 |
| `OcrHigh` | String | 高质量 OCR 文本 | 经过消重、标点标记等清理，语义更连贯 |
| `Asr` | String | 音频语音识别 (ASR) 提取的文本 | 来自视频/音频内容的语音转文字 |

### 来源与作者

| 字段名 | 类型 | 说明 | 备注 |
|-------|------|------|------|
| `MainDomain` | String | 数据来源的主域名 | 如 `"douyin.com"`、`"weibo.com"` |
| `MediaName` | String | 发布作者或媒体名称 | - |
| `FansCount` | Integer | 作者的粉丝数 | 无法获取时返回 0 或 null |
| `IsFollow` | Boolean | 是否为转发/跟帖/引用等非原创类型 | `true` 表示非原创 |

### AI 分析

| 字段名 | 类型 | 说明 | 备注 |
|-------|------|------|------|
| `RiskType` | Array | 风险标签列表 | 标识数据中可能存在的风险类型 |
| `Emotion` | String | 情感分析标签 | AI 识别的内容情感倾向 |
| `Reason` | String | AI 精筛原因 | 解释为何此条数据被 AI 模型选中 |
| `DedupID` / `DedupId` | String | 聚类 ID | 相同值为同一事件/话题的强相关内容，可用于去重和聚合 |

### 地理位置 (Locations)

`Locations` 是一个 Location 对象数组，每个对象代表一个提及的地理位置。

| 字段名 | 类型 | 必填 | 说明 |
|-------|------|------|------|
| `Name` | String | 是 | 地理位置名称 |
| `Region` | String | 否 | 所属区域，如 `"CN"` |
| `Province` | String | 否 | 省份 |
| `City` | String | 否 | 城市 |
| `District` | String | 否 | 区/县 |
| `Town` | String | 否 | 乡/镇/街道 |
| `RegionCode` | String | 否 | 区域行政代码 |
| `CityCode` | String | 否 | 城市行政代码 |
| `DistrictCode` | String | 否 | 区/县行政代码 |
| `TownCode` | String | 否 | 乡/镇/街道行政代码 |
| `Location` | String | 否 | 完整的地理位置描述 |

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

1. 遵守 API 的 QPS 限制
2. 循环拉取时在请求间加入适当延时（如 `time.sleep(0.1)`）
3. 收到限流错误时采用**指数退避策略**重试

### 避免重复消费

- **分页层面**：PullPost 的数据快照机制保证同一次分页请求不会重复
- **跨请求层面**：多次独立请求拉取重叠时间段可能产生重复数据
- **解决方案**：使用 `PostID` 作为幂等键进行业务层去重

---

## 分页逻辑详解

```
┌─────────────────────────────────────┐
│ 1. 构造首次请求                      │
│    TaskID + StartTime + EndTime     │
│    + Size (不带 PageToken)           │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 2. 发送 POST 请求，获取响应          │
│    → ItemDocs (数据列表)             │
│    → HasMore (是否还有更多)           │
│    → NextPageToken                  │
└──────────────┬──────────────────────┘
               ▼
┌─────────────────────────────────────┐
│ 3. 处理当前页 ItemDocs 数据          │
└──────────────┬──────────────────────┘
               ▼
         ┌───────────┐
         │ HasMore?   │
         └─────┬─────┘
          yes  │  no
         ┌─────┴─────┐
         ▼           ▼
┌────────────┐  ┌──────────┐
│ 设置        │  │ 结束循环  │
│ PageToken   │  └──────────┘
│ = Next      │
│ PageToken   │
│ 回到步骤 2  │
└────────────┘
```

**注意**：使用 `PageToken` 分页后，`StartTime` 和 `EndTime` 将被忽略。

---

## 正确调用示例（HTTP API + Bearer Token）

```python
import json
import os
import time
import urllib.request

api_host = os.getenv("ARK_SKILL_API_BASE")
api_key = os.getenv("ARK_SKILL_API_KEY")
url = f"{api_host}/?Action=PullPost&Version=2025-09-05"

headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {api_key}",
    "ServiceName": "insight",
}

# 首次请求
payload = {
    "TaskID": 2445,
    "StartTime": "2026-03-19 20:24:08",
    "EndTime": "2026-03-19 23:24:08",
    "Size": 50,
}

all_posts = []
while True:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")

    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())["Result"]

    docs = result.get("ItemDocs", [])
    has_more = result.get("HasMore", False)
    next_token = result.get("NextPageToken")

    for doc in docs:
        print(f"[{doc.get('PostID')}] {doc.get('Title', '(无标题)')}")
        all_posts.append(doc)

    if not has_more:
        break
    payload["PageToken"] = next_token
    time.sleep(0.1)

print(f"共获取 {len(all_posts)} 条数据")
```
