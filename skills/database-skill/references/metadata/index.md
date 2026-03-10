---
name: "database-skill-metadata-governance"
description: "元数据问答与治理：探查数据库实例、库表结构及资产信息。适用于数据治理、表结构分析及了解数据全貌的场景。"
---

# 数据库元数据与治理 Skill

本 Skill 专注于 **元数据问答** 和 **数据治理**，帮助用户全面探查数据库资产——从实例、数据库到表和字段的详细定义。

当你有以下需求时使用此 Skill：
- 发现可用的数据库实例及其详细信息。
- 探查数据库模式（Schema）和表定义。
- 回答关于数据位置的问题（例如："用户表在哪个数据库里？"）。
- 执行数据治理任务（例如：检查废弃表、审计表结构变更）。

## 依赖文件

- `scripts/dbw_client.py`: HTTP 客户端实现。
- `scripts/toolbox.py`: `DatabaseToolbox` 类封装。

## 初始化

```python
from scripts.toolbox import DatabaseToolbox
toolbox = DatabaseToolbox()
```

## 可用方法

### 1. 列出实例 (`list_instances`)
发现所有可用的数据库实例。支持按类型、名称、状态等条件过滤。

```python
# 列出所有 MySQL 实例
toolbox.list_instances(ds_type="MySQL", page_number=1, page_size=10)

# 按名称查找实例
toolbox.list_instances(instance_name="production-db")
```
- **返回**: `{"success": true, "data": {"total": N, "instances": [{"id": "...", "name": "...", "type": "MySQL", ...}]}}`
- **用途**: 获取正确的实例 ID（`instance_id`）以供后续操作使用。

### 2. 列出数据库 (`list_databases`)
列出指定实例下的所有数据库。

```python
toolbox.list_databases(instance_id="your_instance_id", page_number=1, page_size=10)
```
- **返回**: `{"success": true, "data": {"total": N, "databases": [{"name": "db_name", ...}]}}`

### 3. 列出表 (`list_tables`)
列出指定数据库下的所有表。

```python
toolbox.list_tables(database="your_db", instance_id="your_instance_id", page_number=1, page_size=10)
```
- **返回**: `{"success": true, "data": {"total": N, "tables": [{"name": "table_name", ...}]}}`

### 4. 获取表结构 (`get_table_info`)
获取指定表的详细结构信息（字段、类型、注释等）。

```python
toolbox.get_table_info(table="your_table", database="your_db", instance_id="your_instance_id")
```
- **返回**: `{"success": true, "data": {"name": "table_name", "columns": [{"name": "col", "type": "int", "comment": "..."}]}}`

## 数据治理工作流

利用上述元数据 API，可以构建自动化的数据治理流程。以下为三个核心治理场景的详细指南：

### 1. 全域资产盘点
建立企业级数据地图，发现“影子资产”，统计资产规模。
- [查看详细文档：全域资产盘点 (Global Asset Inventory)](asset-inventory.md)

### 2. 库表规范性审计
自动化检查数据库表结构设计规范，如主键、命名、注释、类型等。
- [查看详细文档：库表规范性审计 (Schema Standardization Audit)](schema-audit.md)

### 3. 敏感数据识别与分级
自动化扫描库表，识别 PII 和金融数据，进行数据分级打标。
- [查看详细文档：敏感数据识别与分级 (Sensitive Data Identification & Classification)](sensitive-data.md)

### 4. 数据探查
自动化分析数据分布、统计特征、空值率等，帮助理解数据内容和质量。
- [查看详细文档：数据探查 (Data Profiling)](data-profiling.md)

### 5. 数据质量监控
定义并执行 DQ 规则（准确性、一致性、及时性），生成质量报告，触发告警。
- [查看详细文档：数据质量监控 (Data Quality Monitoring)](data-quality.md)

## 常见场景

- **资产发现**: "我们有哪些数据库实例？" -> `list_instances`
- **模式导航**: "找到生产环境实例中的 'users' 表。" -> `list_databases` -> `list_tables`
- **结构分析**: "给我看下 'orders' 表的结构。" -> `get_table_info`
- **治理**: "列出所有数据库以检查是否有未授权创建的库。"
