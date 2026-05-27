---
name: newsletter-generation
description: 当用户请求生成、创建、撰写或起草 newsletter、邮件摘要、每周汇总、行业简报或精选内容总结时使用此 skill。支持基于主题的研究、多来源内容策展，以及适用于邮件或网页分发的专业格式。可在诸如“create a newsletter about X”“write a weekly digest”“generate a tech roundup”或“curate news about Y”之类的请求中触发。
---

# Newsletter 生成 Skill

## 概览

此 skill 生成专业、研究充分的 newsletter，将来自多个来源的精选内容与原创分析和评论结合起来。它遵循 Morning Brew、The Hustle、TLDR 和 Benedict Evans 等出版物的现代 newsletter 最佳实践，产出兼具信息性、吸引力和可操作性的内容。

输出为完整、可直接发布的 Markdown 格式 newsletter，适用于邮件分发平台、网页发布或转换为 HTML。

## 核心能力

- 研究并策展指定主题的多来源网页内容
- 生成聚焦单一主题或多主题、且语气一致的 newsletter
- 撰写吸引人的标题、摘要和原创评论
- 为最佳可读性和快速浏览而组织内容
- 支持多种 newsletter 形式（日报摘要、每周汇总、深度解读、行业简报）
- 包含相关链接、来源和署名
- 根据目标受众调整语气和风格（技术型、高管型、泛大众）
- 生成具有一致品牌风格和结构的连续 newsletter 系列

## 何时使用此 Skill

**在以下情况下始终加载此 skill：**

- 用户要求生成 newsletter、邮件摘要或内容汇总
- 用户请求对某个主题的新闻或进展进行精选总结
- 用户想创建一个可复用的 newsletter 模板/系列
- 用户要求将某一领域的近期进展整理成简报
- 用户需要一个格式化好的、可直接用于邮件的多条目精选内容
- 用户要求“weekly roundup”“monthly digest”或“morning briefing”

## Newsletter 工作流

### 阶段 1：规划

#### 步骤 1.1：理解 Newsletter 需求

识别关键参数：

| 参数 | 说明 | 默认值 |
|-----------|-------------|---------|
| **主题** | 要覆盖的主要主题领域 | 必需 |
| **形式** | 日报摘要、每周汇总、深度解读或行业简报 | 每周汇总 |
| **目标受众** | 技术型、高管型、泛大众或细分社区 | 泛大众 |
| **语气** | 专业、对话式、风趣或分析型 | 对话式-专业 |
| **长度** | 短（5 分钟阅读）、中（10 分钟）、长（15 分钟以上） | 中等 |
| **栏目** | 内容栏目数量与类型 | 4-6 个栏目 |
| **发布频率背景** | 一次性内容还是系列中的一期 | 一次性 |

#### 步骤 1.2：定义 Newsletter 结构

根据形式选择合适结构：

**日报摘要结构**：
```
1. Top Story (1 item, detailed)
2. Quick Hits (3-5 items, brief)
3. One Stat / Quote of the Day
4. What to Watch
```

**每周汇总结构**：
```
1. Editor's Note / Intro
2. Top Stories (2-3 items, detailed)
3. Trends & Analysis (1-2 items, original commentary)
4. Quick Bites (4-6 items, brief summaries)
5. Tools & Resources (2-3 items)
6. One More Thing / Closing
```

**深度解读结构**：
```
1. Introduction & Context
2. Background / Why It Matters
3. Key Developments (detailed analysis)
4. Expert Perspectives
5. What's Next / Implications
6. Further Reading
```

**行业简报结构**：
```
1. Executive Summary
2. Market Developments
3. Company News & Moves
4. Product & Technology Updates
5. Regulatory & Policy Changes
6. Data & Metrics
7. Outlook
```

### 阶段 2：研究与策展

#### 步骤 2.1：多来源研究

使用 web search 进行充分研究。**newsletter 的质量直接取决于研究的质量和时效性。**

**搜索策略**：

```
# Current news and developments
"[topic] news [current month] [current year]"
"[topic] latest developments"
"[topic] announcement this week"

# Trends and analysis
"[topic] trends [current year]"
"[topic] analysis expert opinion"
"[topic] industry report"

# Data and statistics
"[topic] statistics [current year]"
"[topic] market data latest"
"[topic] growth metrics"

# Tools and resources
"[topic] new tools [current year]"
"[topic] open source release"
"best [topic] resources [current year]"
```

