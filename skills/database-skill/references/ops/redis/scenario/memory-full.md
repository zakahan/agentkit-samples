# 内存打满故障排查

## 概述

内存打满是指 Redis 实例的内存使用率达到 `maxmemory` 上限，导致 OOM (Out of Memory) 错误，无法写入新数据。

## 典型症状

- 内存使用率 100% 或达到 maxmemory 上限
- 写入数据报错: `OOM command not allowed when used memory`
- 内存监控显示持续高水位
- 数据被驱逐（如果配置了驱逐策略）

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="Redis"
)
```

### 步骤 1: 检查内存使用率

```python
import time
now = int(time.time())

# 获取内存使用率
toolbox.get_metric_data(
    metric_name="MemoryUsage",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="redis-xxx",
    instance_type="Redis"
)
```

### 步骤 2: 获取内存信息

```python
# 获取 Redis 内存信息
toolbox.execute_sql(
    commands="INFO memory;", database="0"
)
```

### 步骤 3: 检查驱逐策略

```python
# 检查 maxmemory policy
toolbox.execute_sql(
    commands="CONFIG GET maxmemory-policy;", database="0"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 数据增长 | 数据快速增长，未及时清理 |
| 大 Key | 大 key 占用大量内存 |
| 内存泄漏 | 内存泄漏 |
| 连接泄漏 | 连接未正确关闭 |

## ⚠️ 应急处置（需确认后执行）

### 清空数据库

> **警告**：清空数据库会删除所有数据，请在确认后执行！

```python
# 异步清空数据库
toolbox.execute_sql(
    commands="FLUSHDB ASYNC;", database="0"
)
```

### 调整 maxmemory

> **警告**：修改参数可能影响业务，请在确认后执行！

```python
# 临时增加 maxmemory
toolbox.execute_sql(
    commands="CONFIG SET maxmemory 4gb;", database="0"
)
```

## 预防措施

1. 设置内存监控和告警
2. 对 key 使用 TTL
3. 实施数据清理策略
4. 监控大 key
5. 使用适当的驱逐策略
6. 设置内存使用预测
