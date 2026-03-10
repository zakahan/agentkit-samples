---
name: "redis-ops"
description: "Redis 故障排查指南"
---

# Redis 故障排查

## 选择故障场景

### P0 - 紧急故障（需立即处理）

| 场景 | 描述 | 优先级 |
|----------|-------------|----------|
| [内存打满](scenario/memory-full.md) | 内存耗尽 (OOM) | P0 |
| [连接数打满](scenario/connection-full.md) | 连接数达到上限 | P0 |
| [集群故障](scenario/cluster-failure.md) | 集群节点故障 | P0 |

### P1 - 高优先级故障

| 场景 | 描述 | 优先级 |
|----------|-------------|----------|
| [慢查询](scenario/slow-query.md) | 慢命令执行 | P1 |
| [持久化阻塞](scenario/persistence-block.md) | AOF/RDB 阻塞 | P1 |
| [阻塞命令](scenario/blocking-command.md) | 阻塞命令 | P1 |
| [复制延迟](scenario/replication-delay.md) | 主从延迟 | P1 |
| [CPU 打满](scenario/cpu-spike.md) | CPU 使用率过高 | P1 |

---

## 常用工具

```python
from scripts.toolbox import DatabaseToolbox
toolbox = DatabaseToolbox()
```

## 相关资源

- [总故障排查入口](../index.md) - 返回主索引
