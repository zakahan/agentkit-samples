# 锁等待故障排查

## 概述

锁等待是指事务由于无法获取所需的锁而处于等待状态，可能是由于行锁等待、表锁等待或元数据锁等待导致。

## 典型症状

- 查询执行变慢
- 特定操作被阻塞
- 锁等待时间增长
- `pg_stat_activity` 显示很多进程在等待

## 排查步骤

### 步骤 1: 检查锁等待

```python
# 获取当前锁等待
toolbox.execute_sql(
    commands="""
    SELECT 
        pid,
        usename,
        relname,
        mode,
        granted,
        grant_time,
        wait_start
    FROM pg_locks l
    JOIN pg_stat_activity a ON l.pid = a.pid
    WHERE NOT granted;
    """, database="postgres"
)
```

### 步骤 2: 检查阻塞查询

```python
# 查找阻塞查询
toolbox.execute_sql(
    commands="""
    SELECT 
        blocked_locks.pid AS blocked_pid,
        blocked_activity.usename AS blocked_user,
        blocking_locks.pid AS blocking_pid,
        blocking_activity.usename AS blocking_user
    FROM pg_catalog.pg_locks blocked_locks
    JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
    JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.pid != blocked_locks.pid
    JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
    WHERE NOT blocked_locks.granted;
    """, database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 长事务 | 事务过长，持有锁久 |
| 乱序访问 | 不同事务以不同顺序访问 |
| 缺少索引 | 缺少索引导致锁范围大 |
| DDL 操作 | ALTER/CREATE 等 DDL 操作 |

## ⚠️ 应急处置（需确认后执行）

### 终止阻塞事务

> **警告**：终止事务会导致当前事务失败，请在确认后执行！

```python
# 终止阻塞进程
toolbox.execute_sql(
    commands="SELECT pg_terminate_backend(12345);", database="postgres"
)
```

## 预防措施

1. 保持事务简短
2. 按一致顺序访问数据
3. 添加适当索引
4. 避免在高峰期进行长时间 DDL
5. 监控锁等待时间
6. 使用适当的锁模式
