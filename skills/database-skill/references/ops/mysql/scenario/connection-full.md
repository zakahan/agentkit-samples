# 连接数打满故障排查

## 概述

连接数打满是指 MySQL 实例的当前连接数达到 `max_connections` 上限，导致新请求无法建立连接，出现 `Too many connections` 错误。

## 典型症状

- 应用报错: `Too many connections`
- 无法建立新的数据库连接
- 连接数监控显示达到上限
- 旧连接未被释放，堆积

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="MySQL"
)
```

### 步骤 1: 检查当前连接数

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

### 步骤 2: 检查 max_connections 设置

```python
# 获取 max_connections 值
toolbox.execute_sql(
    commands="SHOW VARIABLES LIKE 'max_connections';"
)
```

### 步骤 3: 分析连接状态

```python
# 获取详细进程列表
toolbox.execute_sql(
    commands="""
    SELECT 
        COMMAND,
        COUNT(*) AS COUNT,
        STATE,
        USER
    FROM information_schema.PROCESSLIST 
    GROUP BY COMMAND, STATE, USER 
    ORDER BY COUNT DESC;
    """
)
```

### 步骤 4: 识别空闲连接

```python
# 查找长时间空闲的连接
toolbox.execute_sql(
    commands="""
    SELECT 
        ID,
        USER,
        HOST,
        DB,
        COMMAND,
        TIME,
        STATE
    FROM information_schema.PROCESSLIST 
    WHERE COMMAND = 'Sleep' AND TIME > 60
    ORDER BY TIME DESC;
    """
)
```

### 步骤 5: 检查应用连接泄漏

```python
# 检查连接生命周期
toolbox.execute_sql(
    commands="""
    SELECT 
        USER,
        HOST,
        COUNT(*) AS CONN_COUNT,
        MAX(TIME) AS MAX_TIME
    FROM information_schema.PROCESSLIST 
    GROUP BY USER, HOST
    ORDER BY CONN_COUNT DESC;
    """
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 连接泄漏 | 应用未正确关闭数据库连接 |
| 连接过多 | 并发请求过多，连接池配置不当 |
| 长查询 | 查询耗时过长，占用连接 |
| 空闲连接 | 长时间空闲的 Sleep 连接未释放 |
| 应用 Bug | 连接未正确释放 |

## ⚠️ 应急处置（需确认后执行）

### 终止空闲连接

> **警告**：终止连接会导致当前事务失败，请在确认后执行！

```python
# 终止指定的空闲进程
toolbox.kill_process(
    process_ids=["12345", "12346"],
    node_id="node-1",
    instance_id="mysql-xxx",
    instance_type="MySQL"
)
```

### 增加 max_connections

> **警告**：修改参数可能影响业务，请在确认后执行！

```python
# 临时增加连接数限制（生产环境不推荐）
toolbox.execute_sql(
    commands="SET GLOBAL max_connections = 2000;"
)
```

### 刷新主机缓存

```python
toolbox.execute_sql(
    commands="FLUSH HOSTS;"
)
```

## 预防措施

1. 使用正确的连接池（HikariCP, Druid 等）
2. 设置适当的连接超时
3. 监控并终止长时间空闲的连接
4. 设置连接数告警
5. 审查应用连接生命周期
6. 配置 `wait_timeout` 和 `interactive_timeout`
