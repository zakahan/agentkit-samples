---
name: "database-skill-analysis"
description: "数据分析与BI：使用自然语言生成SQL查询、执行SELECT查询并返回Pandas DataFrame，进行探索性数据分析、统计分析和可视化。当用户需要查询、分析数据时调用。"
---

# 数据分析 Skill

> **帮用户多想一步** — 不只完成任务，更提供专家洞察。

## 核心哲学

1. **先理解，后执行** — 拿到任务先问「用户真正需要什么」
2. **专家视角** — 从数据分析师视角出发，提供专业分析
3. **多想一步** — 完成后主动指出用户可能没注意到的问题、趋势或机会
4. **数据诚实** — 绝不编造数据，图表不误导
5. **结论先行** — 先说好还是不好，再说为什么

## 工作流 (Workflow)

严格遵循 [workflow.md](./workflow.md) 的 7 步流程：

1. **数据探查** (Data Exploration)
2. **数据获取** (Data Acquisition)
3. **质量检查** (Quality Check)
4. **EDA与方法论** (EDA & Methodology)
5. **结论提炼** (Conclusion)
   - *5.5 反思与验证 (Reflection)*
6. **报告生成** (Report Generation)
7. **交付与建议** (Delivery)

### 工作流管理器

每次分析**必须**使用 `AnalysisWorkflow` 管理工作区：

```python
from scripts.analysis_workflow import create_workflow

# 1. 创建工作区
wf = create_workflow()
# 输出: /path/to/workspace/analysis_20260308_143022/

# 2. 保存多数据源配置（Step 1）
wf.save_data_sources([
    {"name": "byd_sales", "type": "mysql", "instance_id": "mysql-xxx", "database": "demo"},
    {"name": "competitor", "type": "postgresql", "instance_id": "postgres-xxx", "database": "demo", "schema": "public"}
])

# 3. 保存数据获取摘要（Step 2）
wf.save_acquisition_summary({
    "sources": [
        {"source_name": "byd_sales", "sql": "...", "row_count": 15000},
        {"source_name": "competitor", "sql": "...", "row_count": 5000}
    ]
})

# 4. 获取指定数据源的数据
sales_data = wf.get_source_data("sales")

# 5. 检查断点（可选）
if wf.check_step_completed("02_acquisition"):
    raw_data = wf.load_step_output("02_acquisition", "raw_data.csv")
```

### 输出文件规范

| 步骤 | 目录 | 输出文件 |
|------|------|----------|
| 数据探查 | `01_exploration/` | `tables.json`, `schema_{table}.json` |
| 数据获取 | `02_acquisition/` | `raw_data.csv` |
| 质量检查 | `03_quality/` | `quality_report.json` |
| EDA分析 | `04_eda/` | `metrics.json`, `trends.json`, `comparison.json`, `topn.json` |
| 结论提炼 | `05_conclusion/` | `conclusion.md`, `reflection.json` |
| 报告生成 | `06_report/` | `analysis_report.html`, `analysis_report.png` |

### Checklist

- [ ] **Step 0**: 初始化工作区 `create_workflow()`
- [ ] **Step 1**: 数据探查 → 保存到 `01_exploration/`
- [ ] **Step 2**: 数据获取 → 保存到 `02_acquisition/`
- [ ] **Step 3**: 质量检查 → 保存到 `03_quality/`
- [ ] **Step 4**: EDA分析 → 保存到 `04_eda/`
- [ ] **Step 5**: 结论提炼 → 保存到 `05_conclusion/`
- [ ] **Step 6**: 报告生成 → 保存到 `06_report/`
- [ ] **Step 7**: 最终交付（展示 PNG 截图和 HTML 链接）

---

## API

详细 API 文档 → [api.md](./api.md)

---

## 数据分析示例

```python
# 销售数据分析
df = toolbox.query_sql(
    instance_id="mysql-ba85dba2cdd1",
    instance_type="MySQL",
    database="company",
    sql="SELECT date, product, sales, region FROM sales_data"
)

# 按产品统计
product_sales = df.groupby('product')['sales'].sum().sort_values(ascending=False)

# 按区域统计
region_sales = df.groupby('region')['sales'].agg(['sum', 'mean', 'count'])

# 同比增长
current = df[df['date'] >= '2024-01-01']['sales'].sum()
previous = df[df['date'] < '2024-01-01']['sales'].sum()
growth = (current - previous) / previous * 100
```

---

## 可视化与报告（必选）

**除非用户明确拒绝，否则必须基于以下规范生成 HTML 报告文件。**

### 报告风格（用户未指定时随机选择）

| 风格 | 标志元素 | 最适场景 |
|------|---------|---------|
| Financial Times | 三文鱼粉底 + 4px蓝顶线 | 金融分析 |
| McKinsey | 深蓝Header + Exhibit编号 | 战略分析 |
| The Economist | 红色thin bar | 行业洞察 |
| Swiss / NZZ | 黑白灰红 + 72px大字 | 数据展示 |

详细风格规范 → `report-style.md`

### HTML 模板

- 报告要根据用户对话语言进行定制化，支持中文、英文、日文等不同语言
- KPI看板、对比表格、趋势图表、问题诊断卡片
- 零CDN依赖（纯SVG/内联JS）
- Playwright 截图生成图片

详细模板 → `html-templates.md`

### 截图命令

```bash
playwright screenshot --full-page --path /tmp/analysis_report.png /tmp/analysis_report.html
```

---

## 注意事项

- **生成报告前必须问**：受众是谁？用途是什么？
- **可视化原则**：柱状图Y轴从0开始，条形图用绝对比例
