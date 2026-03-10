# 慢查询故障排查

## 概述

慢查询在 Redis 中通常指执行时间较长的命令，可能是由于大 key 操作、复杂数据结构、keys 命令等原因导致。

## 典型症状

- 命令执行时间变长
- 特定操作响应慢
- CPU 使用率升高
- 客户端超时

## 排查步骤

### 步骤 1: 获取慢查询趋势图

```python
import time
now = int(time.time())

# 获取慢查询时间序列趋势（了解慢查询随时间的变化）
toolbox.describe_slow_log_time_series_stats(
    start_time=now - 3600,
    end_time=now,
    instance_id="redis-xxx",
    instance_type="Redis",
    interval=300
)
```

### 步骤 2: 获取慢查询聚合统计

```python
# 获取慢查询聚合统计（按命令聚合，找出最耗时的命令类型）
toolbox.describe_aggregate_slow_logs(
    start_time=now - 3600,
    end_time=now,
    instance_id="redis-xxx",
    instance_type="Redis",
    order_by="TotalQueryTime",
    sort_by="DESC"
)
```

### 步骤 3: 获取慢查询明细

```python
# 获取慢查询明细（查看具体哪些命令最慢）
toolbox.describe_slow_logs(
    start_time=now - 3600,
    end_time=now,
    order_by="QueryTime",
    sort_by="DESC"
)
```

### 步骤 4: 获取完整命令历史

```python
# 获取完整命令历史详情
toolbox.describe_full_sql_detail(
    start_time=now - 3600,
    end_time=now,
    instance_id="redis-xxx",
    instance_type="Redis",
    page_size=20
)
```

### 步骤 5: 获取命令统计

```python
# 获取命令统计
toolbox.execute_sql(
    commands="INFO commandstats;", database="0"
)
```

### 步骤 6: 扫描大 Key

```python
# 使用 Redis SCAN 扫描大 Key（需要您确认后执行）
# 使用 redis-cli --bigkeys 或 SCAN + DEBUG OBJECT
toolbox.execute_sql(
    commands="""
    redis-cli --bigkeys -h <host> -p <port> -a <password>
    """, database="0"
)
```

## 常见根因

| 根因 | 说明 |
|-------|-------------|
| 大 Key | 大 key 操作 |
| Keys/Scan | keys 命令遍历全量数据 |
| Sort/ZUnion | 复杂集合操作 |
| Lua Script | 复杂 Lua 脚本 |
| HGETALL/SMEMBERS | 获取大 hash/set |

## ⚠️ 应急处置（需确认后执行）

### 终止长时间运行的命令

> **警告**：终止命令会导致当前操作失败，请在确认后执行！

```python
# 使用 CLIENT KILL 终止长时间连接的客户端
# 需要您确认后才能执行
toolbox.execute_sql(
    commands="CLIENT KILL ID <client-id>;", database="0"
)
```

### 删除大 Key

> **警告**：删除大 key 可能导致阻塞，请在确认后执行！

```python
# 使用 SCAN + DEL 渐进式删除大 key
# 需要您确认后才能执行
toolbox.execute_sql(
    commands="""
    SCAN 0 MATCH "big:*" COUNT 1000
    -- 建议使用 UNLINK 代替 DEL
    """, database="0"
)
```

## 预防措施

1. 避免 KEYS 命令，使用 SCAN 代替
2. 使用适当的数据结构
3. 在客户端设置命令超时
4. 监控慢查询日志
5. 使用 pipeline 批量操作
6. 设置延迟告警
