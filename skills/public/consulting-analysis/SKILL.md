---
name: consulting-analysis
description: 当用户请求生成、创建或撰写专业研究报告时使用此 skill，报告类型包括但不限于市场分析、消费者洞察、品牌分析、财务分析、行业研究、竞争情报、投资尽调或任何咨询级分析报告。此 skill 分两个阶段运行——（1）生成结构化分析框架，包括章节骨架、数据查询需求和分析逻辑；（2）在其他 skills 完成数据收集后，产出最终的咨询级报告，包含结构化叙述、嵌入图表和战略洞察。
---

# 专业研究报告 Skill

## 概述

此 skill 用于生成专业、咨询级的 Markdown 研究报告，覆盖**市场分析、消费者洞察、品牌战略、财务分析、行业研究、竞争情报、投资研究以及宏观经济分析**等领域。它分两个明确阶段运行：

1. **Phase 1 — Analysis Framework Generation**：给定研究主题，产出严谨的分析框架，包括章节骨架、各章节数据需求、分析逻辑以及可视化计划。
2. **Phase 2 — Report Generation**：在其他 skills 完成数据收集后，将所有输入综合成一份最终润色完成的报告。

输出遵循 McKinsey/BCG 风格标准。报告语言遵循 `output_locale` 设置（默认：中文 `zh_CN`）。

## 数据真实性协议

**严格遵守规则**：报告中呈现的所有数据以及图表中的所有数据，**必须**直接来源于提供的 **Data Summary** 或 **External Search Findings**。
- **禁止幻觉**：不要编造、估算或模拟数据。如果缺失数据，应写明“Data not available”，而不是伪造数字。
- **来源可追溯**：每一个重要主张和每一张图表都必须可追溯到输入数据包。

## 核心能力

- 仅根据研究主题与范围，从零设计分析框架
- 将原始数据转化为结构化、高深度研究报告
- 在每个小节中遵循 **“Visual Anchor → Data Contrast → Integrated Analysis”** 流程
- 按 **“Data → User Psychology → Strategy Implication”** 链路产出洞察
- 嵌入预生成图表并构建对比表
- 生成符合 **GB/T 7714-2015** 标准的行内引用
- 按 `output_locale` 指定语言输出专业咨询风格报告
- 根据领域（营销、金融、行业等）调整分析深度与结构

## 何时使用此 Skill

**在以下情况下始终加载此 skill：**

- 用户要求市场分析、消费者洞察报告、财务分析、行业研究，或任意咨询级分析报告
- 用户提供研究主题，并在数据收集前需要结构化分析框架
- 用户提供数据摘要、分析框架或图表文件，需要综合成报告
- 用户需要专业咨询风格的研究报告
- 任务涉及将研究发现转化为结构化战略叙事

---

# Phase 1：分析框架生成

## 目的

给定一个**研究主题**（例如 “Gen-Z Skincare Market Analysis”“NEV Industry Competitive Landscape”“Brand X Consumer Profiling”），生成一份完整的**分析框架**，作为后续数据收集与最终报告生成的蓝图。

## Phase 1 输入

| 输入 | 说明 | 必填 |
|-------|-------------|----------|
| **Research Subject** | 要分析的主题或问题 | 是 |
| **Scope / Constraints** | 地理范围、时间范围、行业细分、目标受众等 | 可选 |
| **Specific Angles** | 用户希望重点探索的特定角度或假设 | 可选 |
| **Domain** | 分析领域：市场、金融、行业、品牌、消费者、投资等 | 推断获得 |

## Phase 1 工作流

### 步骤 1.1：理解研究主题

- 解析研究主题，识别**核心实体**（市场、品牌、产品、行业、消费者群体、金融工具等）
- 识别**分析领域**（营销、金融、行业、竞争、消费者、投资、宏观等）
- 根据领域确定其**自然分析维度**：

