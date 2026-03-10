# 锁等待故障排查

## 概述

锁等待是指事务由于无法获取所需的锁而处于等待状态，可能是由于行锁等待、表锁等待或元数据锁等待导致。

## 典型症状

- 查询执行变慢
- 特定操作被阻塞
- 锁等待时间增长
- `SHOW PROCESSLIST` 显示很多 State 为 "Waiting for ..."

## 排查步骤

### 步骤 1: 检查锁等待

```python
# 获取锁等待
toolbox.describe_trx_and_locks(
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 步骤 2: 获取详细锁分析

```python
# 分析事务和锁关系
toolbox.analyze_trx_and_lock(instance_id="mysql-xxx")
```

### 步骤 3: 检查 InnoDB 锁等待

```python
# 获取 InnoDB 锁等待
toolbox.execute_sql(
    commands="SELECT * FROM information_schema.INNODB_LOCK_WAITS;"
)
```

### 步骤 4: 检查 InnoDB 锁

```python
# 获取 InnoDB 锁
toolbox.execute_sql(
    commands="SELECT * FROM information_schema.INNODB_LOCKS;"
)
```

### 步骤 5: 检查运行中的事务

```python
# 获取运行中的事务
toolbox.execute_sql(
    commands="SELECT * FROM information_schema.INNODB_TRX;"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 长事务 | 事务过长，持有锁久 |
| 乱序访问 | 不同事务以不同顺序访问 |
| 缺少索引 | 缺少索引导致锁范围大 |
| DDL 操作 | ALTER/CREATE 等 DDL 操作 |
| 批量更新 | 批量更新同一范围数据 |

## ⚠️ 应急处置（需确认后执行）

### 终止阻塞事务

> **警告**：终止事务会导致当前事务失败，请在确认后执行！

```python
# 终止阻塞进程
toolbox.kill_process(
    process_ids=["12345"],
    node_id="node-1",
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 设置较低隔离级别

> **警告**：修改参数可能影响业务，请在确认后执行！

```python
# 使用 READ COMMITTED
toolbox.execute_sql(
    commands="SET GLOBAL transaction_isolation = 'READ-COMMITTED';"
)
```

## 预防措施

1. 保持事务简短
2. 按一致顺序访问数据
3. 添加适当索引
4. 避免在高峰期进行长时间 DDL
5. 监控锁等待时间
6. 使用适当的隔离级别
