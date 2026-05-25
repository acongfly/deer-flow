---
name: academic-paper-review
description: 当用户请求审阅、分析、批判性评价或总结学术论文、研究文章、预印本或科学出版物时使用此 skill。支持全面且结构化的审阅，涵盖方法论评估、贡献评价、文献定位以及建设性反馈生成。当查询涉及论文 URL、上传的 PDF、arXiv 链接，或类似“review this paper”“analyze this research”“summarize this study”“write a peer review”的请求时触发。
---

# 学术论文审阅 Skill

## 概述

此 skill 用于生成结构化、达到同行评审质量的学术论文与研究出版物分析。它遵循顶级学术场所（NeurIPS、ICML、ACL、Nature、IEEE）所采用的既有学术审稿标准，提供严谨、建设性且平衡的评估。

审阅内容涵盖**总结、优点、缺点、方法论评估、贡献评价、文献定位以及可执行建议**——全部基于论文自身提供的证据。

## 核心能力

- 解析并理解来自上传 PDF 或抓取 URL 的学术论文
- 按照顶级会议/期刊审稿模板生成结构化评审
- 评估方法论严谨性（实验设计、统计有效性、可复现性）
- 评价贡献的新颖性与重要性
- 通过有针对性的文献搜索，将工作置于更广泛的研究图景中
- 识别局限、缺口以及潜在改进方向
- 同时生成详细评审版和简明执行摘要版
- 支持任意科学领域的论文（CS、生物、物理、社会科学等）

## 何时使用此 Skill

**在以下情况下始终加载此 skill：**

- 用户提供论文 URL（arXiv、DOI、会议论文集、期刊链接）
- 用户上传研究论文或预印本的 PDF
- 用户要求“review”“analyze”“critique”“assess”或“summarize”某篇研究论文
- 用户想了解某项研究的优点和缺点
- 用户请求对学术工作进行同行评审风格的评价
- 用户请求帮助为会议或期刊投稿准备审稿意见

## 审阅方法论

### 阶段 1：论文理解

在形成任何判断之前，先彻底阅读并理解论文。

#### 步骤 1.1：识别论文元数据

提取并记录：

| 字段 | 说明 |
|-------|-------------|
| **Title** | 论文完整标题 |
| **Authors** | 作者列表及所属机构 |
| **Venue / Status** | 发表场所、预印本服务器或投稿状态 |
| **Year** | 发表或投稿年份 |
| **Domain** | 研究领域与子领域 |
| **Paper Type** | 实证、理论、综述、立场论文、系统论文等 |

#### 步骤 1.2：深入通读

系统性阅读论文：

1. **Abstract & Introduction** — 识别论文声称的贡献与研究动机
2. **Related Work** — 记录作者如何将其工作相对于已有研究进行定位
3. **Methodology** — 详细理解提出的方法、模型或框架
4. **Experiments / Results** — 审查数据集、基线、指标与报告结果
5. **Discussion & Limitations** — 记录作者自我指出的局限
6. **Conclusion** — 将结论中的主张与文中实际呈现的证据进行对照

#### 步骤 1.3：提取关键主张

明确列出论文的主要主张：

```
Claim 1: [Specific claim about contribution or finding]
Evidence: [What evidence supports this claim in the paper]
Strength: [Strong / Moderate / Weak]

Claim 2: [...]
...
```

### 阶段 2：批判性分析

#### 步骤 2.1：文献背景搜索

使用 web search 了解研究图景：

```
Search queries:
- "[paper topic] state of the art [current year]"
- "[key method name] comparison benchmark"
- "[authors] previous work [topic]"
- "[specific technique] limitations criticism"
- "survey [research area] recent advances"
```

对关键相关论文或综述使用 `web_fetch`，以理解该工作所处的位置。

#### 步骤 2.2：方法论评估

使用以下框架评估方法论：

| 标准 | 需要提出的问题 | 评分 |
|-----------|-----------------|--------|
| **Soundness** | 方法在技术上是否正确？是否存在逻辑缺陷？ | 1-5 |
| **Novelty** | 真正的新意是什么？哪些只是增量改进？ | 1-5 |
| **Reproducibility** | 细节是否足以复现？代码/数据是否可得？ | 1-5 |
| **Experimental Design** | 基线是否公平？消融是否充分？数据集是否合适？ | 1-5 |
| **Statistical Rigor** | 结果是否具有统计显著性？是否报告误差条？是否进行了多次运行？ | 1-5 |
| **Scalability** | 方法是否可扩展？是否讨论了计算成本？ | 1-5 |

#### 步骤 2.3：贡献重要性评估

评估贡献的重要性等级：

| 等级 | 说明 | 标准 |
|-------|-------------|----------|
| **Landmark** | 从根本上改变该领域 | 新范式、具有广泛适用性的突破 |
| **Significant** | 有力推动了当前最优水平 | 有明确改进且证据扎实 |
| **Moderate** | 有价值但存在一定局限的贡献 | 增量但有效的改进 |
| **Marginal** | 相较现有工作推进有限 | 收益较小，适用范围狭窄 |
| **Below threshold** | 未达到发表标准 | 存在根本性缺陷，证据不足 |

#### 步骤 2.4：优缺点分析

对于每个优点或缺点，都要提供：
- **What**：具体观察
- **Where**：对应章节/图/表引用
- **Why it matters**：它对论文主张或实际价值的影响

### 阶段 3：综合形成评审

#### 步骤 3.1：组装结构化评审

使用下方模板生成最终评审。

## 评审输出模板

