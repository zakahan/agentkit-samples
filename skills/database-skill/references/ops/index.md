---
name: "database-skill-ops"
description: "数据库运维 SOP：基于标准化流程（SOP）进行数据库故障排查，涵盖资源基线确认、负载分析、会话分析、慢查询定位、空间分析及变更追溯。"
---

# 数据库故障排查 SOP

选择您要排查的数据库类型：

## MySQL（包括 VeDBMySQL、ByteRDS 等 MySQL 兼容引擎）

MySQL 及 MySQL 兼容数据库引擎的故障排查指南。

**常见场景：**
- [CPU 打满](mysql/scenario/cpu-spike.md) - CPU 使用率过高
- [连接数打满](mysql/scenario/connection-full.md) - 连接数达到上限
- [磁盘空间不足](mysql/scenario/disk-full.md) - 磁盘空间耗尽
- [内存压力](mysql/scenario/memory-pressure.md) - 内存使用率过高
- [死锁](mysql/scenario/deadlock.md) - 事务死锁
- [主从延迟](mysql/scenario/replication-delay.md) - 主从复制延迟
- [慢查询](mysql/scenario/slow-query.md) - 查询性能问题
- [IO 瓶颈](mysql/scenario/io-bottleneck.md) - 磁盘 IO 瓶颈
- [锁等待](mysql/scenario/lock-wait.md) - 锁竞争
- [会话堆积](mysql/scenario/session-pileup.md) - 活跃会话堆积
- [临时表溢出](mysql/scenario/temp-table-overflow.md) - 磁盘临时表溢出
- [Binlog 延迟](mysql/scenario/binlog-delay.md) - Binlog 延迟
- [网络抖动](mysql/scenario/network-jitter.md) - 网络延迟问题

[MySQL 故障排查索引](mysql/index.md)

---

## PostgreSQL（包括所有 PostgreSQL 兼容引擎）

PostgreSQL 及所有 PostgreSQL 兼容数据库引擎的故障排查指南。

**常见场景：**
- [CPU 打满](postgresql/scenario/cpu-spike.md) - CPU 使用率过高
- [连接数打满](postgresql/scenario/connection-full.md) - 连接数达到上限
- [磁盘空间不足](postgresql/scenario/disk-full.md) - 磁盘空间耗尽
- [慢查询](postgresql/scenario/slow-query.md) - 查询性能问题
- [锁等待](postgresql/scenario/lock-wait.md) - 锁竞争
- [内存压力](postgresql/scenario/memory-pressure.md) - 内存使用率过高
- [VACUUM 阻塞](postgresql/scenario/vacuum-blocking.md) - VACUUM 操作阻塞
- [WAL 积压](postgresql/scenario/wal-backlog.md) - WAL 累积
- [复制延迟](postgresql/scenario/replication-delay.md) - 流复制延迟

[PostgreSQL 故障排查索引](postgresql/index.md)

---

## MongoDB

MongoDB 数据库故障排查指南。

**常见场景：**
- [连接数打满](mongodb/scenario/connection-full.md) - 连接数达到上限
- [磁盘空间不足](mongodb/scenario/disk-full.md) - 磁盘空间耗尽
- [慢查询](mongodb/scenario/slow-query.md) - 查询性能问题
- [内存压力](mongodb/scenario/memory-pressure.md) - WiredTiger 缓存压力
- [复制延迟](mongodb/scenario/replication-delay.md) - 副本集延迟
- [锁等待](mongodb/scenario/lock-wait.md) - 数据库/集合锁
- [连接泄漏](mongodb/scenario/connection-leak.md) - 连接泄漏
- [集群故障](mongodb/scenario/cluster-failure.md) - 分片集群问题

[MongoDB 故障排查索引](mongodb/index.md)

---

## Redis

Redis 内存数据库故障排查指南。

**常见场景：**
- [内存打满](redis/scenario/memory-full.md) - 内存耗尽 (OOM)
- [连接数打满](redis/scenario/connection-full.md) - 连接数达到上限
- [慢查询](redis/scenario/slow-query.md) - 慢命令执行
- [持久化阻塞](redis/scenario/persistence-block.md) - AOF/RDB 阻塞
- [集群故障](redis/scenario/cluster-failure.md) - 集群节点故障
- [阻塞命令](redis/scenario/blocking-command.md) - 阻塞命令
- [复制延迟](redis/scenario/replication-delay.md) - 主从延迟
- [CPU 打满](redis/scenario/cpu-spike.md) - CPU 使用率过高

[Redis 故障排查索引](redis/index.md)

---

## 快速参考

### 常用工具

```python
from scripts.toolbox import DatabaseToolbox
toolbox = DatabaseToolbox()
```

### 常用监控指标

| 指标 | 说明 |
|---------|-------------|
| CpuUsage | CPU使用率 |
| MemoryUsage | 内存使用率 |
| QPS | 每秒查询数 |
| TPS | 每秒事务数 |
| ActiveSessions | 活跃连接数 |
| IOPS | 磁盘IOPS |
| DiskUsage | 磁盘使用率 |

### ⚠️ 重要提示

> **危险操作需确认**：以下类型的操作需要您确认后才能执行：
> - 终止会话/进程 (kill_process)
> - 修改数据库参数 (SET GLOBAL)
> - 删除/清空数据 (DELETE, DROP, FLUSH)
> - 执行checkpoint或vacuum
>
> 在执行这些操作前，系统会提示您确认。
