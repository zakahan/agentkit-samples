# 磁盘空间不足故障排查

## 概述

磁盘空间不足是指 PostgreSQL 实例的磁盘使用率达到 100% 或接近上限，导致无法写入数据、无法创建索引、WAL 无法写入。

## 典型症状

- 磁盘使用率 100% 或接近 100%
- 写入数据报错
- DDL 操作失败
- WAL 无法写入

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="Postgres"
)
```

### 步骤 1: 检查磁盘使用率

```python
import time
now = int(time.time())

# 获取磁盘使用率
toolbox.get_metric_data(
    metric_name="DiskUsage",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="pg-xxx",
    instance_type="Postgres"
)
```

### 步骤 2: 查找大表

```python
# 获取空间占用 Top 表
toolbox.describe_space_top(
    region_id="cn-beijing",
    instance_id="pg-xxx",
    instance_type="Postgres",
    limit=20
)
```

### 步骤 3: 检查 WAL 使用情况

```python
# 检查 WAL 目录大小
toolbox.execute_sql(
    commands="""
    SELECT 
        pg_current_wal_lsn(),
        pg_walfile_name(pg_current_wal_lsn()),
        pg_wal_lsn_diff(pg_current_wal_lsn(), '0/0') AS wal_used;
    """, database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 数据增长 | 数据快速增长，未及时清理 |
| WAL 累积 | WAL 日志积压 |
| 索引膨胀 | 索引膨胀 |
| 临时表 | 临时表占用空间 |
| VACUUM 未完成 | VACUUM 未完成 |

## ⚠️ 应急处置（需确认后执行）

### 回收空间

> **警告**：VACUUM 会锁定表，请在确认后执行！

```python
# 回收空间
toolbox.execute_sql(
    commands="VACUUM (VERBOSE, ANALYZE);", database="postgres"
)

# 完整 vacuum（会锁定表）
toolbox.execute_sql(
    commands="VACUUM FULL (VERBOSE);", database="postgres"
)
```

### 删除旧数据

> **警告**：删除数据可能无法恢复，请在确认后执行！

```python
# 归档或删除旧数据
toolbox.execute_sql(
    commands="DELETE FROM logs WHERE created_at < '2023-01-01';", database="postgres"
)
```

## 预防措施

1. 设置磁盘使用率监控和告警
2. 实施数据归档和清理策略
3. 定期 VACUUM（启用 AUTOVACUUM）
4. 监控 WAL 增长
5. 使用表分区
6. 设置空间使用预测