| 领域 | 典型维度 |
|--------|--------------------|
| Market Analysis | 市场规模、增长趋势、市场细分、增长驱动因素、竞争格局、消费者画像 |
| Brand Analysis | 品牌定位、市场份额、消费者感知、营销策略、竞品对比 |
| Consumer Insights | 人口画像、购买行为、决策旅程、痛点、场景分析 |
| Financial Analysis | 宏观环境、行业趋势、公司基本面、财务指标、估值、风险评估 |
| Industry Research | 价值链分析、市场规模、竞争格局、政策环境、技术趋势、进入壁垒 |
| Investment Due Diligence | 商业模式、财务健康度、管理层评估、市场机会、风险因素、退出路径 |
| Competitive Intelligence | 竞争对手识别、战略对比、SWOT 分析、差异化定位、市场动态 |

### 步骤 1.2：选择分析框架与模型

基于识别出的领域和研究主题，选择**一个或多个**专业分析框架，用于组织每一章中的推理结构。所选框架将指导章节骨架中的**Analysis Logic**（步骤 1.3）。

#### 战略与环境分析

| 框架 | 说明 | 最适用场景 |
|-----------|-------------|----------|
| **SWOT Analysis** | 优势、劣势、机会、威胁 | 品牌评估、竞争定位、战略规划 |
| **PEST / PESTEL Analysis** | 政治、经济、社会、技术（+ 环境、法律） | 宏观环境扫描、市场进入评估、政策影响分析 |
| **Porter's Five Forces** | 供应商议价力、买方议价力、新进入者威胁、替代品威胁、行业竞争强度 | 行业竞争格局、进入壁垒评估、利润率分析 |
| **Porter's Diamond Model** | 要素条件、需求条件、相关产业、企业战略与结构 | 国家/区域竞争优势分析 |
| **VRIO Analysis** | 价值、稀缺性、难模仿性、组织性 | 核心能力评估、资源优势分析 |

#### 市场与增长分析

| 框架 | 说明 | 最适用场景 |
|-----------|-------------|----------|
| **STP Analysis** | 细分、目标、定位 | 市场细分、目标市场选择、品牌定位 |
| **BCG Matrix (Growth-Share Matrix)** | 明星、现金牛、问题、瘦狗 | 产品组合管理、资源配置决策 |
| **Ansoff Matrix** | 市场渗透、市场开发、产品开发、多元化 | 增长战略选择 |
| **Product Life Cycle (PLC)** | 导入、增长、成熟、衰退 | 产品战略制定、市场时机判断 |
| **TAM-SAM-SOM** | 总市场 / 可服务市场 / 可获取市场 | 市场规模测算、机会量化 |
| **Technology Adoption Lifecycle** | Innovators → Early Adopters → Early Majority → Late Majority → Laggards | 新兴技术/品类渗透分析 |

#### 消费者与行为分析

| 框架 | 说明 | 最适用场景 |
|-----------|-------------|----------|
| **Consumer Decision Journey** | 认知 → 考虑 → 评估 → 购买 → 忠诚 | 消费者行为路径映射、触点优化 |
| **AARRR Funnel (Pirate Metrics)** | Acquisition、Activation、Retention、Revenue、Referral | 用户增长分析、转化率优化 |
| **RFM Model** | 最近一次、频率、金额 | 客户价值分层、精准营销 |
| **Maslow's Hierarchy of Needs** | 生理 → 安全 → 社交 → 尊重 → 自我实现 | 消费者心理分析、产品价值主张 |
| **Jobs-to-be-Done (JTBD)** | 用户在特定情境下需要完成的“工作” | 需求洞察、产品创新方向 |

#### 财务与估值分析

| 框架 | 说明 | 最适用场景 |
|-----------|-------------|----------|
| **DuPont Analysis** | ROE = 净利率 × 资产周转率 × 权益乘数 | 盈利能力拆解、财务健康诊断 |
| **DCF (Discounted Cash Flow)** | 自由现金流折现 | 企业/项目估值 |
| **Comparable Company Analysis** | PE、PB、PS、EV/EBITDA 可比倍数对比 | 相对估值、同业基准对比 |
| **EVA (Economic Value Added)** | 税后营业利润 - 资本成本 | 价值创造能力评估 |

