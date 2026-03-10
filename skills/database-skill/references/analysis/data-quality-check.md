# 数据质量检查

## 场景说明

在获取数据后，必须进行数据质量检查，确保数据可用再做分析。这是数据分析流程中的**必做步骤**。

---

## 检查清单

### 1. 数据概览

```python
# 查看数据维度（行数 x 列数）
print(f"维度：{df.shape[0]}行 × {df.shape[1]}列")
```

### 2. 缺失值检查

```python
# 计算每列的缺失值百分比
missing_pct = (df.isnull().sum() / len(df) * 100).round(2)

# 只显示有缺失值的列
missing_cols = missing_pct[missing_pct > 0]
if len(missing_cols) > 0:
    print("存在缺失值的列：")
    print(missing_cols)
else:
    print("无缺失值")
```

**处理方式**：
- 缺失率 > 50%：考虑删除该列
- 缺失率 < 10%：可填充默认值或删除缺失行
- 缺失率 10%-50%：根据业务逻辑决定填充方式

### 3. 重复值检查

```python
# 检查重复行数量
duplicates = df.duplicated().sum()
print(f"重复行数：{duplicates}")

# 如果有重复，查看重复行
if duplicates > 0:
    print("\n重复行示例：")
    print(df[df.duplicated(keep=False)].head(10))
```

### 4. 数值列统计

```python
# 查看数值列的基本统计信息
print(df.describe())
```

检查要点：
- **计数**：是否与预期一致
- **均值/中位数**：是否合理
- **最小值/最大值**：是否存在异常值（如负数年龄、超大金额）
- **标准差**：是否存在极端值

### 5. 分类列唯一值检查

```python
# 查看所有分类（字符串）列的唯一值分布
for col in df.select_dtypes(include='object').columns:
    unique_count = df[col].nunique()
    print(f"\n【{col}】唯一值数量：{unique_count}")
    print(df[col].value_counts().head(10))
```

---

## 常见数据问题及修复方法

### 问题一：列值异常（超出业务合理范围）

**识别**：
```python
# 检查年龄列是否有异常值
print(df['age'].describe())
print(df[df['age'] < 0])  # 负数年龄
print(df[df['age'] > 120])  # 超长年龄
```

**修复**：
```python
# 将异常值设为空
df.loc[df['age'] < 0, 'age'] = None
df.loc[df['age'] > 120, 'age'] = None

# 或者替换为合理值
df.loc[df['age'] < 0, 'age'] = df['age'].median()
```

### 问题二：格式不一致

**日期格式混乱**：
```python
# 查看日期列的数据类型和示例
print(df['date'].head(10))
print(df['date'].dtype)

# 统一转换为日期类型
df['date'] = pd.to_datetime(df['date'], errors='coerce')
```

**数值格式问题**：
```python
# 去除千分位逗号，转换为数值
df['amount'] = df['amount'].str.replace(',', '').astype(float)
```

### 问题三：字符串前后空格/编码问题

```python
# 去除前后空格
df['name'] = df['name'].str.strip()

# 去除多余空格
df['name'] = df['name'].str.replace(r'\s+', ' ', regex=True)

# 处理编码问题
df['name'] = df['name'].str.normalize('NFKC')
```

### 问题四：重复记录

```python
# 查看重复情况
print(f"重复行数：{df.duplicated().sum()}")

# 删除重复行
df = df.drop_duplicates()

# 根据特定列去重
df = df.drop_duplicates(subset=['order_id'])
```

---

## 自动化检查函数

可将上述检查封装为函数，方便复用：

```python
def check_data_quality(df):
    """数据质量检查"""
    print("=" * 50)
    print("数据质量检查报告")
    print("=" * 50)

    # 1. 数据概览
    print(f"\n【1. 数据概览】")
    print(f"维度：{df.shape[0]}行 × {df.shape[1]}列")

    # 2. 缺失值
    print(f"\n【2. 缺失值检查】")
    missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
    missing_cols = missing_pct[missing_pct > 0]
    if len(missing_cols) > 0:
        print(missing_cols)
    else:
        print("无缺失值")

    # 3. 重复值
    print(f"\n【3. 重复值检查】")
    duplicates = df.duplicated().sum()
    print(f"重复行数：{duplicates}")

    # 4. 数值列统计
    print(f"\n【4. 数值列统计】")
    print(df.describe())

    # 5. 分类列唯一值
    print(f"\n【5. 分类列唯一值】")
    for col in df.select_dtypes(include='object').columns:
        print(f"{col}: {df[col].nunique()} 个唯一值")

    print("\n" + "=" * 50)

# 使用
check_data_quality(df)
```

---

## 检查结果记录

检查完成后，需要记录发现的问题：

```python
quality_issues = []

# 记录缺失值
if missing_pct.sum() > 0:
    quality_issues.append(f"存在缺失值：{missing_cols.to_dict()}")

# 记录重复值
if duplicates > 0:
    quality_issues.append(f"存在 {duplicates} 条重复记录")

# 记录异常值
if any(df['age'] < 0):
    quality_issues.append("存在负数年龄")

print("发现的数据质量问题：")
for issue in quality_issues:
    print(f"  - {issue}")
```

---

## 何时需要询问用户

以下情况**必须主动询问用户**：

1. **列含义不明**：字段名无法判断业务含义（如 `col1`, `flag`）
2. **异常值不确定**：不知道是数据错误还是真实值（如超高收入）
3. **缺失值处理方式不明确**：不知道应该删除还是填充
4. **业务规则不确定**：不知道某个字段的有效范围

**示例**：
> 「发现 `status` 列有 5 个唯一值：`['pending', 'completed', 'cancelled', 'unknown', 'N/A']`。其中 `unknown` 和 `N/A` 是否应该视为缺失值处理？」
