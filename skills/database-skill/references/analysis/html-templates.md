# HTML可视化模板

> 即用型模板，用 Playwright 截图生成高品质数据可视化图片。

**重要**：每个模板单独一个文件，生成报告时先将各模板 HTML 合并成一个完整报告，再对总报告截图。

---

## 模板列表

| 模板 | 文件 | 用途 |
|------|------|------|
| KPI看板 | [templates/template-kpi.md](./templates/template-kpi.md) | 数据概览 / 关键指标 |
| 对比表格 | [templates/template-table.md](./templates/template-table.md) | 多维度对比 |
| 柱状图 | [templates/template-bar.md](./templates/template-bar.md) | 趋势展示 / 类别对比 |
| 诊断卡片 | [templates/template-diagnosis.md](./templates/template-diagnosis.md) | 问题诊断 / 优化建议 |
| 折线图 | [templates/template-line.md](./templates/template-line.md) | 时间序列趋势 |
| 饼图/环形图 | [templates/template-pie.md](./templates/template-pie.md) | 占比分析 |
| 漏斗图 | [templates/template-funnel.md](./templates/template-funnel.md) | 转化率分析 |
| 进度条 | [templates/template-progress.md](./templates/template-progress.md) | 目标达成情况 |
| 排名榜单 | [templates/template-rank.md](./templates/template-rank.md) | TOP N 排名 |
| 多Tab报告 | [templates/template-tabs.md](./templates/template-tabs.md) | 综合报告 |
| 地图 | [templates/template-map.md](./templates/template-map.md) | 地区分布 |
| 热力图 | [templates/template-heatmap.md](./templates/template-heatmap.md) | 交叉分析 |
| 词云 | [templates/template-wordcloud.md](./templates/template-wordcloud.md) | 关键词/热词 |

---

## 使用流程

### 1. 选择模板

根据内容类型选择合适的模板：

| 内容类型 | 推荐模板 |
|----------|----------|
| 数据概览/周报开头 | KPI看板 |
| 多维度对比 | 对比表格 |
| 趋势展示 | 柱状图 / 折线图 |
| 占比分析 | 饼图/环形图 |
| 转化分析 | 漏斗图 |
| 目标达成 | 进度条 |
| 排名榜单 | 排名榜单 |
| 问题诊断 | 诊断卡片 |
| 多板块报告 | 多Tab切换 |

### 2. 填充数据

复制对应模板文件中的 HTML 代码，替换数据值和标签。

### 3. 合成总报告

将多个模板的 HTML 内容合并成一个完整的 HTML 报告：

```html
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  /* 全局样式 */
  body { margin: 0; padding: 40px; background: #F5E6D3; font-family: "PingFang SC", Arial, sans-serif; }
  .section { margin-bottom: 40px; background: #FFFDF7; border: 4px solid #1A1A1A; border-radius: 12px; padding: 30px; box-shadow: 6px 6px 0 #1A1A1A; }
</style>
</head>
<body>
  <!-- 模板1: KPI看板 -->
  <div class="section">
    <!-- KPI HTML 内容 -->
  </div>

  <!-- 模板2: 对比表格 -->
  <div class="section">
    <!-- 表格 HTML 内容 -->
  </div>

  <!-- 更多模板... -->
</body>
</html>
```

### 4. 保存到临时目录

```python
html_content = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><style>body { margin: 0; padding: 40px; background: #F5E6D3; } .section { margin-bottom: 40px; background: #FFFDF7; border: 4px solid #1A1A1A; border-radius: 12px; padding: 30px; box-shadow: 6px 6px 0 #1A1A1A; }</style></head>
<body>
  <!-- 合并各模板内容 -->
</body>
</html>
"""

# 保存到临时目录
html_file = "/tmp/analysis_report.html"
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)
```

### 5. 截图

```bash
HTML_FILE="/tmp/analysis_report.html"
PNG_FILE="${HTML_FILE%.html}.png"

npx playwright screenshot "file://${HTML_FILE}" "${PNG_FILE}" \
  --viewport-size=1200,675 \
  --full-page \
  --wait-for-timeout=3000
```

**参数说明**：
- `--full-page`：截取完整页面（而非仅视口），确保长报告完整导出
- `--wait-for-timeout=3000`：等待 3 秒，确保图表/数据加载完成
- 临时目录：使用 `/tmp/` 而非 skill 所在目录
- PNG 命名：与 HTML 文件名一致

---

## 配色速查

| 用途 | 色值 |
|------|------|
| 珊瑚（主色） | `#E17055` |
| 薄荷绿 | `#45B7AA` |
| 橄榄绿 | `#5B8C5A` |
| 金色（暗金） | `#D4A017` |
| 正面/增长 | `#4CAF50` |
| 负面/警告 | `#FF3B4F` |
| 背景奶油 | `#F5E6D3` |
| 卡片白 | `#FFFDF7` |
