# 08 — 核心模块：Skills 技能系统

> 原始资料：[`backend/CLAUDE.md`](../../backend/CLAUDE.md)  
> 源码位置：`backend/packages/harness/deerflow/skills/`  
> 技能目录：`skills/public/` · `skills/custom/`

---

## 1. 什么是 Skills

Skills（技能）是 DeerFlow 的可扩展知识单元。每个技能以目录形式存在，包含一个 `SKILL.md` 文件描述能力和使用要求。已启用的技能会被注入到 Agent 的系统提示词中，让 Agent 知道如何调用特定工具或执行特定任务。

**Skills vs Tools**：
- **Tool**：Agent 可以调用的函数（有输入/输出）
- **Skill**：告诉 Agent *如何做某件事* 的指令文档，可以指定需要哪些工具

---

## 2. 总体结构

```
skills/
├── public/           # 内置技能（已提交到 git）
│   ├── web-search/
│   │   └── SKILL.md
│   ├── code-analysis/
│   │   └── SKILL.md
│   └── ...
└── custom/           # 自定义技能（git-ignored）
    └── my-skill/
        └── SKILL.md
```

```
deerflow/skills/          # 技能加载逻辑
├── __init__.py
├── loader.py             # load_skills()
├── parser.py             # 解析 SKILL.md frontmatter
└── models.py             # SkillMetadata 数据模型
```

---

## 3. SKILL.md 格式

每个技能目录必须包含一个 `SKILL.md` 文件，格式为带 YAML frontmatter 的 Markdown：

```markdown
---
name: web-search          # 技能唯一标识符
description: 网络搜索能力  # 技能描述（注入到系统提示词）
version: 1.0.0            # 版本（可选）
author: DeerFlow Team     # 作者（可选）
license: MIT              # 许可证（可选）
compatibility: ">=2.0"    # 兼容的 DeerFlow 版本（可选）
allowed-tools:            # 允许使用的工具列表（可选，限制工具访问）
  - tavily_search
  - web_fetch
---

## 技能说明

这个技能让你可以搜索网页内容。使用时需要：

1. 使用 `tavily_search` 工具进行网页搜索
2. 使用 `web_fetch` 工具获取具体页面内容
3. 综合多个来源的信息给出答案

## 使用示例

当用户询问最新新闻时，先搜索关键词，再获取具体文章内容。
```

---

## 4. 技能加载流程

**文件**：`backend/packages/harness/deerflow/skills/loader.py`

```
load_skills()
    │
    ├── 递归扫描 skills/public/ 和 skills/custom/ 目录
    │
    ├── 对每个 SKILL.md：
    │   ├── 解析 YAML frontmatter（name, description, allowed-tools 等）
    │   └── 从 extensions_config.json 读取 enabled 状态
    │
    └── 返回 SkillMetadata 列表（包含 enabled 状态）
```

---

## 5. 技能注入

已启用的技能在 `apply_prompt_template()` 中注入到系统提示词：

```
System Prompt:
  ...基础指令...
  
  ## Available Skills
  
  ### web-search（位于 /mnt/skills/public/web-search/）
  网络搜索能力...（SKILL.md 内容）
  
  ### code-analysis（位于 /mnt/skills/public/code-analysis/）
  代码分析能力...
  
  ...记忆信息...
```

Agent 可以通过读取 `/mnt/skills/` 路径下的文件来了解技能的详细说明。

---

## 6. 技能启用/禁用（通过 API）

```bash
# 列出所有技能及其状态
GET /api/skills/

# 获取特定技能详情
GET /api/skills/{name}

# 启用/禁用技能
PUT /api/skills/{name}
Content-Type: application/json
{"enabled": true}
```

技能的启用状态保存在 `extensions_config.json` 的 `skills` 字段中。

---

## 7. 安装 .skill 包

```bash
# 通过 API 安装技能包（.skill 文件是 ZIP 格式）
POST /api/skills/install
Content-Type: multipart/form-data
file=@my-skill.skill
```

安装逻辑：
1. 解压 `.skill` ZIP 档案到 `skills/custom/` 目录
2. 验证 `SKILL.md` 存在且格式正确
3. 从 frontmatter 读取标准字段（`version`、`author`、`compatibility`）
4. 技能立即可用（无需重启）

---

## 8. 开发步骤：创建自定义技能

### 步骤 1：创建技能目录

```bash
mkdir -p skills/custom/my-skill
```

### 步骤 2：编写 SKILL.md

```markdown
---
name: my-skill
description: 我的自定义技能，用于执行特定任务
version: 1.0.0
author: 我的名字
allowed-tools:
  - bash
  - read_file
  - write_file
---

## 使用场景

当用户需要执行 XXX 任务时，使用此技能。

## 操作步骤

1. 首先用 read_file 读取目标文件
2. 分析内容...
3. 用 write_file 写入结果

## 注意事项

- 只处理 `.txt` 和 `.md` 文件
- 不要修改系统文件
```

### 步骤 3：通过 API 启用

```bash
curl -X PUT http://localhost:8001/api/skills/my-skill \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### 步骤 4：打包为 .skill 文件（用于分发）

```bash
cd skills/custom
zip -r my-skill.skill my-skill/
```

---

## 9. 技能与 MCP 的关系

- **MCP** 扩展 Agent 的工具能力（Agent 能调用哪些函数）
- **Skills** 扩展 Agent 的知识能力（Agent 知道如何做某件事）
- 两者可以结合：一个 Skill 可以指导 Agent 如何使用某个 MCP 工具

示例：
```markdown
---
name: database-query
description: 使用 PostgreSQL MCP 工具查询数据库
allowed-tools:
  - mcp_postgresql_query
---

使用 mcp_postgresql_query 工具时，始终：
1. 先验证 SQL 语句安全性
2. 限制结果集大小（添加 LIMIT 子句）
3. 将结果格式化为 Markdown 表格
```
