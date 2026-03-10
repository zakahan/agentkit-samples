# 探索性数据分析 (EDA)

## 场景说明

在完成数据质量检查后，对数据进行探索性分析，发现数据中的规律、趋势和异常。

这是**从数据到洞察的关键步骤**。

---

## 分析类型

### 1. 基本统计

```python
# 查看数值列的基本统计信息
df.describe()
```

```python
# 单独计算某列的统计值
df['sales'].mean()    # 平均值
df['sales'].median()  # 中位数
df['sales'].std()     # 标准差
df['sales'].min()     # 最小值
df['sales'].max()     # 最大值
df['sales'].sum()     # 总和
df['sales'].count()   # 非空值数量
```

---

### 2. 分组统计

按某个维度（分类字段）进行聚合分析。

```python
# 按单个维度分组统计
df.groupby('category')['sales'].sum()           # 按品类求和
df.groupby('region')['sales'].mean()            # 按区域求平均
df.groupby('status')['order_id'].count()        # 按状态计数
```

```python
# 按多个维度分组
df.groupby(['region', 'category'])['sales'].agg(['sum', 'mean', 'count'])
```

```python
# 分组后排序
top_regions = df.groupby('region')['sales'].sum().sort_values(ascending=False)
```

---

### 3. 时间趋势分析

当数据中包含日期/时间字段时，进行时间维度的分析。

```python
# 转换日期列
df['date'] = pd.to_datetime(df['date'])

# 按月汇总
monthly_sales = df.set_index('date').resample('M')['sales'].sum()

# 按周汇总
weekly_sales = df.set_index('date').resample('W')['sales'].sum()

# 按天汇总
daily_sales = df.set_index('date').resample('D')['sales'].sum()

# 同比/环比计算
monthly_sales.pct_change()        # 环比增长率
monthly_sales.pct_change(12)     # 同比增长率（假设按月）
```

---

### 4. 分布分析

查看数据的分布情况。

```python
# 数值列分布
df['age'].hist(bins=30)          # 直方图
df['sales'].describe(percentiles=[0.25, 0.5, 0.75, 0.9])  # 分位数

# 分类列分布
df['category'].value_counts()                     # 频次
df['category'].value_counts(normalize=True)        # 频率（占比）
```

---

### 5. 相关性分析

查看不同变量之间的相关关系。

```python
# 相关矩阵
df.corr()

# 某列与目标列的相关性
df['price'].corr(df['sales'])

# 绘制散点图（需要 matplotlib）
import matplotlib.pyplot as plt
plt.scatter(df['price'], df['sales'])
```

---

### 6. 排名分析

```python
# Top N 分析
df.nlargest(10, 'sales')                    # 销售额前10
df.nsmallest(10, 'profit')                   # 利润后10

# 分组 Top N
df.groupby('region').apply(lambda x: x.nlargest(5, 'sales'))
```

---

### 7. 漏斗分析

常用于分析转化率。

```python
# 漏斗分析示例：订单流程
funnel = df.groupby('step')['user_id'].nunique()
funnel_rate = funnel / funnel.iloc[0] * 100  # 转化率
```

---

## 常用分析模式

### 销售分析

```python
# 整体销售情况
total_sales = df['sales'].sum()
avg_sales = df['sales'].mean()

# 按区域销售
region_sales = df.groupby('region')['sales'].sum().sort_values(ascending=False)

# 按产品销售
product_sales = df.groupby('product_name')['sales'].sum().sort_values(ascending=False)

# 按时间趋势
df['month'] = df['date'].dt.to_period('M')
monthly_sales = df.groupby('month')['sales'].sum()
```

### 用户分析

```python
# 用户数量
total_users = df['user_id'].nunique()

# 新用户/活跃用户
new_users = df[df['is_new'] == 1].groupby('date')['user_id'].nunique()

# 用户留存
retention = df.groupby(['register_date', 'activity_date']).agg({'user_id': 'nunique'})
```

---

## EDA 输出模板

每次 EDA 完成后，建议记录以下内容：

```python
eda_report = {
    "数据概况": {
        "总行数": len(df),
        "总列数": len(df.columns),
        "数值列": list(df.select_dtypes(include='number').columns),
        "分类列": list(df.select_dtypes(include='object').columns),
    },
    "关键发现": [
        "发现1：xxx",
        "发现2：xxx",
    ],
    "下一步建议": [
        "建议1：xxx",
    ]
}
```

---

## 注意事项

1. **先问目标**：在开始 EDA 前，先明确用户想了解什么
2. **层层深入**：从总体到细节，从概览到细分
3. **关注异常**：发现数据中的异常值、异常模式
4. **可视化辅助**：适当用图表辅助理解，但重点放在数值洞察上

---

## 8. 麦肯锡分析框架函数库

> **⚠️ AI 在 Step 4 必须调用以下函数进行框架分析**

### 8.1 逻辑树 (Logic Tree) - 用于利润/增长问题

```python
def logic_tree_analysis(df, target_column, dimensions):
    """
    利润拆解分析：利润 = 收入 - 成本
    收入 = 量 × 价

    Args:
        df: DataFrame
        target_column: 目标指标（如 'sales', 'profit'）
        dimensions: 拆解维度列表（如 ['region', 'product_category']）

    Returns:
        dict: {
            'breakdown': {...},
            'top_contributors': [...],
            'insights': [...]
        }
    """
    total = df[target_column].sum()

    breakdown = {}
    for dim in dimensions:
        dim_contribution = df.groupby(dim)[target_column].sum()
        dim_contribution_pct = dim_contribution / total * 100
        breakdown[dim] = {
            'values': dim_contribution.to_dict(),
            'percentages': dim_contribution_pct.to_dict()
        }

    all_items = df.groupby(dimensions[-1])[target_column].sum().sort_values(ascending=False)
    cumulative_pct = all_items.cumsum() / all_items.sum() * 100
    top_contributors = all_items[cumulative_pct <= 80].index.tolist()

    insights = [
        f"{dimensions[-1]} '{top_contributors[0]}' 贡献了 {all_items.iloc[0]/total*100:.1f}% 的 {target_column}",
        f"头部 {len(top_contributors)} 个 {dimensions[-1]} 贡献了 80% 的 {target_column}"
    ]

    return {
        'breakdown': breakdown,
        'top_contributors': top_contributors,
        'insights': insights,
        'total': total
    }
```

