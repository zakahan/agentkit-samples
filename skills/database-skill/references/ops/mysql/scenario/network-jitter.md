# 网络抖动故障排查

## 概述

网络抖动是指网络延迟不稳定或丢包，导致数据库连接超时、响应时间波动、数据传输中断等问题。

## 典型症状

- 连接超时错误
- 响应时间波动大
- 连接断开重连
- 网络延迟监控显示抖动

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="MySQL"
)
```

### 步骤 1: 检查网络指标

```python
import time
now = int(time.time())

# 获取网络流量
toolbox.get_metric_data(
    metric_name="NetworkIn",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
    instance_type="MySQL"
)

toolbox.get_metric_data(
    metric_name="NetworkOut",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 步骤 2: 检查连接错误

```python
# 检查连接错误
toolbox.execute_sql(
    commands="""
    SHOW GLOBAL STATUS LIKE 'Aborted%';
    """
)

# 检查连接统计
toolbox.execute_sql(
    commands="""
    SHOW GLOBAL STATUS LIKE 'Connection%';
    """
)
```

### 步骤 3: 检查异常状态连接

```python
# 检查处于异常状态的连接
toolbox.execute_sql(
    commands="""
    SELECT 
        STATE,
        COUNT(*) AS COUNT
    FROM information_schema.PROCESSLIST 
    WHERE STATE LIKE '%Timeout%' 
    OR STATE LIKE '%Disconnect%'
    GROUP BY STATE;
    """
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 网络拥塞 | 网络拥塞 |
| 硬件问题 | 网卡/交换机故障 |
| DNS 问题 | DNS 解析问题 |
| 防火墙 | 防火墙规则变化 |
| 高延迟 | 网络延迟高 |

## ⚠️ 应急处置（需确认后执行）

### 增加超时设置

> **警告**：修改参数可能影响业务，请在确认后执行！

```python
# 增加连接超时
toolbox.execute_sql(
    commands="SET GLOBAL connect_timeout = 20;"
)

# 增加等待超时
toolbox.execute_sql(
    commands="SET GLOBAL wait_timeout = 600;"
)
```

### 使用 IP 而非主机名

```python
# 配置连接使用 IP 而非主机名
# 更新应用连接字符串
```

## 预防措施

1. 使用稳定的网络基础设施
2. 监控网络指标
3. 设置适当的超时值
4. 使用连接池
5. 在应用中实现重试逻辑
6. 设置网络告警
