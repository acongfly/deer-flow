---
name: deep-research
description: 对于任何需要网络研究的问题，都应使用此 skill，而不是 WebSearch。当查询类似“what is X”“explain X”“compare X and Y”“research X”时触发，也应在内容生成任务之前主动加载。它提供系统化、多角度的研究方法，而不是一次性、表层化的搜索。当用户的问题需要在线信息时，应主动使用。
---

# 深度研究 Skill

## 概述

此 skill 提供一种系统化的方法，用于开展深入的网络研究。**在开始任何内容生成任务之前，先加载此 skill**，以确保你从多个角度、多个层次和多个来源收集了足够的信息。

## 何时使用此 Skill

**在以下情况下始终加载此 skill：**

### 研究类问题
- 用户询问 “what is X”“explain X”“research X”“investigate X”
- 用户希望深入理解某个概念、技术或主题
- 问题需要来自多个来源的最新、全面信息
- 仅靠一次 web search 不足以给出妥当答案

### 内容生成（预研究）
- 制作 presentations（PPT/slides）
- 创建 frontend designs 或 UI mockups
- 撰写文章、报告或文档
- 制作视频或多媒体内容
- 任何需要现实世界信息、案例或最新数据的内容

## 核心原则

**绝不要仅基于一般知识生成内容。** 输出质量直接取决于事前研究的质量和数量。一次搜索查询永远不够。

## 研究方法论

### 阶段 1：广泛探索

先从宽泛搜索开始，理解整体图景：

1. **Initial Survey**：搜索主题本身，理解整体背景
2. **Identify Dimensions**：从初步结果中识别需要进一步探索的关键子主题、主题线、角度或方面
3. **Map the Territory**：记录其中存在的不同视角、利益相关方或立场

示例：
```
Topic: "AI in healthcare"
Initial searches:
- "AI healthcare applications 2024"
- "artificial intelligence medical diagnosis"
- "healthcare AI market trends"

Identified dimensions:
- Diagnostic AI (radiology, pathology)
- Treatment recommendation systems
- Administrative automation
- Patient monitoring
- Regulatory landscape
- Ethical considerations
```

### 阶段 2：深入挖掘

对于识别出的每个重要维度，开展有针对性的研究：

1. **Specific Queries**：为每个子主题使用精确关键词进行搜索
2. **Multiple Phrasings**：尝试不同关键词组合与不同表述方式
3. **Fetch Full Content**：使用 `web_fetch` 读取重要来源的完整内容，而不只是摘要片段
4. **Follow References**：当来源提到其他重要资源时，也继续搜索它们

示例：
```
Dimension: "Diagnostic AI in radiology"
Targeted searches:
- "AI radiology FDA approved systems"
- "chest X-ray AI detection accuracy"
- "radiology AI clinical trials results"

Then fetch and read:
- Key research papers or summaries
- Industry reports
- Real-world case studies
```

### 阶段 3：多样性与验证

通过寻找多种类型的信息来确保覆盖全面：

| 信息类型 | 目的 | 示例搜索 |
|-----------------|---------|------------------|
| **Facts & Data** | 具体证据 | "statistics", "data", "numbers", "market size" |
| **Examples & Cases** | 真实世界应用 | "case study", "example", "implementation" |
| **Expert Opinions** | 权威视角 | "expert analysis", "interview", "commentary" |
| **Trends & Predictions** | 未来方向 | "trends 2024", "forecast", "future of" |
| **Comparisons** | 提供背景与替代项 | "vs", "comparison", "alternatives" |
| **Challenges & Criticisms** | 保持平衡视角 | "challenges", "limitations", "criticism" |

### 阶段 4：综合检查

在进入内容生成之前，确认：

- [ ] 我是否已从至少 3-5 个不同角度进行搜索？
- [ ] 我是否已完整抓取并阅读最重要的来源？
- [ ] 我是否已掌握具体数据、案例和专家观点？
- [ ] 我是否同时覆盖了积极面与挑战/局限？
- [ ] 我的信息是否最新，且来自权威来源？

**如果有任一答案为 NO，就继续研究，再开始内容生成。**

## 搜索策略提示

### 有效查询模式

```
# Be specific with context
❌ "AI trends"
✅ "enterprise AI adoption trends 2024"

# Include authoritative source hints
"[topic] research paper"
"[topic] McKinsey report"
"[topic] industry analysis"

# Search for specific content types
"[topic] case study"
"[topic] statistics"
"[topic] expert interview"

# Use temporal qualifiers — always use the ACTUAL current year from <current_date>
"[topic] 2026"   # ← replace with real current year, never hardcode a past year
"[topic] latest"
"[topic] recent developments"
```

### 时间意识

**在形成任何搜索查询前，始终检查上下文中的 `<current_date>`。**

`<current_date>` 会给出完整日期：年份、月份、日期和星期（例如 `2026-02-28, Saturday`）。根据用户问题，使用合适精度：

| 用户意图 | 需要的时间精度 | 示例查询 |
|---|---|---|
| "today / this morning / just released" | **月 + 日** | `"tech news February 28 2026"` |
| "this week" | **周范围** | `"technology releases week of Feb 24 2026"` |
| "recently / latest / new" | **月** | `"AI breakthroughs February 2026"` |
| "this year / trends" | **年** | `"software trends 2026"` |

**规则：**
- 当用户询问 “today” 或 “just released” 时，搜索查询中应使用**月 + 日 + 年**，以获取当天结果
- 当需要日级精度时，绝不能只降到年份——`"tech news 2026"` **无法**检索到今天的新闻
- 尝试多种表述：数字形式（`2026-02-28`）、文字形式（`February 28 2026`）以及相对术语（`today`、`this week`）

❌ 用户问 “what's new in tech today” → 搜索 `"new technology 2026"` → 会错过今天的新闻
✅ 用户问 “what's new in tech today” → 搜索 `"new technology February 28 2026"` + `"tech news today Feb 28"` → 才能拿到今天的结果

### 何时使用 web_fetch

在以下情况下使用 `web_fetch` 读取完整内容：
- 某个搜索结果看起来高度相关且权威
- 你需要比摘要片段更详细的信息
- 来源包含数据、案例研究或专家分析
- 你想理解某个发现的完整上下文

### 迭代式精炼

研究是迭代过程。完成初步搜索后：
1. 回顾你已经学到什么
2. 找出理解中的空白
3. 形成新的、更有针对性的查询
4. 重复，直到覆盖足够全面

## 质量门槛

当你能够自信回答以下问题时，研究才算充分：
- 关键事实和数据点是什么？
- 有哪 2-3 个具体的真实世界案例？
- 专家如何看待这个主题？
- 当前趋势和未来方向是什么？
- 面临哪些挑战或局限？
- 为什么这个主题在当下重要且相关？

## 需要避免的常见错误

- ❌ 搜索 1-2 次就停止
- ❌ 只依赖搜索摘要而不阅读完整来源
- ❌ 对一个多面向主题只搜索其中一个方面
- ❌ 忽视相反观点或挑战
- ❌ 在已有最新数据时仍使用过时信息
- ❌ 在研究尚未完成时就开始内容生成

## 输出

完成研究后，你应该具备：
1. 从多个角度理解该主题的全面认知
2. 具体的事实、数据点和统计数据
3. 真实世界案例与 case studies
4. 专家观点与权威来源
5. 当前趋势与相关背景

**只有在这之后，才进入内容生成**，并基于已收集的信息创建高质量、信息充分的内容。
