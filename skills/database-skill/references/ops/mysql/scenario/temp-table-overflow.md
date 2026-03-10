# 临时表溢出故障排查

## 概述

临时表溢出是指由于排序或分组操作产生的数据无法完全在内存中完成，导致使用磁盘临时表（MyISAM 临时表或 InnoDB 内部临时表），性能下降。

## 典型症状

- 磁盘临时表使用增多
- 查询执行时间变长
- `Created_tmp_disk_tables` 变量增大
- 性能下降

## 排查步骤

### 步骤 1: 检查临时表统计

```python
# 获取临时表统计
toolbox.execute_sql(
    commands="""
    SHOW GLOBAL STATUS LIKE 'Created_tmp%';
    """
)

# 获取排序统计
toolbox.execute_sql(
    commands="""
    SHOW GLOBAL STATUS LIKE 'Sort%';
    """
)
```

### 步骤 2: 检查 tmp_table_size 和 max_heap_table_size

```python
# 检查临时表大小限制
toolbox.execute_sql(
    commands="SHOW VARIABLES LIKE 'tmp_table_size';"
)
toolbox.execute_sql(
    commands="SHOW VARIABLES LIKE 'max_heap_table_size';"
)
```

### 步骤 3: 识别使用临时表的查询

```python
# 查找可能使用临时表的查询
toolbox.execute_sql(
    commands="""
    SELECT 
        SQL_NO_CACHE,
        COUNT(*) AS cnt,
        SUM(ROWS_EXAMINED) AS rows_scanned
    FROM information_schema.PROCESSLIST 
    WHERE INFO LIKE '%GROUP BY%' 
    OR INFO LIKE '%ORDER BY%'
    GROUP BY LEFT(INFO, 50);
    """
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| tmp_table_size 太小 | 内存临时表大小限制过小 |
| 结果集过大 | 查询返回结果集过大 |
| 复杂 GROUP/ORDER BY | 复杂分组/排序无法在内存完成 |
| LOB 数据 | 包含大字段类型 |
| 无合适索引 | 缺少索引导致 filesort |

## ⚠️ 应急处置（需确认后执行）

### 增加 tmp_table_size

> **警告**：修改参数可能影响内存使用，请在确认后执行！

```python
# 增加临时表大小
toolbox.execute_sql(
    commands="SET GLOBAL tmp_table_size = 256 * 1024 * 1024;"
)
```

### 优化查询

> **警告**：添加索引可能影响写入性能，请在确认后执行！

```python
# 添加索引以避免 filesort
toolbox.execute_sql(
    commands="ALTER TABLE table_name ADD INDEX idx_column (column);"
)
```

## 预防措施

1. 正确配置 tmp_table_size 和 max_heap_table_size
2. 添加适当索引以避免 filesort
3. 优化查询以减少结果集大小
4. 监控临时表使用情况
5. 使用适当的数据类型
6. 审查慢查询日志中的临时表使用
