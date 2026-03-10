# CPU 打满故障排查

## 概述

CPU 打满是指 Redis 实例的 CPU 使用率持续接近或达到 100%，导致响应变慢或完全无响应。Redis 是单线程模型，CPU 打满通常意味着某个命令消耗过多 CPU。

## 典型症状

- CPU 使用率持续 100% 或接近 100%
- 命令响应变慢
- 客户端超时
- 请求堆积

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="Redis"
)
```

### 步骤 1: 检查 CPU 使用率

```python
import time
now = int(time.time())

# 获取 CPU 使用率
toolbox.get_metric_data(
    metric_name="CpuUsage",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="redis-xxx",
    instance_type="Redis"
)
```

### 步骤 2: 获取命令统计

```python
# 获取命令统计
toolbox.execute_sql(
    commands="INFO commandstats;", database="0"
)
```

### 步骤 3: 检查慢日志

```python
# 获取慢命令
toolbox.execute_sql(
    commands="SLOWLOG GET 20;", database="0"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| KEYS/SCAN | 遍历全量 key |
| SORT | 排序操作 |
| 大 Set 操作 | 大 set 的交集/并集 |
| Lua Script | 复杂 Lua 脚本 |
| HGETALL | 获取大 hash |

## ⚠️ 应急处置（需确认后执行）

### 终止高 CPU 客户端

> **警告**：终止客户端会导致当前任务失败，请在确认后执行！

```python
# 终止指定客户端
toolbox.execute_sql(
    commands="CLIENT KILL ID <id>;", database="0"
)
```

## 预防措施

1. 避免 KEYS 命令，使用 SCAN 代替
2. 使用适当的数据结构
3. 设置命令超时
4. 监控慢命令
5. 使用 pipeline 批量操作
6. 设置 CPU 使用告警
