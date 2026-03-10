# 慢查询故障排查

## 概述

慢查询是指执行时间较长的 SQL 语句，可能是由于缺少索引、统计信息过期、数据量过大等原因导致。

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
    instance_id="pg-xxx",
    instance_type="Postgres",
    interval=300
)
```

### 步骤 2: 获取慢查询聚合统计

```python
# 获取慢查询聚合统计（按 SQL 模板聚合，找出最耗时的 SQL 类型）
toolbox.describe_aggregate_slow_logs(
    start_time=now - 3600,
    end_time=now,
    instance_id="pg-xxx",
    instance_type="Postgres",
    order_by="TotalQueryTime",
    sort_by="DESC"
)
```

### 步骤 3: 获取慢查询明细

```python
# 获取慢查询明细（查看具体哪些 SQL 最慢）
toolbox.describe_slow_logs(
    start_time=now - 3600,
    end_time=now,
    order_by="QueryTime",
    sort_by="DESC"
)
```

### 步骤 4: 获取完整 SQL 历史

```python
# 获取完整 SQL 历史详情（包含执行计划等详细信息）
toolbox.describe_full_sql_detail(
    start_time=now - 3600,
    end_time=now,
    instance_id="pg-xxx",
    instance_type="Postgres",
    page_size=20
)
```

### 步骤 5: 检查查询统计

```python
# 获取查询统计
toolbox.execute_sql(
    commands="""
    SELECT 
        query,
        calls,
        total_exec_time,
        mean_exec_time,
        max_exec_time,
        rows,
        shared_blks_hit,
        shared_blks_read
    FROM pg_stat_statements 
    ORDER BY total_exec_time DESC 
    LIMIT 20;
    """, database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 缺少索引 | 缺少索引导致全表扫描 |
| 统计信息过期 | 统计信息过期 |
| 复杂 JOIN | 多表 JOIN 复杂 |
| 大表扫描 | 数据量大 |
| 锁等待 | 锁等待 |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的查询

> **警告**：终止查询会导致当前事务失败，请在确认后执行！

```python
# 终止长查询（请先确认要终止的 PID）
# 需要您确认后才能执行
toolbox.execute_sql(
    commands="SELECT pg_terminate_backend(12345);", database="postgres"
)
```

### 添加索引

> **警告**：添加索引可能影响写入性能，请在确认后执行！

```python
# 添加索引（请先确认表名和字段）
# 需要您确认后才能执行
toolbox.execute_sql(
    commands="CREATE INDEX idx_column ON table_name (column);", database="postgres"
)
```

## 预防措施

1. 定期审查慢查询日志
2. 添加适当的索引
3. 保持统计信息更新（ANALYZE）
4. 使用 EXPLAIN 分析查询计划
5. 设置慢查询告警
6. 优化应用 SQL 模式