#### 竞争与战略定位

| 框架 | 说明 | 最适用场景 |
|-----------|-------------|----------|
| **Benchmarking** | 关键指标逐项对比 | 竞品差距分析、最佳实践识别 |
| **Strategic Group Mapping** | 按两个关键维度聚类竞争者 | 竞争格局可视化、空白机会识别 |
| **Value Chain Analysis** | 主活动 + 支撑活动价值拆解 | 成本优势来源、差异化机会识别 |
| **Blue Ocean Strategy** | 价值曲线、四动作框架（Eliminate-Reduce-Raise-Create） | 差异化创新、新市场空间创造 |
| **Perceptual Mapping** | 沿两项消费者感知维度绘制品牌位置 | 品牌定位分析、市场空隙发现 |

#### 行业与供应链分析

| 框架 | 说明 | 最适用场景 |
|-----------|-------------|----------|
| **Industry Value Chain** | 上游 → 中游 → 下游拆解 | 行业结构理解、利润分布分析 |
| **Gartner Hype Cycle** | 技术触发 → 期望膨胀顶峰 → 幻灭低谷 → 启蒙坡 → 生产力平台 | 新兴技术成熟度评估 |
| **GE-McKinsey Matrix** | 行业吸引力 × 竞争实力 | 业务组合优先级、投资决策 |

#### 选择原则

1. **领域优先**：根据步骤 1.1 识别出的领域，从上述工具箱中选择**2-4 个**最相关框架
2. **互补性**：选择互补而非重叠的框架（例如宏观层面的 PESTEL + 微观层面的 Porter's Five Forces）
3. **深度优先于广度**：深度运用 2 个框架，好过浅层堆叠 6 个
4. **数据可行性**：所选框架必须能被后续数据收集 skills 支撑——如果某框架所需数据无法合理获得，应降级或替换
5. **显式映射**：在章节骨架中，明确标注每一章使用了哪个框架以及如何应用

#### 框架选择输出格式

```markdown
## Framework Selection

| Chapter | Selected Framework(s) | Application |
|---------|----------------------|-------------|
| Market Size & Growth Trends | TAM-SAM-SOM + Product Life Cycle | TAM-SAM-SOM to quantify market space, PLC to determine market stage |
| Competitive Landscape Assessment | Porter's Five Forces + Strategic Group Mapping | Five Forces to assess industry competition intensity, Group Mapping to visualize competitive positioning |
| Consumer Profiling | RFM + Consumer Decision Journey | RFM to segment customer value, Decision Journey to identify key conversion nodes |
| Brand Strategy Recommendations | SWOT + Blue Ocean Strategy | SWOT to summarize overall landscape, Blue Ocean to guide differentiation direction |
```

### 步骤 1.3：设计章节骨架

生成层级化章节结构。每一章都必须包含：

1. **Chapter Title** —— 专业、简洁、基于主题（遵循“格式”章节中的标题约束）
2. **Analysis Objective** —— 本章意图揭示什么
3. **Analysis Logic** —— 推理链或分析框架（必须引用步骤 1.2 选定的框架）
4. **Core Hypothesis** —— 需要通过数据验证或证伪的初步假设

#### 章节骨架输出格式

```markdown
## Analysis Framework

### Chapter 1: [Title]
- **Analysis Objective**: [This chapter aims to...]
- **Analysis Logic**: [Framework or reasoning chain used]
- **Core Hypothesis**: [Hypotheses to validate]
- **Data Requirements**: (see Step 1.4)
- **Visualization Plan**: (see Step 1.5)

### Chapter 2: [Title]
...
```

### 步骤 1.4：为每一章定义数据查询需求

对于每一章，明确说明**具体需要收集哪些数据**。这是连接后续数据收集 skills 的桥梁。

每条数据需求必须包含：