### 8.2 3C 模型 (3C Analysis) - 用于市场/客户问题

```python
def three_c_analysis(df, customer_col, product_col, sales_col):
    """
    3C 分析：Customer, Company, Competitor

    Returns:
        dict: {
            'customer': {...},
            'company': {...},
            'competitor': {...}
        }
    """
    customer_analysis = {
        'top_customers': df.groupby(customer_col)[sales_col].sum().nlargest(10).to_dict(),
        'customer_concentration': df.groupby(customer_col)[sales_col].sum().nlargest(1).sum() / df[sales_col].sum() * 100
    }

    company_analysis = {
        'total_sales': df[sales_col].sum(),
        'avg_transaction': df[sales_col].mean(),
        'transaction_count': len(df)
    }

    competitor_analysis = {}
    if 'competitor' in df.columns:
        competitor_analysis = {
            'market_share': df.groupby('competitor')[sales_col].sum() / df[sales_col].sum() * 100,
            'top_competitor': df.groupby('competitor')[sales_col].sum().idxmax()
        }

    return {
        'customer': customer_analysis,
        'company': company_analysis,
        'competitor': competitor_analysis
    }
```

### 8.3 假设驱动分析 (Hypothesis-Driven) - 用于复杂归因问题

```python
def hypothesis_driven_analysis(df, target_column, factor_columns):
    """
    假设驱动分析流程：
    1. 提出假设
    2. 验证假设（统计检验）
    3. 修正结论

    Args:
        df: DataFrame
        target_column: 目标变量
        factor_columns: 候选影响因素列表

    Returns:
        dict: {
            'hypotheses': [...],
            'validated': [...],
            'rejected': [...],
            'correlations': {...}
        }
    """
    results = {
        'hypotheses': [],
        'validated': [],
        'rejected': [],
        'correlations': {}
    }

    for factor in factor_columns:
        if factor in df.columns and df[factor].dtype in ['int64', 'float64']:
            valid_mask = df[factor].notna() & df[target_column].notna()
            if valid_mask.sum() > 10:
                corr = df.loc[valid_mask, factor].corr(df.loc[valid_mask, target_column])

                hypothesis = f"{factor} 与 {target_column} 存在相关关系"
                results['hypotheses'].append(hypothesis)

                if abs(corr) > 0.3:
                    results['validated'].append({
                        'factor': factor,
                        'correlation': corr,
                        'strength': 'strong' if abs(corr) > 0.5 else 'moderate'
                    })
                else:
                    results['rejected'].append({
                        'factor': factor,
                        'correlation': corr
                    })

                results['correlations'][factor] = {'corr': corr}

    return results
```

### 8.4 YoY/MoM 对比分析

```python
def time_comparison_analysis(df, date_column, value_column, period='M'):
    """
    同比/环比分析

    Args:
        df: DataFrame
        date_column: 日期列
        value_column: 数值列
        period: 'M' 月, 'W' 周, 'D' 日

    Returns:
        dict: {
            'current': float,
            'previous': float,
            'change_pct': float,
            'trend': 'up/down/stable'
        }
    """
    df = df.copy()
    df[date_column] = pd.to_datetime(df[date_column])

    time_series = df.set_index(date_column)[value_column].resample(period).sum()

    if len(time_series) >= 2:
        current = time_series.iloc[-1]
        previous = time_series.iloc[-2]
        change_pct = (current - previous) / previous * 100 if previous != 0 else 0
    else:
        current = time_series.iloc[-1]
        previous = 0
        change_pct = 0

    return {
        'current': current,
        'previous': previous,
        'change_pct': change_pct,
        'trend': 'up' if change_pct > 5 else ('down' if change_pct < -5 else 'stable')
    }
```

### 8.5 反思报告生成器

```python
def generate_reflection_report(q1_to_q7_answers):
    """
    生成结构化反思报告

    Args:
        q1_to_q7_answers: dict with keys 'q1' to 'q7'

    Returns:
        dict: reflection_report
    """
    q6_answer = q1_to_q7_answers.get('q6', '否')
    q7_answer = q1_to_q7_answers.get('q7', '否')

    overall_pass = ('是' in q6_answer and '是' in q7_answer)

    issues = []
    corrections = []

    for i in range(1, 8):
        q_key = f'q{i}'
        if q_key in q1_to_q7_answers and '否' in q1_to_q7_answers[q_key]:
            issues.append(f"Q{i} 未通过: {q1_to_q7_answers[q_key]}")
            corrections.append(f"需要修正 Q{i} 对应的问题")

    return {
        'reflection_report': {
            'q1_answer': q1_to_q7_answers.get('q1', '否'),
            'q2_answer': q1_to_q7_answers.get('q2', '否'),
            'q3_answer': q1_to_q7_answers.get('q3', '否'),
            'q4_answer': q1_to_q7_answers.get('q4', '否'),
            'q5_answer': q1_to_q7_answers.get('q5', '否'),
            'q6_answer': q6_answer,
            'q7_answer': q7_answer,
            'overall_pass': overall_pass,
            'issues_found': issues,
            'correction_actions': corrections
        }
    }
```
