# Binlog 延迟故障排查

## 概述

Binlog 延迟是指主库产生的二进制日志（Binlog）未及时传输到从库或从库未及时应用，导致主从数据不一致、复制延迟。

## 典型症状

- 从库延迟增大
- `SHOW SLAVE STATUS` 显示 `Seconds_Behind_Master` > 0
- Binlog 积压
- 复制链路延迟

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

### 步骤 2: 检查 Binary Log 状态

```python
# 获取 binary log 信息
toolbox.execute_sql(
    commands="SHOW MASTER STATUS;"
)
toolbox.execute_sql(
    commands="SHOW BINARY LOGS;"
)
```

### 步骤 3: 检查 Binlog 增长速度

```python
import time
now = int(time.time())

# 监控 binlog 大小趋势
toolbox.get_metric_data(
    metric_name="BinlogSize",
    period=300,
    start_time=now - 86400,
    end_time=now,
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 大事务 | 大事务导致 binlog 传输慢 |
| 网络延迟 | 主从网络延迟 |
| 磁盘 IO 慢 | 从库磁盘 IO 慢 |
| 从库负载 | 从库负载过高 |
| Binlog 格式 | Binlog 格式问题 |

## ⚠️ 应急处置（需确认后执行）

### 清理旧 Binlog

> **警告**：清理 binlog 可能影响数据恢复能力，请在确认后执行！

```python
# 清理旧的 binlog
toolbox.execute_sql(
    commands="PURGE BINARY LOGS BEFORE DATE_SUB(NOW(), INTERVAL 1 DAY);"
)
```

### 跳过一步事件

> **警告**：跳过事件可能导致数据不一致，请在确认后执行！

```python
# 跳过一个事件
toolbox.execute_sql(
    commands="SET GLOBAL sql_slave_skip_counter = 1;"
)
```

### 重启复制

> **警告**：重启复制会中断当前复制，请在确认后执行！

```python
# 重启从库
toolbox.execute_sql(
    commands="STOP SLAVE; START SLAVE;"
)
```

## 预防措施

1. 使用 ROW 格式进行复制
2. 保持事务简短
3. 确保从库有足够资源
4. 监控 binlog 增长速度
5. 使用半同步复制
6. 设置复制延迟监控告警