| 字段 | 说明 |
|-------|-------------|
| **Data Metric** | 所需的具体指标或数据点（例如：“China skincare market size 2020-2025 (in billion CNY)”） |
| **Data Type** | Quantitative、Qualitative 或 Mixed |
| **Suggested Sources** | 建议来源类别：行业报告、财务报表、政府统计、社交媒体、电商平台、调研数据、新闻 |
| **Search Keywords** | 面向数据收集 agents 的建议搜索词 |
| **Priority** | P0（必需）/ P1（重要）/ P2（补充） |
| **Time Range** | 数据应覆盖的时间范围 |

#### 数据需求输出格式（按章节）

```markdown
#### Data Requirements

| # | Data Metric | Data Type | Suggested Sources | Search Keywords | Priority | Time Range |
|---|-------------|-----------|-------------------|-----------------|----------|------------|
| 1 | Market size (billion CNY) | Quantitative | Industry reports, government statistics | "China skincare market size 2024" | P0 | 2020-2025 |
| 2 | CAGR | Quantitative | Industry reports | "skincare CAGR growth rate" | P0 | 2020-2025 |
| 3 | Sub-category share | Quantitative | E-commerce platforms, industry reports | "skincare category share cream serum sunscreen" | P1 | Latest |
| 4 | Policy & regulatory updates | Qualitative | Government announcements, news | "cosmetics regulation 2024" | P2 | Past 1 year |
```

### 步骤 1.5：为每一章定义可视化与内容结构

对于每一章，明确最终报告中的**计划可视化**与**内容结构**：

| 字段 | 说明 |
|-------|-------------|
| **Visualization Type** | 图表类型：折线图、柱状图、饼图、散点图、雷达图、热力图、桑基图、对比表等 |
| **Visualization Title** | 图表的描述性标题 |
| **Visualization Data Mapping** | 哪些数据指标映射到 X/Y 轴或分段 |
| **Comparison Table Design** | 数据对比表的列头与对比维度 |
| **Argument Structure** | 计划中的 “What → Why → So What” 叙事结构 |

#### 可视化计划输出格式（按章节）

```markdown
#### Visualization & Content Plan

**Chart 1**: [Type] — [Title]
- X-axis: [Dimension], Y-axis: [Metric]
- Data source: Corresponds to Data Requirement #1, #2

**Comparison Table**:
| Dimension | Item A | Item B | Item C |
|-----------|--------|--------|--------|

**Argument Structure**:
1. **Observation (What)**: [Surface phenomenon revealed by data]
2. **Attribution (Why)**: [Driving factors or underlying causes]
3. **Implication (So What)**: [Strategic implications or recommended actions]
```

### 步骤 1.6：输出完整分析框架

将所有输出组装成一份结构化的**Analysis Framework Document**：

```markdown
# [Research Subject] Analysis Framework

## Research Overview
- **Research Subject**: [...]
- **Scope**: [Geography, time range, industry segment]
- **Analysis Domain**: [Market / Finance / Industry / Brand / Consumer / ...]
- **Core Research Questions**: [1-3 key questions]

## Framework Selection

| Chapter | Selected Framework(s) | Application |
|---------|----------------------|-------------|
| ... | ... | ... |

## Chapter Skeleton

### 1. [Chapter Title]
- **Analysis Objective**: [...]
- **Analysis Logic**: [...]
- **Core Hypothesis**: [...]

#### Data Requirements
| # | Data Metric | Data Type | Suggested Sources | Search Keywords | Priority | Time Range |
|---|-------------|-----------|-------------------|-----------------|----------|------------|
| ... | ... | ... | ... | ... | ... | ... |

#### Visualization & Content Plan
[Chart plan + Comparison table design + Argument structure]

### 2. [Chapter Title]
...

### N. [Chapter Title]
...

## Data Collection Task List
[Consolidate all P0/P1 data requirements across chapters into a structured task list for downstream data collection skills to execute]
```

## Phase 1 质量检查清单