```markdown
# Paper Review: [Paper Title]

## Paper Metadata
- **Authors**: [Author list]
- **Venue**: [Publication venue or preprint server]
- **Year**: [Year]
- **Domain**: [Research field]
- **Paper Type**: [Empirical / Theoretical / Survey / Systems / Position]

## Executive Summary

[2-3 paragraph summary of the paper's core contribution, approach, and main findings.
State your overall assessment upfront: what the paper does well, where it falls short,
and whether the contribution is sufficient for the claimed venue/impact level.]

## Summary of Contributions

1. [First claimed contribution — one sentence]
2. [Second claimed contribution — one sentence]
3. [Additional contributions if any]

## Strengths

### S1: [Concise strength title]
[Detailed explanation with specific references to sections, figures, or tables in the paper.
Explain WHY this is a strength and its significance.]

### S2: [Concise strength title]
[...]

### S3: [Concise strength title]
[...]

## Weaknesses

### W1: [Concise weakness title]
[Detailed explanation with specific references. Explain the impact of this weakness on
the paper's claims. Suggest how it could be addressed.]

### W2: [Concise weakness title]
[...]

### W3: [Concise weakness title]
[...]

## Methodology Assessment

| Criterion | Rating (1-5) | Assessment |
|-----------|:---:|------------|
| Soundness | X | [Brief justification] |
| Novelty | X | [Brief justification] |
| Reproducibility | X | [Brief justification] |
| Experimental Design | X | [Brief justification] |
| Statistical Rigor | X | [Brief justification] |
| Scalability | X | [Brief justification] |

## Questions for the Authors

1. [Specific question that would clarify a concern or ambiguity]
2. [Question about methodology choices or alternative approaches]
3. [Question about generalizability or practical applicability]

## Minor Issues

- [Typos, formatting issues, unclear figures, notation inconsistencies]
- [Missing references that should be cited]
- [Suggestions for improved clarity]

## Literature Positioning

[How does this work relate to the current state of the art?
Are key related works cited? Are comparisons fair and comprehensive?
What important related work is missing?]

## Recommendations

**Overall Assessment**: [Accept / Weak Accept / Borderline / Weak Reject / Reject]

**Confidence**: [High / Medium / Low] — [Justification for confidence level]

**Contribution Level**: [Landmark / Significant / Moderate / Marginal / Below threshold]

### Actionable Suggestions for Improvement
1. [Specific, constructive suggestion]
2. [Specific, constructive suggestion]
3. [Specific, constructive suggestion]
```

## 评审原则

### 建设性批评
- **始终给出如何修复的建议** —— 不要只指出问题，还要提出解决方案
- **该给的认可一定要给** —— 即使论文存在缺陷，也要承认其真实贡献
- **保持具体** —— 引用准确的章节、公式、图和表
- **区分轻重** —— 将致命缺陷与可修复问题区分开来

### 客观性标准
- ❌ “This paper is poorly written” （模糊且无帮助）
- ✅ “Section 3.2 introduces notation X without formal definition, making the proof in Theorem 1 difficult to follow. Consider adding a notation table after the problem formulation.”（具体且可执行）

### 伦理审稿实践
- 不要因作者声誉或机构而否定工作
- 依据工作本身的价值进行评估
- 以建设性的方式指出潜在伦理问题（如数据集偏差、双重用途风险）
- 对未发表工作保持保密

## 按论文类型调整

| 论文类型 | 关注重点 |
|------------|-------------|
| **Empirical** | 实验设计、基线、统计显著性、消融实验、可复现性 |
| **Theoretical** | 证明正确性、假设合理性、界的紧致性、与实践的联系 |
| **Survey** | 全面性、分类体系质量、近期工作覆盖度、综合洞见 |
| **Systems** | 架构决策、可扩展性证据、真实部署、工程贡献 |
| **Position** | 论证连贯性、主张证据、潜在影响、论述是否公平 |

## 需要避免的常见陷阱

- ❌ 审阅你希望作者写的论文，而不是其实际提交的论文
- ❌ 要求范围明显不合理的额外实验
- ❌ 因论文没有解决另一个问题而惩罚它
- ❌ 过度受写作质量影响，而忽视技术贡献
- ❌ 因未比较你自己的工作而将其视为缺点
- ❌ 只给出总结而没有批判性分析

## 质量检查清单

在完成评审前，确认：

- [ ] 已完整阅读论文（而非只看摘要和引言）
- [ ] 所有主要主张都已识别，并与证据逐一对照评估
- [ ] 至少提供 3 个优点和 3 个缺点，并附有具体引用
- [ ] 方法论评估表已填写完整，包含评分与理由
- [ ] 给作者的问题针对真实歧义，而非修辞式批评
- [ ] 已进行文献搜索，以便为贡献提供背景定位
- [ ] 建议具有可执行性且富有建设性
- [ ] 总体评价与识别出的优缺点保持一致
- [ ] 评审语气专业且尊重
- [ ] 轻微问题与主要问题已区分开

## 输出格式

- 使用 **Markdown** 格式输出完整评审
- 在 sandbox 中工作时，将评审保存到 `/mnt/user-data/outputs/review-{paper-topic}.md`
- 使用 `present_files` tool 向用户展示评审结果

## 说明

- 此 skill 可与 `deep-research` skill 配合使用——当用户希望在更广阔领域背景下审阅论文时，加载两者
- 对于付费墙后的论文，应基于可访问内容开展工作（摘要、公开版本、预印本镜像等）
- 根据用户需求调整评审深度：快速分诊时给出简评，为投稿准备时给出完整评审
- 比较性地审阅多篇论文时，需在所有评审中保持一致标准
- 始终披露你评审的局限（例如：“I could not verify the proofs in Appendix B in detail”）
