---
name: "mysql-ops"
description: "MySQL / MySQL 兼容引擎故障排查指南"
---

# MySQL / MySQL 兼容引擎故障排查

适用于 MySQL 及所有 MySQL 兼容数据库引擎（VeDBMySQL、ByteRDS 等）。

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
| [内存压力](scenario/memory-pressure.md) | 内存使用率过高 | P1 |
| [死锁](scenario/deadlock.md) | 事务死锁 | P1 |
| [主从延迟](scenario/replication-delay.md) | 主从复制延迟 | P1 |
| [慢查询](scenario/slow-query.md) | 查询性能问题 | P1 |
| [IO 瓶颈](scenario/io-bottleneck.md) | 磁盘 IO 瓶颈 | P1 |
| [锁等待](scenario/lock-wait.md) | 锁竞争 | P1 |

### P2 - 中优先级故障

| 场景 | 描述 | 优先级 |
|----------|-------------|----------|
| [会话堆积](scenario/session-pileup.md) | 活跃会话堆积 | P2 |
| [临时表溢出](scenario/temp-table-overflow.md) | 磁盘临时表溢出 | P2 |
| [Binlog 延迟](scenario/binlog-delay.md) | Binlog 延迟 | P2 |
| [网络抖动](scenario/network-jitter.md) | 网络延迟问题 | P2 |

---

## 常用工具

```python
from scripts.toolbox import DatabaseToolbox
toolbox = DatabaseToolbox()
```

## 相关资源

- [总故障排查入口](../index.md) - 返回主索引
