# 磁盘空间不足故障排查

## 概述

磁盘空间不足是指 MySQL 实例的磁盘使用率达到 100% 或接近上限，导致无法写入数据、无法创建索引、无法执行 DDL 操作。

## 典型症状

- 磁盘使用率 100% 或接近 100%
- 写入数据报错: `Disk full`
- DDL 操作失败: `Table 'xxx' is full`
- Binlog 无法写入
- InnoDB 无法 checkpoint

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="MySQL"
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
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 步骤 2: 查找大表

```python
# 获取空间占用 Top 表
toolbox.describe_space_top(
    region_id="cn-beijing",
    instance_id="mysql-xxx",
    instance_type="ByteRDS",
    limit=20
)
```

### 步骤 3: 分析表空间

```python
# 获取详细表空间信息
toolbox.describe_table_space(
    database="db_name",
    table_name="table_name",
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 步骤 4: 检查 Binlog 使用情况

```python
# 检查 binlog 使用情况
toolbox.execute_sql(
    commands="SHOW BINARY LOGS;"
)

# 检查 binlog 大小
toolbox.execute_sql(
    commands="""
    SELECT 
        log_name,
        file_size,
        (SELECT SUM(file_size) FROM mysql.bbinlog_files) AS total_size
    FROM mysql.bbinlog_files 
    ORDER BY log_name;
    """
)
```

### 步骤 5: 检查 InnoDB 表空间

```python
# 检查 InnoDB 文件大小
toolbox.execute_sql(
    commands="""
    SELECT 
        FILE_NAME,
        TABLESPACE_NAME,
        INITIAL_SIZE,
        TOTAL_EXTENTS * EXTENT_SIZE AS TOTAL_SIZE
    FROM information_schema.FILES
    WHERE FILE_TYPE = 'TABLESPACE';
    """
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 数据增长 | 数据快速增长，未及时清理 |
| Binlog 累积 | Binlog 未清理，磁盘占满 |
| 临时表 | 临时表/排序文件占用空间 |
| Undo/Redo | Undo/Redo 日志过大 |
| 慢查询 | 大排序操作产生临时文件 |

## ⚠️ 应急处置（需确认后执行）

### 清理 Binlog

> **警告**：清理 binlog 可能影响数据恢复能力，请在确认后执行！

```python
# 清理指定时间之前的 binlog
toolbox.execute_sql(
    commands="PURGE BINARY LOGS BEFORE '2024-01-01 00:00:00';"
)

# 清理到指定的 binlog 文件
toolbox.execute_sql(
    commands="PURGE BINARY LOGS TO 'mysql-bin.000010';"
)
```

### 删除旧数据

> **警告**：删除数据可能无法恢复，请在确认后执行！

```python
# 归档或删除旧数据
toolbox.execute_sql(
    commands="DELETE FROM logs WHERE created_at < '2023-01-01';"
)
```

### 删除未使用的索引

> **警告**：删除索引可能影响查询性能，请在确认后执行！

```python
# 检查未使用的索引
toolbox.execute_sql(
    commands="""
    SELECT 
        OBJECT_SCHEMA,
        OBJECT_NAME,
        INDEX_NAME
    FROM performance_schema.table_io_waits_summary_by_index_usage
    WHERE INDEX_NAME IS NOT NULL
    AND COUNT_STAR = 0
    AND OBJECT_SCHEMA != 'mysql';
    """
)
```

## 预防措施

1. 设置磁盘使用率监控和告警
2. 实施数据归档和清理策略
3. 配置 binlog 过期（binlog_expire_logs_seconds）
4. 定期表优化（OPTIMIZE TABLE）
5. 监控临时表使用情况
6. 设置空间使用预测
