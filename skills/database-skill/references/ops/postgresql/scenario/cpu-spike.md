# CPU 打满故障排查

## 概述

CPU 打满是指 PostgreSQL 实例的 CPU 使用率持续接近或达到 100%，导致数据库响应变慢或完全无响应。

## 典型症状

- CPU 使用率持续 100% 或接近 100%
- 数据库响应变慢，查询超时
- 连接堆积，新请求排队等待
- 系统负载高

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="Postgres"
)
```

### 步骤 1: 确认 CPU 使用率

```python
import time
now = int(time.time())

# 获取当前 CPU 使用率
toolbox.get_metric_data(
    metric_name="CpuUsage",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="pg-xxx",
    instance_type="Postgres"
)
```

### 步骤 2: 检查数据库连接

```python
# 查询活跃连接
toolbox.execute_sql(
    commands="SELECT count(*) FROM pg_stat_activity;", database="postgres"
)
```

### 步骤 3: 查找长时间运行的查询

```python
# 获取长时间运行的查询
toolbox.execute_sql(
    commands="""
    SELECT 
        pid,
        usename,
        query,
        state,
        wait_event_type,
        wait_event,
        duration
    FROM pg_stat_activity 
    WHERE state != 'idle'
    AND query_start < now() - interval '5 minutes';
    """, database="postgres"
)
```

### 步骤 4: 检查锁

```python
# 检查锁
toolbox.execute_sql(
    commands="""
    SELECT 
        pid,
        relname,
        mode,
        granted,
        duration
    FROM pg_locks l
    JOIN pg_stat_activity a ON l.pid = a.pid
    WHERE NOT granted;
    """, database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 复杂查询 | 复杂查询消耗 CPU |
| 缺少索引 | 缺少索引导致全表扫描 |
| 高并发 | 并发请求过多 |
| 大数据处理 | 大数据量处理 |
| 函数执行 | 自定义函数消耗 CPU |

## ⚠️ 应急处置（需确认后执行）

### 取消长时间运行的查询

> **警告**：取消查询会导致当前事务失败，请在确认后执行！

```python
# 取消指定查询
toolbox.execute_sql(
    commands="SELECT pg_cancel_backend(12345);", database="postgres"
)

# 终止后端
toolbox.execute_sql(
    commands="SELECT pg_terminate_backend(12345);", database="postgres"
)
```

### 终止空闲连接

> **警告**：终止连接会导致当前事务失败，请在确认后执行！

```python
toolbox.execute_sql(
    commands="""
    SELECT pg_terminate_backend(pid) 
    FROM pg_stat_activity 
    WHERE state = 'idle' 
    AND query_start < now() - interval '10 minutes';
    """, database="postgres"
)
```

## 预防措施

1. 添加适当的索引
2. 优化查询计划
3. 使用连接池（PgBouncer）
4. 监控长时间运行的查询
5. 设置资源限制
6. 定期统计信息收集（ANALYZE）