- [ ] 分析框架覆盖了该领域的所有自然分析维度
- [ ] 已选择 2-4 个专业分析框架，并明确映射到各章节
- [ ] 选定框架彼此互补（不重叠）且数据可行
- [ ] 每章都有清晰的 Analysis Objective、Analysis Logic（引用所选框架）和 Core Hypothesis
- [ ] 数据需求具体、可衡量，并包含搜索关键词
- [ ] 每章至少有一个可视化计划
- [ ] 数据优先级（P0/P1/P2）分配合理
- [ ] 框架具备可执行性——数据收集 agent 可以直接根据 Search Keywords 开始工作
- [ ] Data Collection Task List 完整且去重

---

# Phase 1→2 交接：数据收集与图表生成

在分析框架生成之后，它将交给**其他数据收集 skills**（例如 deep-research、data-analysis、web search agents）去完成以下工作：

1. 执行各章节数据需求中的 **Search Keywords**
2. 收集量化数据、定性洞察以及来源 URL
3. 根据 **Visualization & Content Plan** 生成图表
4. 返回一个 **Data Package**，其中包含：
   - **Data Summary**：按章节整理的原始数字、指标和定性发现
   - **Chart Files**：已生成图表图片及其本地文件路径
   - **External Search Findings**：用于引用的来源 URL 与摘要

> **此 skill 不负责数据收集。** 它只负责产出框架（Phase 1）与最终报告（Phase 2）。
>
> **Chart Generation**：如果有可用的可视化/制图 skill（例如 data-analysis、image-generation），图表生成也可以延后到 Phase 2 的开头执行——见步骤 2.3。

---

# Phase 2：报告生成

## 目的

接收上游提供的完整 **Analysis Framework** 和 **Data Package**，并将其综合成最终的咨询级报告。

## Phase 2 输入

| 输入 | 说明 | 必填 |
|-------|-------------|----------|
| **Analysis Framework** | Phase 1 产出的框架文档 | 是 |
| **Data Summary** | 数据收集阶段按章节整理的数据 | 是 |
| **Chart Files** | 已生成图表图片的本地文件路径。如果未提供，则在步骤 2.3 中使用可用的可视化 skills 生成 | 可选 |
| **External Search Findings** | 行内引用所需的 URL 与摘要 | 可选 |

## Phase 2 工作流

### 步骤 2.1：接收并校验输入

确认所有必需输入均已提供：

1. **Analysis Framework** —— 确认其中包含章节骨架、数据需求和可视化计划
2. **Data Summary** —— 确认其中按章节组织了数据，并与 P0 需求交叉核对
3. **Chart Files** —— 确认文件路径为有效本地路径

如果缺少任何 P0 数据，应在报告中标注并提示用户。

### 步骤 2.2：映射报告结构

根据 Analysis Framework 映射最终报告结构：

1. **Abstract** —— 包含关键结论的执行摘要
2. **Introduction** —— 背景、目标、方法论
3. **Main Body Chapters (2...N)** —— 映射自 Framework 中的章节骨架
4. **Conclusion** —— 纯粹、客观的综合结论
5. **References** —— 按 **GB/T 7714-2015** 格式编排的参考文献

### 步骤 2.3：生成章节图表（报告前可视化）

在编写报告之前，根据 Analysis Framework 中的 **Visualization & Content Plan** 生成所有计划图表。这样可确保每个小节在开始叙述前都具备自己的“Visual Anchor”。

#### 何时执行此步骤

- **已提供 Chart Files**：跳过此步骤——直接进入步骤 2.4。
- **未提供 Chart Files，但有可用的可视化 skill**：执行此步骤，先生成全部图表。
- **既没有 Chart Files，也没有可用的可视化 skill**：跳过此步骤——在步骤 2.4 中以对比表作为主要视觉锚点，并说明缺少图表。

#### 图表生成工作流

1. **提取图表任务**：解析 Analysis Framework 中全部 `Visualization & Content Plan` 条目，构建图表生成任务清单：

| # | 章节 | 图表类型 | 图表标题 | 数据映射 | 数据来源 |
|---|---------|------------|-------------|--------------|-------------|
| 1 | 2.1 | 折线图 | 2020-2025 市场规模趋势 | X：Year，Y：Market Size (billion CNY) | Data Requirement #1, #2 |
| 2 | 3.1 | 饼图 | 消费者年龄分布 | 分段：Age groups，数值：Share % | Data Requirement #5 |
| ... | ... | ... | ... | ... | ... |

