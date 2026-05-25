# 输出模式

当技能需要产生一致、高质量的输出时，使用这些模式。

## 模板模式

为输出格式提供模板。根据需要调整严格程度。

**对于严格要求（如 API 响应或数据格式）：**

```markdown
## 报告结构

始终使用此精确模板结构：

# [分析标题]

## 执行摘要
[关键发现的一段概述]

## 主要发现
- 带支持数据的发现 1
- 带支持数据的发现 2
- 带支持数据的发现 3

## 建议
1. 具体可操作的建议
2. 具体可操作的建议
```

**对于灵活指导（当适应性有用时）：**

```markdown
## 报告结构

这是一个合理的默认格式，但请运用你的最佳判断：

# [分析标题]

## 执行摘要
[概述]

## 主要发现
[根据发现内容调整章节]

## 建议
[针对具体情境定制]

根据具体分析类型调整章节。
```

## 示例模式

对于输出质量依赖于查看示例的技能，提供输入/输出对：

```markdown
## 提交信息格式

按照以下示例生成提交信息：

**示例 1：**
输入：Added user authentication with JWT tokens
输出：
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**示例 2：**
输入：Fixed bug where dates displayed incorrectly in reports
输出：
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

遵循此风格：类型(范围): 简短描述，然后是详细说明。
```

示例比单纯的描述更能帮助 Claude 理解所需的风格和详细程度。
