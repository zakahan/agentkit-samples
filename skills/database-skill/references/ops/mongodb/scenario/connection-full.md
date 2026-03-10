# 连接数打满故障排查

## 概述

连接数打满是指 MongoDB 实例的当前连接数达到上限，导致新请求无法建立连接，出现连接错误。

## 典型症状

- 应用报错: `too many connections`
- 无法建立新的数据库连接
- 连接数监控显示达到上限
- 旧连接未被释放，堆积

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="Mongo"
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
    instance_id="mongo-xxx",
    instance_type="Mongo"
)
```

### 步骤 2: 获取连接统计

```python
# 获取连接统计
toolbox.execute_sql(
    commands="db.serverStatus().connections;", database="admin"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 连接泄漏 | 应用未正确关闭数据库连接 |
| 连接过多 | 并发请求过多，连接池配置不当 |
| 长运行操作 | 操作耗时过长，占用连接 |
| 应用 Bug | 连接未正确释放 |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的操作

> **警告**：终止操作会导致当前任务失败，请在确认后执行！

```python
# 终止指定操作
toolbox.execute_sql(
    commands="""
    db.getSiblingDB('admin').killOp(<opId>);
    """, database="admin"
)
```

## 预防措施

1. 使用正确的连接池（MongoClient 设置）
2. 设置适当的连接超时
3. 监控并终止长时间空闲的连接
4. 设置连接数告警
5. 审查应用连接生命周期
6. 适当配置 `maxIncomingConnections`
