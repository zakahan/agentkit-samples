# 查询文件数据源

## 场景说明

当用户需要从本地文件（CSV、Excel、JSON、Parquet）中获取数据时使用此方式。

适用场景：
- 用户提供了本地文件路径
- 数据存储在 CSV、Excel、JSON 或 Parquet 文件中
- 不需要连接数据库

---

## 支持的文件类型

| 文件类型 | 扩展名 | 说明 |
|---------|--------|------|
| CSV | .csv | 逗号分隔值文件 |
| Excel | .xlsx, .xls | Excel 文件，可指定 Sheet |
| JSON | .json | JSON 格式文件 |
| Parquet | .parquet | 列式存储文件，查询性能高 |

---

## 使用步骤

### 1. 初始化分析器

```python
from scripts.multi_source_analyzer import MultiSourceAnalyzer

analyzer = MultiSourceAnalyzer()
```

### 2. 注册文件

```python
# 注册 CSV 文件
analyzer.register_file('sales', '../data/regional_sales.csv')

# 注册 Excel 文件（指定 Sheet 名称）
analyzer.register_file('products', '../data/business_data.xlsx', sheet='Product Inventory')

# 注册 Excel 文件（使用第一个 Sheet）
analyzer.register_file('inventory', '../data/business_data.xlsx')

# 注册 JSON 文件
analyzer.register_file('users', '../data/users.json')

# 注册 Parquet 文件
analyzer.register_file('events', '../data/events.parquet')
```

**参数说明**：
- `name`：数据源名称（用于 SQL 查询中的表名），建议使用英文
- `file_path`：文件路径，相对于当前工作目录或绝对路径
- `sheet`：仅 Excel 文件需要，指定 Sheet 名称或索引（默认 0）

### 3. 查看数据源列表

```python
analyzer.list_sources()
```

返回示例：
```json
[
  {"name": "sales", "type": "file", "columns": [...], "row_count": 1000},
  {"name": "products", "type": "file", "columns": [...], "row_count": 500}
]
```

### 4. 预览数据

```python
# 查看前5行
analyzer.preview('sales', n=5)
```

### 5. 查看数据结构

```python
# 查看表结构（字段名和类型）
analyzer.describe('sales')
```

### 6. 执行查询

```python
# SQL 查询
result = analyzer.query("""
    SELECT * FROM sales LIMIT 10
""")
df = pd.DataFrame(result)
df
```

---

## 完整示例

```python
# 1. 初始化
from scripts.multi_source_analyzer import MultiSourceAnalyzer
import pandas as pd

analyzer = MultiSourceAnalyzer()

# 2. 注册文件
analyzer.register_file('product', '../data/business_data.xlsx', sheet='Product Inventory')

# 3. 预览数据
analyzer.preview('product', n=5)

# 4. 查看结构
analyzer.describe('product')

# 5. 查询数据
result = analyzer.query("""
    SELECT product_name, category, price, stock
    FROM product
    WHERE price > 100
    ORDER BY stock DESC
""")
df = pd.DataFrame(result)
df
```

---

## 示例数据

参考 [data/index.md](../../data/index.md)，包含以下测试数据：

| 类型 | 文件 | 说明 |
|------|------|------|
| CSV | regional_sales.csv | 区域销售目标数据 |
| CSV | sales_associates_performance.csv | 销售人员绩效数据 |
| CSV | customer_satisfaction.csv | 客户满意度调查数据 |
| JSON | product_categories.json | 产品分类数据 |
| Excel | Marketing Campaigns | 营销活动数据 |
| Excel | Product Inventory | 产品库存数据 |
| Excel | Suppliers | 供应商数据 |
| Parquet | sales_history.parquet | 销售历史交易数据 |
| Parquet | user_behavior.parquet | 用户行为数据 |
| Parquet | inventory_snapshot.parquet | 产品库存快照 |
| Parquet | web_logs.parquet | 网站访问日志 |

---

## 注意事项

- 文件路径建议使用**相对路径**（相对于工作目录）或**绝对路径**
- Excel 文件如有多 Sheet，需通过 `sheet` 参数指定
- 大文件可能加载较慢，Parquet 格式查询性能最佳
- 查询结果默认限制 100 条，可通过 `query(sql, limit=N)` 调整
