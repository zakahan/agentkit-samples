# 分析报告风格库

> 5种经实战验证的数据报告视觉风格。用户未指定时随机选择。

## 风格速查

| 风格 | 标志元素 | 最适场景 |
|------|---------|---------|
| Financial Times | 三文鱼粉底 + 4px蓝色顶线 | 金融分析、叙事报告 |
| McKinsey Consulting | 深蓝Header + Exhibit编号 | 战略分析、框架评估 |
| The Economist | 红色thin bar + editorial标题 | 行业洞察、观点报告 |
| Goldman Sachs | Rating徽章 + 金色强调 | 财务建模、估值报告 |
| Swiss / NZZ | 黑白灰红 + 72px大字 | 数据展示、设计感报告 |

---

## 风格 1：Financial Times

**色彩**：
- 页面背景：`#FFF1E5`（三文鱼粉）
- 强调蓝：`#0F5499`
- 边框：`#E0D3C3`

**设计元素**：
- 4px蓝色顶线 `#0F5499`
- 衬线标题（Georgia）+ 无衬线正文
- 关闭动画，线条2px

---

## 风格 2：McKinsey Consulting

**色彩**：
- Header：`#003366`（深蓝）
- 强调蓝：`#4472C4`
- 强调橙：`#ED7D31`

**设计元素**：
- Exhibit 编号（不是图1）
- 结论式标题（「Cloud revenue drives 60%」而非「Revenue by segment」）
- Key Takeaway 框：4px深蓝左边框 + 浅灰背景
- 无渐变、无阴影、无圆角

---

## 风格 3：The Economist

**色彩**：
- 页面背景：`#FFFFFF`
- Header标识线：`#E3120B`（6px红线）
- 强调红：`#E3120B`

**设计元素**：
- 6px红色顶线
- Editorial 标题带观点（「AI的胃口」而非「资本开支趋势」）
- Pull Quote：大号衬线字体 + 左侧红色竖线

---

## 风格 4：Goldman Sachs

**色彩**：
- Header：`#00338D`（深蓝）
- 强调金：`#D4AF37`
- 负面红：`#C62828`

**设计元素**：
- Rating 徽章：BUY(绿)/NEUTRAL(金)/SELL(红)
- Investment Thesis 框：白色卡片 + 4px金色左边框
- 密集金融表格 + 斑马纹

---

## 风格 5：Swiss / NZZ

**色彩**：
- 页面背景：`#FFFFFF`
- 主文字：`#000000`
- 强调红：`#FF0000`

**设计元素**：
- 极端字号对比：72px标题 vs 13px标签
- 黑色分隔线
- Helvetica 字体
- **禁止**：圆角、阴影、渐变、背景色块

---

## 设计规范

### 必须做
- 零CDN依赖（纯SVG/内联JS）
- 柱状图Y轴从0开始
- 条形图用绝对比例
- 辅助文字≥10pt
- 表格必须有斑马纹

### 禁止做
- CDN资源（Chart.js/ECharts）
- SVG坐标超出viewBox
- CSS absolute定位数据点
- 同一报告混用不同风格
