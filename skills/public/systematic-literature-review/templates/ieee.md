# IEEE 引用模板

当用户面向 IEEE 会议或期刊，或明确要求 IEEE 格式时使用此模板。IEEE 使用**数字引用**——参考文献按首次出现顺序编号，正文引用使用括号数字。

## 引用格式规则

### 正文内引用

- **单个引用**：`[1]` — 使用参考文献部分分配的编号。
- **多个引用**：`[1], [3], [5]` 或连续范围 `[1]–[3]`。
- **引用作为名词**：`如 [1] 所示，...` 或 `参考文献 [1] 证明了...`。
- **作者归因**：`Vaswani et al. [1] 引入了...`。

数字按**正文中首次出现的顺序**分配，不按字母顺序。第一个引用的参考文献是 `[1]`，第二个新参考文献是 `[2]`，依此类推。

### arXiv 预印本的参考文献条目

```
[N] A. A. Author, B. B. Author, and C. C. Author, "Title of the paper," arXiv:ARXIV_ID, Year.
```

**实际示例**：

```
[1] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, Ł. Kaiser, and I. Polosukhin, "Attention is all you need," arXiv:1706.03762, 2017.
```

格式规则：

- **作者姓名**：`FirstInitial. LastName` — 首字母在姓氏前，与 APA 相反。用逗号连接；最后一位作者前加 `and`。
- **标题**：用双引号括起，句首大写。不斜体。
- **来源**：`arXiv:<id>` — 字面前缀 `arXiv:` 后跟裸 id（例如 `arXiv:1706.03762`，不是完整 URL）。
- **年份**：最后，逗号后。

### 特殊情况

- **超过 6 位作者**：IEEE 允许列出第一作者后跟 `et al.`。

## 报告结构

```markdown
# 系统性文献综述：<主题>

**日期**：<YYYY-MM-DD>
**调查论文数**：<N>
**引用格式**：IEEE

## 执行摘要

<3-5 句话总结文献现状。首次引入每篇论文时使用括号数字，例如"Transformer 架构 [1] 已成为主导方法，后续工作聚焦于效率 [2], [3] 和长上下文处理 [4]。">

## 主题

<3-6 个主题章节。每篇论文首次出现时获得一个括号数字；后续提及重用相同数字。>

### [1] Vaswani et al., "Attention is all you need" (2017)

**研究问题**：<1 句话>
**方法论**：<1-2 句话>
**主要发现**：
- <要点>
**局限性**：<1-2 句话>

## 参考文献

<按首次出现顺序编号的列表。>

[1] A. Vaswani, N. Shazeer, ..., "Attention is all you need," arXiv:1706.03762, 2017.

[2] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, "BERT: Pre-training of deep bidirectional transformers for language understanding," arXiv:1810.04805, 2018.
```

## 定稿前的质量检查

- [ ] 每篇论文都有唯一的参考编号。
- [ ] 参考编号按**正文中首次出现的顺序**分配，不按字母顺序。
- [ ] 正文中的每个括号数字在参考文献部分都有匹配的条目。
- [ ] 作者姓名使用 `FirstInitial. LastName` 格式（首字母在姓氏前）。
- [ ] arXiv 标识符使用 `arXiv:<bare_id>` 形式，不是完整 URL。