2. **准备图表数据**：对于每个图表任务，从 **Data Summary** 中提取对应数据点。
   > **关键要求**：只使用 Data Summary 中提供的数字。不要为了让图表“更好看”而编造或“平滑”数据。如果缺少数据点，图表必须反映这一现实（例如折线中断、缺失柱），或调整图表类型。

3. **委托给可视化 Skill**：为每个图表任务调用可用的可视化/制图 skill（例如 `data-analysis`），并传入：
   - 图表类型与标题
   - 结构化数据
   - 坐标轴标签与格式偏好
   - 输出文件路径约定：`charts/chapter_{N}_{chart_index}.png`

4. **收集图表文件路径**：记录步骤 2.4 中嵌入所需的全部图表路径：

```markdown
## Generated Charts
| # | Chapter | Chart Title | File Path |
|---|---------|-------------|-----------|
| 1 | 2.1 | Market Size Trend 2020-2025 | charts/chapter_2_1.png |
| 2 | 3.1 | Consumer Age Distribution | charts/chapter_3_1.png |
```

5. **校验**：确认所有 P0 优先级图表都已生成。如有任何图表生成失败，应记录下来，并在对应小节回退为对比表。

> **原则**：在开始写报告前完成**全部**图表生成。这样可以保证视觉叙事一致，避免边生成边写作。

### 步骤 2.4：撰写报告

对于每个小节，遵循 **“Visual Anchor → Data Contrast → Integrated Analysis”** 流程：

1. **Visual Evidence Block**：使用 `![Image Description](Actual_File_Path)` 嵌入图表——使用步骤 2.3 收集到的文件路径
2. **Data Contrast Table**：为关键指标创建 Markdown 对比表
   > **来源规则**：表中的每个数字都必须来自 Data Summary。禁止幻觉。
3. **Integrated Narrative Analysis**：按 “What → Why → So What” 编写分析文本
   > **叙事规则**：叙述必须解释*已提供*的数据。不得提出输入无法支撑的主张。

每个小节结尾都必须有一段有力度的分析段落（至少 200 词），该段落应：
- 综合相互冲突或相互强化的数据点
- 揭示底层用户张力或机会
- 可选地以一个有力的 “One-Liner Truth” 作为结尾，并使用 blockquote（`>`）呈现

### 步骤 2.5：最终结构自检

输出前，确认报告**按顺序包含以下全部部分**：

```
Abstract → 1. Introduction → 2...N. Body Chapters → N+1. Conclusion → N+2. References
```

此外还需验证：
- 步骤 2.3 生成的所有图表都嵌入到了正确的小节中
- `![](path)` 引用中的图表路径有效
- 没有图表的小节使用对比表作为视觉锚点

报告**绝不能**在 Conclusion 后结束——最后一节**必须**是 References。

## 格式与语气标准

### 咨询风格
- **Tone**：McKinsey/BCG —— 权威、客观、专业
- **Language**：所有标题和正文都使用 `output_locale` 指定的语言
- **Number Formatting**：千位分隔符使用英文逗号（`1,000` 而不是 `1，000`）
- **数据强调**：用 **Bold** 突出重要观点和关键数字

### 标题约束
- **编号**：使用标准编号（`1.`、`1.1`），并紧跟标题
- **禁止前缀**：不要使用 “Chapter”“Part”“Section” 作为前缀
- **允许的语气词**：Analysis、Profiling、Overview、Insights、Assessment
- **禁用词**：“Decoding”“DNA”“Secrets”“Mindscape”“Solar System”“Unlocking”

### 小节结论
- **要求**：每个小节结尾都要有一段有力度的分析段落（至少 200 词）。
- **叙事流**：这段文字必须像正文的自然延续，应将本节发现综合为一个战略判断。
- **内容逻辑**：
    1. 综合上方相互冲突或相互强化的数据点。
    2. 揭示*底层*的用户张力或机会。
    3. Key Insight：**可选**：只有在你确实有一句简洁有力的 “One-Liner Truth” 时，才在最后使用 **Blockquote**（`>`）锚定这一节。

