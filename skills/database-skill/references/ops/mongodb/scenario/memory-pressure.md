# 内存压力故障排查

## 概述

内存压力是指 MongoDB 实例的内存使用率持续较高，可能导致 OOM、WiredTiger 缓存命中率下降、查询性能下降等问题。

## 典型症状

- 内存使用率持续 80% 以上
- WiredTiger 缓存命中率下降
- 查询性能下降
- OOM 报错

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="Mongo"
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
    instance_id="mongo-xxx",
    instance_type="Mongo"
)
```

### 步骤 2: 检查 WiredTiger 缓存

```python
# 获取 WiredTiger 缓存使用情况
toolbox.execute_sql(
    commands="db.serverStatus().wiredTiger.cache;", database="admin"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| WiredTiger Cache 太小 | WiredTiger 缓存配置过小 |
| 连接数过多 | 连接数过多 |
| 大查询 | 大查询消耗过多内存 |
| 大排序操作 | 大排序操作 |

## 预防措施

1. 正确配置 WiredTiger 缓存大小
2. 设置适当的连接限制
3. 监控内存使用趋势
4. 优化查询以减少内存消耗
5. 设置内存使用告警
6. 使用投影限制数据传输
