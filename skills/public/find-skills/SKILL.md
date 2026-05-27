---
name: find-skills
description: 当用户提出“how do I do X”“find a skill for X”“is there a skill that can...”之类的问题，或表达出想扩展能力的意图时，帮助用户发现并安装 agent skills。当用户在寻找某种可能以可安装 skill 形式存在的功能时，应使用此 skill。
---

# 查找 Skills

此 skill 可帮助你从开放的 agent skills 生态中发现并安装 skills。

## 何时使用此 Skill

当用户满足以下情况时使用此 skill：

- 询问“how do I do X”，而 X 可能是已有 skill 支持的常见任务
- 说“find a skill for X”或“is there a skill for X”
- 询问“can you do X”，而 X 是专门能力
- 表达出扩展 agent 能力的兴趣
- 想搜索 tools、templates 或 workflows
- 提到自己希望在某个特定领域（设计、测试、部署等）获得帮助

## 什么是 Skills CLI？

Skills CLI（`npx skills`）是开放 agent skills 生态的包管理器。Skills 是模块化包，可通过专门知识、工作流和 tools 扩展 agent 能力。

**关键命令：**

- `npx skills find [query]` - 交互式或按关键词搜索 skills
- `npx skills check` - 检查 skill 更新
- `npx skills update` - 更新所有已安装 skills

**浏览 skills：** https://skills.sh/

## 如何帮助用户查找 Skills

### 步骤 1：理解他们需要什么

当用户请求帮助时，识别：

1. 所属领域（例如 React、testing、design、deployment）
2. 具体任务（例如写测试、创建动画、审查 PR）
3. 这是否足够常见，以至于大概率已有 skill 存在

### 步骤 2：搜索 Skills

使用相关查询运行查找命令：

```bash
npx skills find [query]
```

例如：

- 用户问 “how do I make my React app faster?” → `npx skills find react performance`
- 用户问 “can you help me with PR reviews?” → `npx skills find pr review`
- 用户说 “I need to create a changelog” → `npx skills find changelog`

该命令会返回类似结果：

```
Install with bash /path/to/skill/scripts/install-skill.sh vercel-labs/agent-skills@vercel-react-best-practices

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 步骤 3：向用户展示选项

找到相关 skills 后，应向用户展示：

1. skill 名称及其作用
2. 他们可运行的安装命令
3. 在 skills.sh 上了解详情的链接

示例回复：

```
I found a skill that might help! The "vercel-react-best-practices" skill provides
React and Next.js performance optimization guidelines from Vercel Engineering.

To install it:
bash /path/to/skill/scripts/install-skill.sh vercel-labs/agent-skills@vercel-react-best-practices

Learn more: https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 步骤 4：安装 Skill

如果用户希望继续，使用 `install-skill.sh` 脚本安装该 skill，并自动将其链接到项目：

```bash
bash /path/to/skill/scripts/install-skill.sh <owner/repo@skill-name>
```

例如，如果用户要安装 `vercel-react-best-practices`：

```bash
bash /path/to/skill/scripts/install-skill.sh vercel-labs/agent-skills@vercel-react-best-practices
```

该脚本会将 skill 全局安装到 `skills/custom/`

## 常见 Skill 类别

搜索时，可考虑以下常见类别：

| 类别 | 示例查询 |
| --------------- | ---------------------------------------- |
| Web Development | react, nextjs, typescript, css, tailwind |
| Testing | testing, jest, playwright, e2e |
| DevOps | deploy, docker, kubernetes, ci-cd |
| Documentation | docs, readme, changelog, api-docs |
| Code Quality | review, lint, refactor, best-practices |
| Design | ui, ux, design-system, accessibility |
| Productivity | workflow, automation, git |

## 高效搜索提示

1. **使用具体关键词**：`react testing` 比单独的 `testing` 更好
2. **尝试替代表达**：如果 `deploy` 没结果，试试 `deployment` 或 `ci-cd`
3. **检查热门来源**：很多 skills 来自 `vercel-labs/agent-skills` 或 `ComposioHQ/awesome-claude-skills`

## 当没有找到 Skills 时

如果没有相关 skill：

1. 明确说明未找到现成 skill
2. 提出你仍可使用通用能力直接帮助完成任务
3. 建议用户可以用 `npx skills init` 创建自己的 skill

示例：

```
I searched for skills related to "xyz" but didn't find any matches.
I can still help you with this task directly! Would you like me to proceed?

If this is something you do often, you could create your own skill:
npx skills init my-xyz-skill
```