### 洞察深度（“So What” 链）

每个洞察都必须连接 **Data → User Psychology → Strategy Implication**：

```
❌ Bad: "Females are 60%. Strategy: Target females."

✅ Good: "Females constitute 60% with a high TGI of 180. **This suggests**
   the purchase decision is driven by aesthetic and social validation
   rather than pure utility. **Consequently**, media spend should pivot
   towards visual-heavy platforms (e.g., RED/Instagram) to maximize CTR,
   treating male audiences only as a secondary gift-giving segment."
```

### 参考文献
- **行内**：使用 External Search Findings 时，来源请用 Markdown 链接表示（例如 `[Source Title](URL)`）
- **References section**：严格按 **GB/T 7714-2015** 格式编排

### Markdown 规则
- **直接开始**：直接以 `# Report Title` 开头——不要有引言文字
- **禁止分隔线**：不要使用水平分隔线（`---`）

## 报告结构模板

```markdown
# [Report Title]

## Abstract
[Executive summary with key takeaways]

## 1. Introduction
[Background, objectives, methodology]

## 2. [Body Chapter Title]
### 2.1 [Sub-chapter Title]
![Chart Description](chart_file_path)

| Metric | Brand A | Brand B |
|--------|---------|--------|
| ... | ... | ... |

[Integrated narrative analysis: What → Why → So What, min. 200 words]

> [Optional: One-liner strategic truth]

### 2.2 [Sub-chapter Title]
...

## N+1. Conclusion
[Pure objective synthesis, NO bullet points, neutral tone]
[Para 1: The fundamental nature of the group/market]
[Para 2: Core tension or behavior pattern]
[Final: One or two sentences stating the objective truth]

## N+2. References
[1] Author. Title[EB/OL]. URL, Date.
[2] ...
```

## 完整示例

### Phase 1 示例：框架生成

用户提供：研究主题 “Gen-Z Skincare Market Analysis”

**Phase 1 输出（Analysis Framework）：**

```markdown
# Gen-Z Skincare Market Analysis Framework

## Research Overview
- **Research Subject**: Gen-Z Skincare Market Deep Analysis
- **Scope**: China market, 2020-2025, consumers aged 18-27
- **Analysis Domain**: Market Analysis + Consumer Insights
- **Core Research Questions**:
  1. What is the size and growth momentum of the Gen-Z skincare market?
  2. What is unique about Gen-Z consumer skincare behavior patterns?
  3. How can brands effectively reach and convert Gen-Z consumers?

## Chapter Skeleton

### 1. Market Size & Growth Trends
- **Analysis Objective**: Quantify Gen-Z skincare market size and identify growth drivers
- **Analysis Logic**: Total market → Segmentation → Growth rate → Driver decomposition
- **Core Hypothesis**: Gen-Z is becoming the core engine of skincare consumption growth

#### Data Requirements
| # | Data Metric | Data Type | Suggested Sources | Search Keywords | Priority | Time Range |
|---|-------------|-----------|-------------------|-----------------|----------|------------|
| 1 | China skincare market total size | Quantitative | Industry reports | "China skincare market size 2024 2025" | P0 | 2020-2025 |
| 2 | Gen-Z skincare spending share | Quantitative | Industry reports, e-commerce platforms | "Gen-Z skincare spending share youth" | P0 | Latest |

#### Visualization & Content Plan
**Chart 1**: Line chart — China Skincare Market Size Trend 2020-2025
**Argument Structure**:
1. What: Quantified status of market size and Gen-Z share
2. Why: Consumption upgrade, ingredient-conscious consumers, social media driven
3. So What: Brands should prioritize building youth-oriented product lines

### 2. Consumer Profiling & Behavioral Insights
...

## Data Collection Task List
[Consolidated P0/P1 tasks]
```

### Phase 2 示例：报告生成

在数据收集之后，用户提供：Analysis Framework + 带品牌指标的 Data Summary + 图表文件路径。

