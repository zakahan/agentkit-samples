# 连接数打满故障排查

## 概述

连接数打满是指 PostgreSQL 实例的当前连接数达到 `max_connections` 上限，导致新请求无法建立连接，出现 `sorry, too many clients already` 错误。

## 典型症状

- 应用报错: `sorry, too many clients already`
- 无法建立新的数据库连接
- 连接数监控显示达到上限
- 旧连接未被释放，堆积

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="Postgres"
)
```

### 步骤 1: 检查当前连接数

```python
import time
now = int(time.time())

# 获取活跃会话数
toolbox.get_metric_data(
    metric_name="ActiveSessions",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="pg-xxx",
    instance_type="Postgres"
)
```

### 步骤 2: 检查 max_connections 设置

```python
# 获取 max_connections 值
toolbox.execute_sql(
    commands="SHOW max_connections;", database="postgres"
)
```

### 步骤 3: 分析连接状态

```python
# 获取详细连接信息
toolbox.execute_sql(
    commands="""
    SELECT 
        state,
        COUNT(*) AS count,
        usename
    FROM pg_stat_activity 
    GROUP BY state, usename 
    ORDER BY count DESC;
    """, database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 连接泄漏 | 应用未正确关闭数据库连接 |
| 连接过多 | 并发请求过多，连接池配置不当 |
| 长查询 | 查询耗时过长 |
| 空闲连接 | 长时间空闲的连接未释放 |

## ⚠️ 应急处置（需确认后执行）

### 终止空闲连接

> **警告**：终止连接会导致当前事务失败，请在确认后执行！

```python
# 终止空闲连接
toolbox.execute_sql(
    commands="""
    SELECT pg_terminate_backend(pid) 
    FROM pg_stat_activity 
    WHERE state = 'idle' 
    AND query_start < now() - interval '5 minutes';
    """, database="postgres"
)
```

### 终止特定后端

> **警告**：终止后端会导致当前事务失败，请在确认后执行！

```python
toolbox.execute_sql(
    commands="SELECT pg_terminate_backend(12345);", database="postgres"
)
```

## 预防措施

1. 使用正确的连接池（PgBouncer, Pgpool-II）
2. 设置适当的连接超时
3. 监控并终止长时间空闲的连接
4. 设置连接数告警
5. 审查应用连接生命周期
6. 配置 `idle_in_transaction_session_timeout`
