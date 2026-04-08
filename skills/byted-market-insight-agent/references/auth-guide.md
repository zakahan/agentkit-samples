# API Key 鉴权配置指南

本文档说明如何通过 API Key（Bearer Token）完成火山引擎市场洞察 API 鉴权。

---

## 概述

本技能使用 **API Gateway + Bearer Token** 鉴权模式，替代传统的 AK/SK + SDK 方式。无需安装任何 Python SDK，仅通过标准 HTTP 请求即可调用所有接口。

---

## 获取 API Key

1. 联系火山引擎市场洞察团队获取 API Gateway 地址和 API Key
2. API Gateway 地址格式通常为：`https://{gateway-id}.apigateway-cn-beijing.volceapi.com`

---

## 配置凭证

### 方式一：环境变量（强烈推荐）

```bash
export ARK_SKILL_API_BASE="你的API Gateway地址"
export ARK_SKILL_API_KEY="你的API Key"
```

**持久化配置**（写入 shell 配置文件）：

```bash
# Bash
echo 'export ARK_SKILL_API_BASE="你的API Gateway地址"' >> ~/.bashrc
echo 'export ARK_SKILL_API_KEY="你的API Key"' >> ~/.bashrc
source ~/.bashrc

# Zsh
echo 'export ARK_SKILL_API_BASE="你的API Gateway地址"' >> ~/.zshrc
echo 'export ARK_SKILL_API_KEY="你的API Key"' >> ~/.zshrc
source ~/.zshrc
```

### 方式二：代码中配置（仅限开发测试，不推荐用于生产）

```python
import os
api_host = os.getenv("ARK_SKILL_API_BASE", "你的API Gateway地址")
api_key = os.getenv("ARK_SKILL_API_KEY", "你的API Key")
```

---

## 请求鉴权方式

所有 API 请求通过 HTTP Header 传递鉴权信息：

```python
headers = {
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {api_key}",
    "ServiceName": "insight",
}
```

### 必需的请求头

| Header | 值 | 说明 |
|--------|-----|------|
| `Content-Type` | `application/json; charset=UTF-8` | JSON 请求体 |
| `Authorization` | `Bearer {ARK_SKILL_API_KEY}` | Bearer Token 鉴权 |
| `ServiceName` | `insight` | 服务名标识（**必须附带**） |

---

## 代码示例

```python
import json
import os
import urllib.request

# 从环境变量读取凭证
api_host = os.getenv("ARK_SKILL_API_BASE")
api_key = os.getenv("ARK_SKILL_API_KEY")

if not api_host or not api_key:
    raise SystemExit("缺少必要环境变量: ARK_SKILL_API_BASE, ARK_SKILL_API_KEY")

# 构造请求 URL（以 PullPost 为例）
url = f"{api_host}/?Action=PullPost&Version=2025-09-05"

# 构造请求 Body
payload = {
    "TaskID": 12345,
    "StartTime": "2026-01-20 00:00:00",
    "EndTime": "2026-01-21 00:00:00",
    "Size": 20,
}

# 发送请求
data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers={
    "Content-Type": "application/json; charset=UTF-8",
    "Authorization": f"Bearer {api_key}",
    "ServiceName": "insight",
}, method="POST")

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
        print(json.dumps(result, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"请求失败: {e}")
```

---

## 安全建议

1. **切勿硬编码** — 永远不要将 API Key 以明文形式写入代码或提交到版本控制系统
2. **最小权限** — API Key 仅授予必要的接口访问权限
3. **定期轮换** — 定期轮换 API Key，降低泄露风险
4. **监控审计** — 监控 API Key 的使用情况和请求频率

---

## 与旧鉴权方式的对比

| 维度 | 旧方式（AK/SK + SDK） | 新方式（API Key + HTTP） |
|------|---------------------|------------------------|
| 鉴权凭证 | `VOLCSTACK_ACCESS_KEY_ID` + `VOLCSTACK_SECRET_ACCESS_KEY` | `ARK_SKILL_API_BASE` + `ARK_SKILL_API_KEY` |
| SDK 依赖 | 需安装 `volcenginesdkinsight`（含本地 zip） | **无需任何 SDK** |
| 请求方式 | SDK 方法调用（如 `api.pull_post(request)`） | 原生 HTTP 请求（`urllib`） |
| 签名机制 | HMAC 签名（SDK 自动处理） | Bearer Token（直接在 Header 中传递） |
| 参数命名 | snake_case（如 `task_id`、`page_size`） | PascalCase（如 `TaskID`、`PageSize`） |
| 环境要求 | Python 3.6+ + SDK 安装 | Python 3.6+ 标准库即可 |

---

## 常见鉴权错误

| 现象 | 可能原因 | 排查方式 |
|------|---------|---------|
| HTTP 401 | API Key 无效或已过期 | 检查 API Key 是否正确 |
| HTTP 403 | 无权访问该接口 | 确认 API Key 的权限范围 |
| 连接超时 | API Gateway 地址错误 | 检查 `ARK_SKILL_API_BASE` 是否正确 |
| `ServiceName` 相关错误 | 缺少 ServiceName 头 | 确认请求头包含 `ServiceName: insight` |
