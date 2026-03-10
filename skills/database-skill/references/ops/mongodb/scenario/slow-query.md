# 慢查询故障排查

## 概述

慢查询是指执行时间较长的 MongoDB 操作、数据量过大、，可能是由于缺少索引内存不足等原因导致。

## 典型症状

- 查询响应时间变长
- 慢查询日志增加
- 监控显示 QueryTime 增大
- 特定页面加载变慢

## 排查步骤

### 步骤 1: 获取慢查询趋势图

```python
import time
now = int(time.time())

# 获取慢查询时间序列趋势（了解慢查询随时间的变化）
toolbox.describe_slow_log_time_series_stats(
    start_time=now - 3600,
    end_time=now,
    instance_id="mongo-xxx",
    instance_type="Mongo",
    interval=300
)
```

### 步骤 2: 获取慢查询聚合统计

```python
# 获取慢查询聚合统计（按 SQL 模板聚合，找出最耗时的操作类型）
toolbox.describe_aggregate_slow_logs(
    start_time=now - 3600,
    end_time=now,
    instance_id="mongo-xxx",
    instance_type="Mongo",
    order_by="TotalQueryTime",
    sort_by="DESC"
)
```

### 步骤 3: 获取慢查询明细

```python
# 获取慢查询明细（查看具体哪些操作最慢）
toolbox.describe_slow_logs(
    start_time=now - 3600,
    end_time=now,
    order_by="QueryTime",
    sort_by="DESC"
)
```

### 步骤 4: 获取完整 SQL 历史

```python
# 获取完整操作历史详情（包含执行计划等详细信息）
toolbox.describe_full_sql_detail(
    start_time=now - 3600,
    end_time=now,
    instance_id="mongo-xxx",
    instance_type="Mongo",
    page_size=20
)
```

### 步骤 5: 检查当前操作

```python
# 获取当前正在执行的操作
toolbox.execute_sql(
    commands="""
    db.getSiblingDB('admin').aggregate([
        { $currentOp: { allUsers: true, idleConnections: false } },
        { $match: { secs_running: { $gt: 5 } } },
        { $sort: { secs_running: -1 } },
        { $limit: 20 }
    ]);
    """, database="admin"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 缺少索引 | 缺少索引导致全表扫描 |
| 索引错误 | 使用了错误的索引 |
| 大集合 | 数据量大 |
| 内存压力 | 内存不足 |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的操作

> **警告**：终止操作会导致当前任务失败，请在确认后执行！

```python
# 终止指定操作（请先确认 opId）
# 需要您确认后才能执行
toolbox.execute_sql(
    commands="""
    db.getSiblingDB('admin').killOp(<opId>);
    """, database="admin"
)
```

### 创建索引

> **警告**：创建索引可能影响写入性能，请在确认后执行！

```python
# 创建索引（请先确认集合和字段）
# 需要您确认后才能执行
toolbox.execute_sql(
    commands="""
    db.collection.createIndex({ field: 1 });
    """, database="admin"
)
```

## 预防措施

1. 定期审查慢查询日志
2. 根据查询模式添加适当索引
3. 使用 explain() 分析查询
4. 监控查询执行时间
5. 设置慢查询告警
6. 优化应用查询模式
