---
name: "postgresql-ops"
description: "PostgreSQL / PostgreSQL 兼容引擎故障排查指南"
---

# PostgreSQL / PostgreSQL 兼容引擎故障排查

适用于 PostgreSQL 及所有 PostgreSQL 兼容数据库引擎。

## 选择故障场景

### P0 - 紧急故障（需立即处理）

| 场景 | 描述 | 优先级 |
|----------|-------------|----------|
| [CPU 打满](scenario/cpu-spike.md) | CPU 使用率过高，系统无响应 | P0 |
| [连接数打满](scenario/connection-full.md) | 连接数达到上限 | P0 |
| [磁盘空间不足](scenario/disk-full.md) | 磁盘空间耗尽 | P0 |

### P1 - 高优先级故障

| 场景 | 描述 | 优先级 |
|----------|-------------|----------|
| [慢查询](scenario/slow-query.md) | 查询性能问题 | P1 |
| [锁等待](scenario/lock-wait.md) | 锁竞争 | P1 |
| [内存压力](scenario/memory-pressure.md) | 内存使用率过高 | P1 |
| [复制延迟](scenario/replication-delay.md) | 流复制延迟 | P1 |

### P2 - 中优先级故障

| 场景 | 描述 | 优先级 |
|----------|-------------|----------|
| [VACUUM 阻塞](scenario/vacuum-blocking.md) | VACUUM 操作阻塞 | P2 |
| [WAL 积压](scenario/wal-backlog.md) | WAL 累积 | P2 |

---

## 常用工具

```python
from scripts.toolbox import DatabaseToolbox
toolbox = DatabaseToolbox()
```

## 相关资源

- [总故障排查入口](../index.md) - 返回主索引
