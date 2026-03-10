# 会话堆积故障排查

## 概述

活跃会话堆积是指大量连接处于活跃状态（Sleep/Waiting），导致连接数资源耗尽，响应变慢。

## 典型症状

- 活跃连接数持续较高
- 很多连接处于 Sleep 状态
- 连接数接近上限
- 响应时间变长

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="MySQL"
)
```

### 步骤 1: 检查活跃会话

```python
import time
now = int(time.time())

# 获取活跃会话数
toolbox.get_metric_data(
    metric_name="ActiveSessions",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 步骤 2: 分析会话状态

```python
# 获取进程列表状态
toolbox.execute_sql(
    commands="""
    SELECT 
        STATE,
        COUNT(*) AS COUNT,
        SUM(TIME) AS TOTAL_TIME
    FROM information_schema.PROCESSLIST 
    GROUP BY STATE 
    ORDER BY COUNT DESC;
    """
)
```

### 步骤 3: 查找长时间运行的会话

```python
# 查找长时间运行的查询
toolbox.execute_sql(
    commands="""
    SELECT 
        ID,
        USER,
        HOST,
        DB,
        COMMAND,
        TIME,
        STATE,
        LEFT(INFO, 100) AS SQL_PREVIEW
    FROM information_schema.PROCESSLIST 
    WHERE TIME > 60
    ORDER BY TIME DESC;
    """
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 连接泄漏 | 应用未正确关闭连接 |
| 长查询 | 查询执行时间过长 |
| 网络问题 | 网络问题导致连接断开慢 |
| 应用 Bug | 应用逻辑问题 |
| 连接池配置不当 | 连接池配置不当 |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的查询

> **警告**：终止会话会导致当前事务失败，请在确认后执行！

```python
# 终止问题会话
toolbox.kill_process(
    process_ids=["12345", "12346"],
    node_id="node-1",
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 调整超时设置

> **警告**：修改参数可能影响业务，请在确认后执行！

```python
# 减少 wait_timeout
toolbox.execute_sql(
    commands="SET GLOBAL wait_timeout = 600;"
)
```

## 预防措施

1. 使用正确的连接池
2. 设置适当的超时值
3. 监控连接状态
4. 实现连接生命周期管理
5. 设置连接数告警
6. 审查应用连接代码
