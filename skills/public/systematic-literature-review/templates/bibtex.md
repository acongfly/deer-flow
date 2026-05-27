# BibTeX 引用模板

当用户提到 BibTeX、LaTeX，或希望获得机器可读的参考文献时使用此模板。

## 关键：arXiv 论文使用 `@misc`，而不是 `@article`

**arXiv 预印本必须引用为 `@misc`，而不是 `@article`。**

- `@article` 需要 `journal` 字段。arXiv 不是期刊——它是一个预印本服务器。
- `@misc` 是预印本、技术报告和其他非期刊出版物的正确条目类型。
- 只有当论文**正式发表**在经同行评审的场所且你有场所元数据时，才切换到 `@article`。

## 引用格式规则

### arXiv 预印本的条目结构

```bibtex
@misc{citekey,
  author        = {LastName1, FirstName1 and LastName2, FirstName2 and ...},
  title         = {Title of the Paper},
  year          = {YYYY},
  eprint        = {ARXIV_ID},
  archivePrefix = {arXiv},
  primaryClass  = {PRIMARY_CATEGORY},
  url           = {https://arxiv.org/abs/ARXIV_ID}
}
```

**实际示例**：

```bibtex
@misc{vaswani2017attention,
  author        = {Vaswani, Ashish and Shazeer, Noam and Parmar, Niki and Uszkoreit, Jakob and Jones, Llion and Gomez, Aidan N. and Kaiser, {\L}ukasz and Polosukhin, Illia},
  title         = {Attention Is All You Need},
  year          = {2017},
  eprint        = {1706.03762},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url           = {https://arxiv.org/abs/1706.03762}
}
```

### 字段规则

- **引用键**：`<第一作者姓><年份><标题第一词>`，全小写，无标点。示例：`vaswani2017attention`。
- **`author`**：`LastName, FirstName and LastName, FirstName and ...` — 作者之间使用字面词 `and`，而不是逗号。
- **特殊字符**：转义或包裹 LaTeX 敏感字符。例如，`Łukasz` 变为 `{\L}ukasz`。
- **`title`**：如果包含需要保持大写的缩略词或专有名词，用双花括号包裹：`title = {{BERT}: Pre-training ...}`。
- **`year`**：论文 `published` 字段的 4 位数年份。
- **`eprint`**：**裸 arXiv id**（例如 `1706.03762`），**不带** `arXiv:` 前缀和版本后缀。
- **`archivePrefix`**：字面字符串 `{arXiv}`。
- **`primaryClass`**：论文 `categories` 列表中的第一个类别（例如 `cs.CL`、`cs.CV`）。
- **`url`**：论文元数据中的完整 `abs_url`。

## 报告结构

BibTeX 报告与 APA/IEEE 略有不同：**参考书目是一个单独的 `.bib` 文件**，主报告使用 LaTeX 风格的 `\cite{key}` 引用。

```markdown
# 系统性文献综述：<主题>

**日期**：<YYYY-MM-DD>
**调查论文数**：<N>
**引用格式**：BibTeX

## 执行摘要

<3-5 句话。对引用使用 \cite{key} 形式。>

## BibTeX 参考书目

将以下条目保存到 `.bib` 文件，并在 LaTeX 文档中用 `\bibliography{filename}` 引用。

\`\`\`bibtex
@misc{vaswani2017attention,
  author        = {Vaswani, Ashish and Shazeer, Noam and ...},
  title         = {Attention Is All You Need},
  year          = {2017},
  eprint        = {1706.03762},
  archivePrefix = {arXiv},
  primaryClass  = {cs.CL},
  url           = {https://arxiv.org/abs/1706.03762}
}
\`\`\`
```

## 定稿前的质量检查

- [ ] 每个条目都是 `@misc`，不是 `@article`。
- [ ] 引用键在报告中唯一。
- [ ] `author` 字段在作者之间使用 ` and `（字面词），不是逗号。
- [ ] `eprint` 是裸 arXiv id（无 `arXiv:` 前缀，无版本后缀）。
- [ ] 参考书目在 `` ```bibtex `` 代码块中输出。
