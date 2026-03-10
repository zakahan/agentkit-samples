# 主从延迟故障排查

## 概述

主从延迟是指 MySQL 主从复制过程中，从库的复制进度落后于主库，导致读写分离失效、数据不一致等问题。

## 典型症状

- 从库延迟持续增大
- 读写分离读到的数据过期
- `SHOW SLAVE STATUS` 显示 `Seconds_Behind_Master` > 0
- 复制相关报错

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="MySQL"
)
```

### 步骤 1: 检查复制状态

```python
# 检查从库状态
toolbox.execute_sql(
    commands="SHOW SLAVE STATUS\G"
)
```

### 步骤 2: 获取复制指标

```python
# 检查延迟指标
toolbox.get_metric_data(
    metric_name="SlaveLag",
    period=60,
    start_time=now - 3600,
    end_time=now,
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 步骤 3: 检查主库 Binlog 状态

```python
# 检查 binary log 位置
toolbox.execute_sql(
    commands="SHOW MASTER STATUS;"
)
```

### 步骤 4: 分析从库慢查询

```python
# 检查从库慢查询
toolbox.describe_slow_logs(
    start_time=now - 1800,
    end_time=now,
    order_by="QueryTime",
    sort_by="DESC"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 网络延迟 | 主从网络延迟 |
| 大事务 | 大事务复制时间长 |
| 慢查询 | 从库执行慢查询 |
| IO 瓶颈 | 从库磁盘 IO 瓶颈 |
| Binlog 格式 | Binlog 格式问题 |

## ⚠️ 应急处置（需确认后执行）

### 跳过一步事务

> **警告**：跳过事务可能导致数据不一致，请在确认后执行！

```python
# 跳过一个事件
toolbox.execute_sql(
    commands="SET GLOBAL sql_slave_skip_counter = 1;"
)
```

### 重启从库

> **警告**：重启从库会中断复制，请在确认后执行！

```python
# 停止并启动从库
toolbox.execute_sql(
    commands="STOP SLAVE;"
)
toolbox.execute_sql(
    commands="START SLAVE;"
)
```

## 预防措施

1. 使用行格式复制 (ROW)
2. 保持事务简短
3. 优化从库慢查询
4. 确保从库有足够资源
5. 监控复制延迟
6. 使用半同步复制
