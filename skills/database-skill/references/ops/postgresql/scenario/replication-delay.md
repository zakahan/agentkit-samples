# 复制延迟故障排查

## 概述

复制延迟是指 PostgreSQL 主从复制过程中，从库的复制进度落后于主库，导致读写分离失效、数据不一致等问题。

## 典型症状

- 从库延迟持续增大
- 读写分离读到的数据过期
- `pg_stat_replication` 显示延迟
- 复制相关报错

## 排查步骤

### 步骤 1: 检查复制状态

```python
# 检查复制状态
toolbox.execute_sql(
    commands="""
    SELECT 
        pid,
        usename,
        client_addr,
        state,
        sync_state,
        write_lag,
        flush_lag,
        replay_lag
    FROM pg_stat_replication;
    """, database="postgres"
)
```

### 步骤 2: 检查复制槽

```python
# 检查复制槽
toolbox.execute_sql(
    commands="""
    SELECT 
        slot_name,
        plugin,
        slot_type,
        active,
        restart_lsn
    FROM pg_replication_slots;
    """, database="postgres"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 网络延迟 | 主从网络延迟 |
| 大事务 | 大事务复制时间长 |
| 慢查询 | 从库执行慢查询 |
| IO 瓶颈 | 从库磁盘 IO 瓶颈 |

## ⚠️ 应急处置（需确认后执行）

### 终止从库长查询

> **警告**：终止查询会导致当前事务失败，请在确认后执行！

```python
# 终止从库长查询
toolbox.execute_sql(
    commands="SELECT pg_terminate_backend(12345);", database="postgres"
)
```

## 预防措施

1. 使用流复制
2. 保持事务简短
3. 优化从库慢查询
4. 确保从库有足够资源
5. 监控复制延迟
6. 对关键数据使用同步复制
