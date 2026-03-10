# 磁盘空间不足故障排查

## 概述

磁盘空间不足是指 MongoDB 实例的磁盘使用率达到 100% 或接近上限，导致无法写入数据、无法创建索引、WiredTiger 无法 checkpoint。

## 典型症状

- 磁盘使用率 100% 或接近 100%
- 写入数据报错
- 无法创建索引
- WiredTiger checkpoint 失败

## 排查步骤

### 步骤 0: 获取支持的监控指标（推荐先执行）

> **提示**：在获取具体指标数据之前，建议先调用 `get_metric_items` 查看当前实例支持哪些指标，然后选择合适的指标进行获取。

```python
# 获取当前实例支持的监控指标列表
toolbox.get_metric_items(
    instance_type="Mongo"
)
```

### 步骤 1: 检查磁盘使用率

```python
import time
now = int(time.time())

# 获取磁盘使用率
toolbox.get_metric_data(
    metric_name="DiskUsage",
    period=60,
    start_time=now - 300,
    end_time=now,
    instance_id="mongo-xxx",
    instance_type="Mongo"
)
```

### 步骤 2: 获取 MongoDB 存储容量

```python
# 获取存储容量
toolbox.describe_mongo_storage_capacity(
    instance_id="mongo-xxx",
    instance_type="Mongo"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 数据增长 | 数据快速增长，未及时清理 |
| 索引增长 | 索引过大 |
| WiredTiger Cache | WiredTiger 缓存过大 |
| Oplog 增长 | oplog 过大 |

## ⚠️ 应急处置（需确认后执行）

### 压缩集合

> **警告**：压缩操作会锁定集合，请在确认后执行！

```python
# 压缩集合
toolbox.execute_sql(
    commands="""
    db.collection.runCommand("compact");
    """, database="admin"
)
```

## 预防措施

1. 设置磁盘使用率监控和告警
2. 实施数据归档和清理策略
3. 监控集合大小
4. 使用 TTL 索引自动清理
5. 定期压缩
6. 设置空间使用预测
