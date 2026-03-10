# 死锁故障排查

## 概述

死锁是指两个或多个事务相互持有对方需要的锁，导致所有事务都无法继续执行。MySQL 会自动检测并回滚其中一个事务，但会造成业务报错。

## 典型症状

- 应用报错: `Deadlock found when trying to get lock`
- 事务回滚
- 特定业务操作失败
- 死锁错误日志

## 排查步骤

### 步骤 1: 查看最近的死锁

```python
# 获取死锁信息
toolbox.describe_deadlock(
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 步骤 2: 检查锁等待

```python
# 获取当前锁等待
toolbox.execute_sql(
    commands="SELECT * FROM information_schema.INNODB_LOCK_WAITS;"
)

# 获取当前锁
toolbox.execute_sql(
    commands="SELECT * FROM information_schema.INNODB_LOCKS;"
)
```

### 步骤 3: 检查运行中的事务

```python
# 获取运行中的事务
toolbox.execute_sql(
    commands="""
    SELECT 
        trx_id,
        trx_state,
        trx_started,
        trx_wait_started,
        trx_mysql_thread_id,
        trx_query
    FROM information_schema.INNODB_TRX
    WHERE trx_state = 'LOCK WAIT';
    """
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 乱序访问 | 不同事务以不同顺序访问资源 |
| 长事务 | 事务过长，持有锁时间久 |
| 批量更新 | 批量更新相同范围数据 |
| 缺少索引 | 缺少索引导致锁范围扩大 |
| 高并发 | 并发更新同一行数据 |

## ⚠️ 应急处置（需确认后执行）

### 终止阻塞事务

> **警告**：终止事务会导致当前事务失败，请在确认后执行！

```python
# 终止指定事务
toolbox.kill_process(
    process_ids=["12345"],
    node_id="node-1",
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 设置较低的事务隔离级别

> **警告**：修改参数可能影响业务，请在确认后执行！

```python
# 使用 READ COMMITTED 替代 REPEATABLE READ
toolbox.execute_sql(
    commands="SET GLOBAL transaction_isolation = 'READ-COMMITTED';"
)
```

## 预防措施

1. 按一致顺序访问表
2. 保持事务简短
3. 添加适当索引以缩小锁范围
4. 适当情况下使用较低隔离级别
5. 避免在高峰期进行批量更新
6. 监控死锁日志并优化问题查询