> **重要**：始终检查 `<current_date>`，确保搜索查询使用正确的时间上下文。不要使用硬编码年份。

#### 步骤 2.2：来源评估与选择

评估每个来源并精选最佳内容：

| 标准 | 优先级 |
|-----------|----------|
| **时效性** | 优先选择最近 7-30 天内的内容 |
| **权威性** | 优先一手来源、官方公告、成熟出版物 |
| **独特性** | 选择能提供新视角或报道较少的故事 |
| **相关性** | 每个条目都必须明确关联到 newsletter 的既定主题 |
| **可操作性** | 优先读者可以采取行动的内容（工具、洞见、策略） |
| **多样性** | 混合新闻、分析、数据和实用资源 |

#### 步骤 2.3：深度内容提取

对于关键故事，使用 `web_fetch` 阅读完整文章并提取：

1. **核心事实** —— 发生了什么、涉及谁、何时发生
2. **背景上下文** —— 为什么重要、背景信息
3. **数据点** —— 具体数字、指标或统计
4. **引述** —— 相关专家引述或官方声明
5. **影响** —— 这对读者意味着什么

### 阶段 3：写作

#### 步骤 3.1：Newsletter 头部

每份 newsletter 都以一致的头部开始：

```markdown
# [Newsletter Name]

*[Tagline or description] — [Date]*

---

[Optional: One-sentence preview of what's inside]
```

#### 步骤 3.2：栏目写作指南

**Top Stories / Featured Items**：
- **标题**：有吸引力、清晰、强调收益（不是标题党）
- **钩子**：让读者在开头 1-2 句就觉得值得继续读
- **正文**：关键事实和背景（2-4 段）
- **Why it matters**：与读者的世界建立联系（1 段）
- **来源链接**：始终注明并链接到原始来源

**Quick Bites / Brief Items**：
- **格式**：加粗标题 + 2-3 句摘要 + 来源链接
- **重点**：每条只传达一个关键结论
- **效率**：读者不点开链接也应获得核心洞见

**分析 / 评论栏目**：
- **声音**：newsletter 对趋势或进展的独特视角
- **结构**：观察 → 背景 → 影响 → （可选）可执行结论
- **证据**：每条说法都要有数据或来源支撑

#### 步骤 3.3：写作标准

| 原则 | 实施方式 |
|-----------|---------------|
| **易于浏览** | 使用标题、加粗、项目符号和短段落 |
| **有吸引力** | 先写最有趣的角度，而不是按时间顺序罗列 |
| **简洁** | 每一句都要有存在价值——毫不留情地删掉废话 |
| **准确** | 每个事实都有来源，每个数字都经过核实 |
| **署名明确** | 始终通过行内链接标注原始来源 |
| **像人写的** | 像一位见多识广的朋友，而不是新闻稿 |

**根据受众校准语气**：

| 受众 | 语气 | 示例 |
|----------|------|---------|
| **技术型** | 精确，不解释行话，默认读者具备专业知识 | "The new API supports gRPC streaming with backpressure handling via flow control windows." |
| **高管型** | 聚焦影响、结果导向、强调战略性 | "This acquisition gives Company X a 40% market share in the enterprise segment, directly threatening Incumbent Y's pricing power." |
| **泛大众** | 易懂，使用类比，解释概念 | "Think of it like a universal translator for data — it lets any app talk to any database without learning a new language." |

### 阶段 4：组装与润色

#### 步骤 4.1：组装 Newsletter

按照所选结构模板，将所有栏目整合为最终文档。

#### 步骤 4.2：页脚

每份 newsletter 结尾都要包含：

```markdown
---

*[Newsletter Name] is [description of what it is].*
*[How to subscribe/share/give feedback]*

*Sources: All links are provided inline. This newsletter curates and summarizes
publicly available information with original commentary.*
```

#### 步骤 4.3：质量检查清单

定稿前，确认：

