# 查询数据库

## 场景说明

当用户只需要从一个数据库实例获取数据时使用此方式。这是**最简单、最常用**的场景。

适用场景：
- 用户明确指定了数据库实例
- 只需要查询单个数据库的数据
- 数据量不大，可以直接返回

---

## 方式一：自然语言生成 SQL

**使用场景**：用户不确定如何编写 SQL，或者只想用自然语言描述需求。

**执行步骤**：

1. 调用 `nl2sql` 将自然语言转换为 SQL
2. 检查返回的 SQL 是否合理
3. 调用 `query_sql` 执行查询

```python
# 步骤1：用自然语言生成 SQL
result = toolbox.nl2sql(
    instance_id="mysql-ba85dba2cdd1",  # 数据库实例 ID
    instance_type="MySQL",               # 数据库类型：MySQL, Postgres, VeDBMySQL 等
    database="company",                  # 数据库名称
    query="查询最近一月的订单数据"       # 用户的需求描述
)
# 查看生成的 SQL
print(result["data"]["sql"])

# 步骤2：执行生成的 SQL
df = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql=result["data"]["sql"]  # 使用 nl2sql 返回的 SQL
)
df
```

**注意事项**：
- `nl2sql` 返回的是结构化对象，需要通过 `result["data"]["sql"]` 获取 SQL 字符串
- 生成后**务必检查 SQL 逻辑是否正确**，必要时手动修正
- 某些复杂需求可能无法准确转换，需手动编写 SQL

---

## 方式二：直接执行 SQL

**使用场景**：用户已经知道要执行的 SQL，或者你需要编写特定的查询。

```python
# 直接执行 SQL 查询
df = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT * FROM orders WHERE order_date >= DATE_SUB(NOW(), INTERVAL 1 MONTH) LIMIT 100"
)
df
```

**常用查询示例**：

```python
# 查询订单表前10条
df = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT * FROM orders LIMIT 10"
)

# 按条件筛选
df = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT * FROM orders WHERE status = 'completed' AND total_amount > 1000"
)

# 分组统计
df = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT region, COUNT(*) as cnt, SUM(amount) as total FROM orders GROUP BY region"
)
```

**注意事项**：
- `query_sql()` **仅支持 SELECT 和 SHOW 语句**
- DML（INSERT/UPDATE/DELETE）和 DDL（CREATE/ALTER/DROP）会抛出 `ValueError`
- 大数据量查询建议添加 `LIMIT`，避免返回过多数据导致内存问题

---

## 先探查，再查询

**最佳实践**：在执行查询前，先了解表结构，避免写错字段名。

```python
# 1. 查看有哪些表
result = toolbox.list_tables(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company"
)
print(result)

# 2. 查看表结构
result = toolbox.get_table_info(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    table="orders"
)
print(result)
```
