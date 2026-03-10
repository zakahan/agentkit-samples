# 数据探查

## 场景说明

在正式查询数据之前，必须先了解数据环境中有哪些数据可用、表结构是什么。这就是「数据探查」步骤。

探查的**正确顺序**是：

1. **实例** → 有哪些数据库实例可用
2. **数据库** → 实例下有哪些数据库
3. **表** → 数据库下有哪些表
4. **字段** → 表的列结构（字段名、类型、注释）
5. **列值** → 字段的取值情况（枚举值、时间格式、值范围）

---

## 探查流程

### 步骤一：查看可用的数据库实例

首先查看当前有哪些数据库实例可用，了解可以连接哪些数据源。

```python
# 查看所有可用实例
result = toolbox.list_instances(
    page_size=20
)
result
```

```python
# 搜索实例（按实例名称模糊匹配）
result = toolbox.list_instances(
    query="company",  # 搜索关键词，模糊匹配实例名称
    page_size=20
)
result
```

```python
# 按条件筛选实例
result = toolbox.list_instances(
    ds_type="MySQL",           # 筛选数据库类型（MySQL, Postgres, Redis, Mongo, VeDBMySQL 等）
    region_id="cn-beijing",    # 筛选区域
    instance_status="Running",  # 筛选实例状态
    page_size=20
)
result
```

**返回内容**：实例列表，包括实例 ID、名称、类型、状态等。

**何时使用**：
- 首次探查，不知道有哪些实例可用
- 用户没有提供 instance_id，需要先查询

---

### 步骤二：查看实例下的数据库列表

确定实例后，查看该实例下有哪些数据库。

```python
result = toolbox.list_databases(
    instance_id="mysql-ba85dba2cdd1",  # 数据库实例 ID
    instance_type="MySQL"               # 数据库类型
)
result
```

**返回内容**：数据库名称列表。

---

### 步骤三：列出数据库中的表

在选定的数据库中，列出所有表。

```python
result = toolbox.list_tables(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company"
)
result
```

**返回内容**：表名称列表。

**操作建议**：
- 看到表名后，根据用户需求判断应该查询哪个/哪些表
- 如果表很多，可以关注与业务相关的关键词（如 order、customer、product）

---

### 步骤四：查看表结构（字段信息）

确定要查询的表后，查看表的字段结构。

```python
result = toolbox.get_table_info(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    table="orders"
)
result
```

**返回内容**：表的详细结构，包括：
- 字段名（column_name）
- 字段类型（data_type）
- 是否允许空（nullable）
- 键信息（key）
- 注释（comment）

---

### 步骤五：查看列的取值情况

查看字段的实际取值，用于了解：
- 枚举值（分类字段有哪些唯一值）
- 时间格式（日期字段的格式是否统一）
- 值范围（数值字段的最大最小值）
- 分布情况（各值的出现频率）

```python
# 先查询表的前几行，了解数据样例
df = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT * FROM orders LIMIT 10"
)
df
```

```python
# 查看分类字段的唯一值
for col in ['status', 'region', 'category']:
    print(f"\n【{col}】唯一值：")
    print(df[col].value_counts())
```

```python
# 查看数值字段的统计信息
print(df.describe())
```

```python
# 查看日期字段的格式样例
print(df['order_date'].head(10))
print(df['order_date'].dtype)
```

```python
# 查看时间范围
print(f"订单日期范围：{df['order_date'].min()} ~ {df['order_date'].max()}")
```

---

## 完整探查示例

```python
# ===== Step 1: 查看可用实例 =====
result = toolbox.list_instances(
    ds_type="MySQL",
    page_size=10
)
print("可用实例：", result)

# ===== Step 2: 查看实例下的数据库 =====
result = toolbox.list_databases(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL"
)
print("数据库列表：", result)

# ===== Step 3: 列出表 =====
result = toolbox.list_tables(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company"
)
print("表列表：", result)

# ===== Step 4: 查看表结构 =====
result = toolbox.get_table_info(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    table="orders"
)
print("订单表结构：", result)

# ===== Step 5: 查看列值情况 =====
df = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT * FROM orders LIMIT 100"
)

# 分类字段枚举值
for col in df.select_dtypes(include='object').columns:
    print(f"{col}: {df[col].nunique()} 个唯一值")
    print(df[col].value_counts().head())

# 数值字段范围
print(df.describe())

# 日期字段范围
date_cols = df.select_dtypes(include='datetime').columns
for col in date_cols:
    print(f"{col}: {df[col].min()} ~ {df[col].max()}")
```

---

## 常见问题

### Q1：不知道该查哪个表？

1. 先用 `list_tables()` 列出所有表
2. 根据表名猜测（orders → 订单，customers → 客户）
3. 如果表很多，可以查看 `get_table_info()` 的 comment 字段获取更多信息

### Q2：字段名是英文，看不懂怎么办？

查看 `get_table_info()` 返回的 `comment` 字段，这是字段的中文注释。

如果没有注释，**必须询问用户**该字段的业务含义，不能凭猜测分析。

### Q3：表太多了，查不到需要的表？

1. 尝试查看所有表，筛选与业务关键词相关的
2. 如果是首次探查，可以询问用户：「请问您需要分析哪个主题的数据？比如订单、客户、销售等」

### Q4：如何判断日期字段的格式？

```python
# 查看日期字段的样例
df = toolbox.query_sql(...)
print(df['date_column'].head(20))

# 检查是否有格式不一致的情况
invalid_dates = df['date_column'][pd.to_datetime(df['date_column'], errors='coerce').isna()]
print(f"格式异常的行数：{len(invalid_dates)}")
```

---

## 何时询问用户

以下情况**必须主动询问用户**：

1. **找不到需要的表**：无法从表名判断哪个表包含所需数据
2. **字段含义不明**：字段名和注释都无法判断业务含义
3. **多个表都相关**：不确定应该查询哪个表或如何关联
4. **列值取值不明**：发现值都是英文，无法判断业务含义，无法和客户的所描述的词语所对应。
5. **术语不熟悉，指代不明确**：如： 客户说成功率，成功率指的是物流发送成功率？ 支付成功率。


**示例**：
> 「发现数据库中有 `orders`、`order_details`、`order_history` 三个表都包含订单信息，请问您需要分析哪个表的数据？」

> 「发现 `status` 字段包含值 `['pending', 'completed', 'cancelled', 'unknown', 'N/A']`，其中 `unknown` 和 `N/A` 是什么含义？是有效状态还是异常数据？」