- [ ] **每个事实性陈述都有来源链接** —— 不要有无来源断言
- [ ] **所有链接都可用** —— 使用搜索结果中已验证的 URL
- [ ] **日期引用使用真实当前日期** —— 不要写死或假定日期
- [ ] **内容是最新的** —— 所有主要条目都在预期时间范围内
- [ ] **没有重复故事** —— 每个条目只出现一次
- [ ] **格式一致** —— 标题、列表、链接风格全篇统一
- [ ] **覆盖平衡** —— 不被单一来源或视角主导
- [ ] **长度合适** —— 符合指定的长度目标
- [ ] **开头足够吸引人** —— 前 2 句话能让读者愿意继续读
- [ ] **结尾清晰** —— newsletter 以令人难忘或可执行的结语收束
- [ ] **已校对** —— 没有错别字、格式损坏或残缺句子

## Newsletter 输出模板

```markdown
# [Newsletter Name]

*[Tagline] — [Full date, e.g., April 4, 2026]*

---

[Preview sentence: "This week: [topic 1], [topic 2], and [topic 3]."]

## 🔥 Top Stories

### [Headline 1]

[Hook — why this matters in 1-2 sentences.]

[Body — 2-4 paragraphs covering key facts, context, and implications.]

**Why it matters:** [1 paragraph connecting to reader's interests or industry impact.]

📎 [Source: Publication Name](URL)

### [Headline 2]

[Same structure as above]

## 📊 Trends & Analysis

### [Trend Title]

[Original commentary on an emerging trend, backed by data from research.]

[Key data points presented clearly — consider inline stats or a brief comparison.]

**The bottom line:** [One-sentence takeaway.]

## ⚡ Quick Bites

- **[Headline]** — [2-3 sentence summary with key takeaway.] [Source](URL)
- **[Headline]** — [2-3 sentence summary.] [Source](URL)
- **[Headline]** — [2-3 sentence summary.] [Source](URL)
- **[Headline]** — [2-3 sentence summary.] [Source](URL)

## 🛠️ Tools & Resources

- **[Tool/Resource Name]** — [What it does and why it's useful.] [Link](URL)
- **[Tool/Resource Name]** — [Description.] [Link](URL)

## 💬 One More Thing

[Closing thought, insightful quote, or forward-looking statement.]

---

*[Newsletter Name] curates the most important [topic] news and analysis.*
*Found this useful? Share it with a colleague.*

*All sources are linked inline. Views and commentary are original.*
```

## 适配示例

### 技术 Newsletter
- Emoji 使用：✅ 适中（栏目标题中使用）
- 栏目：Top Stories、Deep Dive、Quick Bites、Open Source Spotlight、Dev Tools
- 语气：技术型-对话式

### 商业/金融 Newsletter
- Emoji 使用：❌ 极少或不用
- 栏目：Market Overview、Deal Flow、Company News、Data Corner、Outlook
- 语气：专业型-分析式

### 垂直行业 Newsletter
- Emoji 使用：适中
- 栏目：Regulatory Updates、Market Data、Innovation Watch、People Moves、Events
- 语气：专家型-权威式

### 创意/营销 Newsletter
- Emoji 使用：✅ 较多
- 栏目：Campaign Spotlight、Trend Watch、Viral This Week、Tools We Love、Inspiration
- 语气：热情型-专业式

## 输出处理

生成后：

- 将 newsletter 保存到 `/mnt/user-data/outputs/newsletter-{topic}-{date}.md`
- 使用 `present_files` tool 将 newsletter 展示给用户
- 提供调整栏目、语气、长度或重点方向的选项
- 如果用户想要 HTML 输出，说明该 Markdown 可使用标准工具转换

## 说明

- 对于需要深入分析的 newsletter，此 skill 与 `deep-research` skill 搭配使用效果最佳——请同时加载两者
- 搜索时的时间上下文以及 newsletter 中的日期引用，始终使用 `<current_date>`
- 对于连续发布的 newsletter，建议保持一致结构，以便读者形成预期
- 策展时，质量胜过数量——5 条优秀内容胜过 15 条平庸内容
- 正确标注所有内容来源——newsletter 通过透明来源建立信任
- 避免总结读者无法访问的付费墙内容
- 如果用户提供了希望纳入的特定 URL 或文章，请与策展结果一起整合进去
- newsletter 的摘要本身应足够有价值，让读者即使不点开每个链接也能受益
