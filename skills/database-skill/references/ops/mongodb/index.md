---
name: "mongodb-ops"
description: "MongoDB 故障排查指南"
---

# MongoDB 故障排查

## 选择故障场景

### P0 - 紧急故障（需立即处理）

| 场景 | 描述 | 优先级 |
|----------|-------------|----------|
| [连接数打满](scenario/connection-full.md) | 连接数达到上限 | P0 |
| [磁盘空间不足](scenario/disk-full.md) | 磁盘空间耗尽 | P0 |

### P1 - 高优先级故障

| 场景 | 描述 | 优先级 |
|----------|-------------|----------|
| [慢查询](scenario/slow-query.md) | 查询性能问题 | P1 |
| [内存压力](scenario/memory-pressure.md) | WiredTiger 缓存压力 | P1 |
| [复制延迟](scenario/replication-delay.md) | 副本集延迟 | P1 |
| [锁等待](scenario/lock-wait.md) | 数据库/集合锁 | P1 |

### P2 - 中优先级故障

| 场景 | 描述 | 优先级 |
|----------|-------------|----------|
| [连接泄漏](scenario/connection-leak.md) | 连接泄漏 | P2 |
| [集群故障](scenario/cluster-failure.md) | 分片集群问题 | P2 |

---

## 常用工具

```python
from scripts.toolbox import DatabaseToolbox
toolbox = DatabaseToolbox()
```

## 相关资源

- [总故障排查入口](../index.md) - 返回主索引
