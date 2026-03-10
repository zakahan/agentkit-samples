# 多数据源联合查询

## 场景说明

当数据分散在**多个数据库实例**或需要**数据库 + 本地文件联合分析**时使用此方式。

适用场景，以下是距离：
- 同类型数据库查询，如：订单数据在 MySQL，客户数据在另一个 MySQL 实例
- 不同类型数据库查询，如：物流配送数据在 Postgres，需要与 MySQL 订单关联
- 需要将数据库数据与本地 Excel/CSV 文件联合分析
- 跨云厂商的数据库联合查询

---

## 与「查询单个数据库」的区别

| 场景 | 使用方式 |
|------|----------|
| 只有一个数据源 | 直接用 `query_sql()` |
| 多个数据源需要关联 | 使用 `MultiSourceAnalyzer` 联合查询 |

---

## 使用步骤

### 1. 初始化分析器

```python
from scripts.multi_source_analyzer import MultiSourceAnalyzer

analyzer = MultiSourceAnalyzer()
```

### 2. 从数据库查询并注册数据

**重要**：必须使用 `query_sql()` 或 `execute_sql()` 查询数据，然后注册到分析器。

```python
# 从 MySQL 查询订单数据
df_orders = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT order_id, customer_id, order_date, total_amount, status FROM orders LIMIT 100"
)

# 从 MySQL 查询客户数据
df_customers = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT customer_id, customer_name, email, region, nation_key FROM customers"
)

# 从 Postgres 查询配送数据（不同实例）
df_shipments = toolbox.query_sql(
    instance_id="postgres-52b504529f97",
    instance_type="Postgres",
    database="d1",
    sql="SELECT shipment_id, order_id, shipment_date, delivery_date, carrier, status FROM shipments"
)

# 注册到分析器
analyzer.register_dataframe('orders', df_orders)
analyzer.register_dataframe('customers', df_customers)
analyzer.register_dataframe('shipments', df_shipments)
```

### 3. 直接读取本地文件（可选）

```python
# 读取本地 CSV 文件
analyzer.register_file('sales', '../data/regional_sales.csv')

# 读取本地 Excel 文件
analyzer.register_file('products', '../data/business_data.xlsx', sheet='Product Inventory')
```

### 4. 查看已注册的数据源

```python
analyzer.list_sources()
```

### 5. 执行跨源联合查询

```python
# MySQL + Postgres + Excel 联合查询
result = analyzer.query("""
    SELECT 
        c.customer_name,
        c.region,
        o.order_id,
        o.total_amount,
        o.status as order_status,
        s.shipment_id,
        s.carrier,
        s.status as shipment_status
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN shipments s ON o.order_id = s.order_id
    ORDER BY o.order_date DESC
    LIMIT 50
""")
df = pd.DataFrame(result)
df
```

---

## 完整示例：电商订单 + 配送 + 区域销售分析

```python
from scripts.multi_source_analyzer import MultiSourceAnalyzer
import pandas as pd

analyzer = MultiSourceAnalyzer()

# ===== 第一步：从多个数据库查询数据 =====

# 1. MySQL 订单数据
df_orders = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="ecom",
    sql="SELECT order_id, customer_id, order_date, total_amount, status FROM ecom_orders WHERE order_date >= '2024-01-01'"
)

# 2. MySQL 客户数据
df_customers = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="ecom",
    sql="SELECT customer_id, customer_name, email, region, nation_key FROM ecom_customers"
)

# 3. Postgres 配送数据
df_shipments = toolbox.query_sql(
    instance_id="postgres-52b504529f97",
    instance_type="Postgres",
    database="logistics",
    sql="SELECT shipment_id, order_id, shipment_date, delivery_date, carrier, status FROM logistics_shipments"
)

# ===== 第二步：注册到分析器 =====
analyzer.register_dataframe('orders', df_orders)
analyzer.register_dataframe('customers', df_customers)
analyzer.register_dataframe('shipments', df_shipments)

# ===== 第三步：读取本地文件 =====
analyzer.register_file('regional_sales', '../data/regional_sales.csv')

# ===== 第四步：联合查询 =====
result = analyzer.query("""
    SELECT 
        c.customer_name,
        c.region,
        c.nation_key,
        o.order_id,
        o.order_date,
        o.total_amount,
        o.status as order_status,
        s.shipment_id,
        s.carrier,
        s.delivery_date,
        s.status as shipment_status,
        r.target_region,
        r.sales_target
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    LEFT JOIN shipments s ON o.order_id = s.order_id
    LEFT JOIN regional_sales r ON c.region = r.region_code
    WHERE o.order_date >= '2024-01-01'
    ORDER BY o.order_date DESC
    LIMIT 100
""")

df = pd.DataFrame(result)
df
```

---

## 支持的数据源组合

| 组合 | 说明 |
|------|------|
| MySQL + MySQL | 同一或不同实例的 MySQL 数据库 |
| MySQL + Postgres | 跨数据库类型 |
| MySQL + Excel | 数据库 + 本地文件 |
| Postgres + CSV | 数据库 + 本地文件 |
| MySQL + Postgres + Excel | 多数据源混合 |

---

## 注意事项

1. **必须先查询数据库**：使用 `query_sql()` 获取数据，再调用 `register_dataframe()` 注册
2. **字段关联**：确保关联字段的数据类型一致（如都是整数或都是字符串）
3. **注册顺序**：建议先注册数据量大的表，提高查询效率
4. **结果限制**：默认返回 100 条，可通过 `query(sql, limit=N)` 调整
5. **性能考虑**：大量数据时，优先在数据库端完成筛选和聚合，只传输需要的字段和行数