**Phase 2 输出（最终报告）遵循如下流程：**

1. 以 `# Gen-Z Skincare Market Deep Analysis Report` 开始
2. Abstract —— 用执行摘要形式写出 3-5 条关键结论
3. 1. Introduction —— 市场背景、研究范围、数据来源
4. 2. Market Size & Growth Trend Analysis —— 嵌入趋势图、对比表、战略叙事
5. 3. Consumer Profiling & Behavioral Insights —— 人口特征、购买驱动因素、“So What” 分析
6. 4. Brand Competitive Landscape Assessment —— 品牌定位、份额分析、竞争动态
7. 5. Marketing Strategy & Channel Insights —— 渠道效果、内容策略含义
8. 6. Conclusion —— 用流动式散文做客观综合（无 bullet）
9. 7. References —— GB/T 7714-2015 格式列表

---

## 质量检查清单

### Phase 1 质量检查清单（Analysis Framework）

- [ ] 框架覆盖了该领域的所有自然分析维度
- [ ] 每章都有清晰的 Analysis Objective、Analysis Logic 和 Core Hypothesis
- [ ] 数据需求具体、可衡量，并包含可执行的 Search Keywords
- [ ] 每章至少有一个可视化计划，并明确图表类型与数据映射
- [ ] 已分配数据优先级（P0/P1/P2）——P0 项是核心论点所必需的数据
- [ ] Data Collection Task List 完整、去重，并可直接用于下游执行
- [ ] 框架能适配正确领域（市场/金融/行业/消费者等）

### Phase 2 质量检查清单（最终报告）

- [ ] **NO HALLUCINATION**：所有数字和图表都已对照输入的 Data Summary 验证
- [ ] 在写报告前已生成所有计划图表（步骤 2.3 先完成）
- [ ] 所有章节按正确顺序出现（Abstract → Introduction → Body → Conclusion → References）
- [ ] 每个小节都遵循 “Visual Anchor → Data Contrast → Integrated Analysis”
- [ ] 每个小节都以至少 200 词的分析段落结尾
- [ ] 所有洞察都遵循 “Data → User Psychology → Strategy Implication” 链
- [ ] 所有标题都使用正确编号（无 “Chapter/Part/Section” 前缀）
- [ ] 图表使用 `![Description](path)` 语法嵌入
- [ ] 数字使用英文逗号作为千位分隔符
- [ ] 在适用处使用 Markdown 链接作为行内引用
- [ ] References section 符合 GB/T 7714-2015
- [ ] 文档中无水平分隔线（`---`）
- [ ] Conclusion 使用流动式散文——无 bullet points
- [ ] 报告直接以 `#` 标题开头——无前言
- [ ] 缺失的 P0 数据在报告中有明确标注

## 输出格式

- **Phase 1**：以 **Markdown** 格式输出完整 Analysis Framework
- **Phase 2**：以 **Markdown** 格式输出完整 Report

## 设置

```
output_locale = zh_CN  # configurable per user request
reasoning_locale = en
```

## 说明

- 此 skill 在多步骤 agentic workflow 中分**两个阶段**运行：
  - **Phase 1** 生成分析框架与数据收集需求
  - **Data collection** 由其他 skills 完成（deep-research、data-analysis 等）
  - **Phase 2** 接收已收集的数据并生成最终报告
- 动态标题：将 Framework 中的主题**重写**为专业、简洁、基于主题的标题
- Conclusion 部分**不得**包含详细建议——这些内容应放在前面的正文章节中
- **ZERO HALLUCINATION POLICY**：报告中的每一句陈述、每一张图和每一个数字，都必须由输入 Data Summary 中的数据点支撑。若缺失数据，就坦诚说明。
- **可追溯性**：如果被要求，你必须能指出 Data Summary 或 External Search Findings 中支撑某条主张的具体行
- 框架应根据具体领域调整分析维度与深度（财务分析所用框架不同于消费者洞察）
- 当研究主题存在歧义时，默认采用最合理的广义范围，并注明假设
