# API 参考

## 1. 自然语言转 SQL

```python
toolbox.nl2sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    query="查询最近一周的销售额",
    tables=["orders"]
)
```

- 返回: `{"success": true, "data": {"sql": "SELECT ...", "sql_type": "SELECT"}}`

## 2. 执行查询（返回 Pandas DataFrame）

```python
df = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT * FROM orders LIMIT 100"
)
df
```

- 仅支持 SELECT/SHOW，返回 `pandas.DataFrame`
- 非 SELECT/SHOW 抛出 `ValueError`

## 3. 执行 SQL（通用）

```python
toolbox.execute_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    commands="SELECT ..."
)
```

- 返回: `{"success": true, "data": {...}}`

## 4. 列出表

```python
result = toolbox.list_tables(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company"
)
result
```

## 5. 获取表结构

```python
result = toolbox.get_table_info(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    table="orders"
)
result
```

## 6. 列出数据库

```python
result = toolbox.list_databases(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL"
)
result
```

## 7. 获取实例列表

```python
result = toolbox.list_instances(
    ds_type="MySQL",           # 数据库类型：MySQL, Postgres, Redis, Mongo, VeDBMySQL 等
    region_id="cn-beijing",    # 区域 ID
    instance_name="company",   # 实例名称（模糊匹配）
    instance_status="Running",  # 实例状态
    page_number=1,
    page_size=10
)
result
```

- 返回实例列表，支持按类型、区域、名称、状态筛选

## 8. 跨源联合查询

使用 `MultiSourceAnalyzer` 进行本地跨数据源分析（支持数据库 + 文件联合查询）。

### 初始化分析器

```python
from scripts.multi_source_analyzer import MultiSourceAnalyzer

analyzer = MultiSourceAnalyzer()
```

### 注册 DataFrame（从数据库查询）

```python
# 从数据库查询数据
df_orders = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT * FROM orders LIMIT 100"
)

# 注册到分析器
analyzer.register_dataframe('orders', df_orders)
```

### 注册文件（CSV/Excel/JSON/Parquet）

```python
analyzer.register_file('sales', '../data/regional_sales.csv')
analyzer.register_file('products', '../data/business_data.xlsx', sheet='Product Inventory')
```

### 列出数据源

```python
analyzer.list_sources()
```

### 预览数据

```python
analyzer.preview('orders', n=5)
```

### 查看表结构

```python
analyzer.describe('orders')
```

### 执行跨源 SQL 查询

```python
result = analyzer.query("""
    SELECT c.name, SUM(o.amount) as total
    FROM orders o
    JOIN customers c ON o.customer_id = c.id
    GROUP BY c.name
""")
df = pd.DataFrame(result)
df
```

### 注意事项

- `query_sql()` 仅支持 SELECT/SHOW，大数据量建议加 LIMIT
- 需要安装 pandas: `pip install pandas`
