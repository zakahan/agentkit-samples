# CPU 打满故障排查

## 概述

CPU 打满是指 MySQL 实例的 CPU 使用率持续接近或达到 100%，导致数据库响应变慢或完全无响应。这是生产环境中常见的高优先级故障。

## 典型症状

- CPU 使用率持续 100% 或接近 100%
- 数据库响应变慢，查询超时
- 连接堆积，新请求排队等待
- `top` 或监控显示 MySQL 进程 CPU 占用高

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="MySQL"
)
```

### 步骤 1: 确认 CPU 使用率

```python
import time
now = int(time.time())

# 获取当前 CPU 使用率
toolbox.get_metric_data(
    metric_name="CpuUsage",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 步骤 2: 检查 QPS/TPS 趋势

```python
# 获取 QPS
toolbox.get_metric_data(
    metric_name="QPS",
    period=60,
    start_time=now - 3600,
    end_time=now,
    instance_id="mysql-xxx",
    instance_type="MySQL"
)

# 获取 TPS
toolbox.get_metric_data(
    metric_name="TPS",
    period=60,
    start_time=now - 3600,
    end_time=now,
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 步骤 3: 识别活跃会话

```python
# 查询当前会话
toolbox.execute_sql(
    commands="SHOW PROCESSLIST;"
)
```

### 步骤 4: 分析慢查询

```python
# 获取慢查询（按执行时间排序）
toolbox.describe_slow_logs(
    start_time=now - 1800,
    end_time=now,
    order_by="QueryTime",
    sort_by="DESC"
)
```

### 步骤 5: 检查锁等待

```python
# 检查 InnoDB 事务
toolbox.execute_sql(
    commands="SELECT * FROM information_schema.INNODB_TRX WHERE trx_state = 'RUNNING';"
)

# 检查锁等待
toolbox.execute_sql(
    commands="SELECT * FROM information_schema.INNODB_LOCK_WAITS;"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 慢查询 | 缺少索引或 SQL 写法问题导致全表扫描 |
| 高并发 | 突发流量激增 |
| 锁竞争 | 行锁等待导致线程堆积 |
| 全表扫描 | 查询未命中索引 |
| IO 瓶颈 | IO 等待导致 CPU 空转 |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的查询

> **警告**：终止进程会导致当前查询失败，请在确认后执行！

```python
# 查找并终止问题进程
toolbox.kill_process(
    process_ids=["12345"],
    node_id="node-1",
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 调整参数

> **警告**：修改参数可能影响业务，请在确认后执行！

```python
# 临时减少最大连接数
toolbox.execute_sql(
    commands="SET GLOBAL max_connections = 100;"
)
```

## 预防措施

1. 优化慢查询，添加合适的索引
2. 正确配置连接池
3. 监控 CPU 使用率并设置告警
4. 定期审查 SQL 执行计划
5. 设置查询超时
