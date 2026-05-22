# 🦌 DeerFlow - 2.0

[英语](./README.md) | [中文](./README_zh.md) | [日语](./README_ja.md) | 法语 | [俄语](./README_ru.md)

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](./backend/pyproject.toml)
[![Node.js](https://img.shields.io/badge/Node.js-22%2B-339933?logo=node.js&logoColor=white)](./Makefile)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

<a href="https://trendshift.io/repositories/14699" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14699" alt="bytedance%2Fdeer-flow | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
> 2026 年 2 月 28 日，DeerFlow 2 发布后登上 GitHub Trending 🏆 第 1 名。非常感谢我们了不起的社区——这一切都离不开你们！💪🔥

DeerFlow（**D**eep **E**xploration and **E**fficient **R**esearch **Flow**）是一个开源的 **super agent harness**，可编排 **sub-agents**、**memory** 和 **sandboxes** 来完成几乎任何任务——并由可扩展的 **skills** 提供支持。

https://github.com/user-attachments/assets/a8bcadc4-e040-4cf2-8fda-dd768b999c18

> [!NOTE]
> **DeerFlow 2.0 是一次彻底重写。** 它与 v1 没有共享任何代码。如果你在寻找最初的 Deep Research 框架，它仍维护在 [`1.x` 分支](https://github.com/bytedance/deer-flow/tree/main-1.x) 上——仍然欢迎贡献。当前的活跃开发已迁移到 2.0。

## 官网

[<img width="2880" height="1600" alt="image" src="https://github.com/user-attachments/assets/a598c49f-3b2f-41ea-a052-05e21349188a" />](https://deerflow.tech)

想了解更多并观看**真实演示**，请访问我们的[**官网**](https://deerflow.tech)。

## 字节跳动火山引擎 Coding Plan

<img width="4808" height="2400" alt="英文方舟" src="https://github.com/user-attachments/assets/2ecc7b9d-50be-4185-b1f7-5542d222fb2d" />

- 我们强烈推荐使用 Doubao-Seed-2.0-Code、DeepSeek v3.2 和 Kimi 2.5 来运行 DeerFlow
- [了解更多](https://www.byteplus.com/en/activity/codingplan?utm_campaign=deer_flow&utm_content=deer_flow&utm_medium=devrel&utm_source=OWO&utm_term=deer_flow)
- [中国大陆开发者请点击这里](https://www.volcengine.com/activity/codingplan?utm_campaign=deer_flow&utm_content=deer_flow&utm_medium=devrel&utm_source=OWO&utm_term=deer_flow)

## InfoQuest

DeerFlow 现已集成由 BytePlus 开发的智能搜索与爬取工具包——[InfoQuest（在线免费试用）](https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest)

<a href="https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest" target="_blank">
  <img
    src="https://sf16-sg.tiktokcdn.com/obj/eden-sg/hubseh7bsbps/20251208-160108.png"   alt="InfoQuest_banner"
  />
</a>

---

## 目录

- [🦌 DeerFlow - 2.0](#-deerflow---20)
  - [官网](#官网)
  - [InfoQuest](#infoquest)
  - [目录](#目录)
  - [给 coding agent 的一句话安装提示](#给-coding-agent-的一句话安装提示)
  - [快速开始](#快速开始)
    - [配置](#配置)
    - [运行应用](#运行应用)
      - [选项 1：Docker（推荐）](#选项-1docker推荐)
      - [选项 2：本地开发](#选项-2本地开发)
    - [高级](#高级)
      - [Sandbox 模式](#sandbox-模式)
      - [MCP 服务器](#mcp-服务器)
      - [消息渠道](#消息渠道)
      - [LangSmith 追踪](#langsmith-追踪)
  - [从 Deep Research 到 Super Agent Harness](#从-deep-research-到-super-agent-harness)
  - [核心功能](#核心功能)
    - [Skills 与工具](#skills-与工具)
      - [Claude Code 集成](#claude-code-集成)
    - [Sub-Agents](#sub-agents)
    - [Sandbox 与文件系统](#sandbox-与文件系统)
    - [Context Engineering](#context-engineering)
    - [长期记忆](#长期记忆)
  - [推荐模型](#推荐模型)
  - [内置 Python 客户端](#内置-python-客户端)
  - [文档](#文档)
  - [⚠️ 安全警告](#️-安全警告)
  - [贡献](#贡献)
  - [许可证](#许可证)
  - [致谢](#致谢)
    - [核心贡献者](#核心贡献者)
  - [Star 历史](#star-历史)

## 给 coding agent 的一句话安装提示

如果你在使用 Claude Code、Codex、Cursor、Windsurf 或其他 coding agent，你可以直接把这句话发给它：

```text
Aide-moi à cloner DeerFlow si nécessaire, puis à initialiser son environnement de développement local en suivant https://raw.githubusercontent.com/bytedance/deer-flow/main/Install.md
```

这条提示词是给 coding agent 用的。它会在需要时克隆仓库、在可用时优先使用 Docker，然后停在启动 DeerFlow 的精确命令以及仍缺失的配置项清单上。

## 快速开始

### 配置

1. **克隆 DeerFlow 仓库**

   ```bash
   git clone https://github.com/bytedance/deer-flow.git
   cd deer-flow
   ```

2. **生成本地配置文件**

   在项目根目录（`deer-flow/`）中，运行：

   ```bash
   make config
   ```

   此命令会根据提供的模板创建本地配置文件。

3. **配置你选择的模型**

   编辑 `config.yaml` 并至少定义一个模型：

   ```yaml
   models:
     - name: gpt-4                       # Internal identifier
       display_name: GPT-4               # Human-readable name
       use: langchain_openai:ChatOpenAI  # LangChain class path
       model: gpt-4                      # Model identifier for API
       api_key: $OPENAI_API_KEY          # API key (recommended: use env var)
       max_tokens: 4096                  # Maximum tokens per request
       temperature: 0.7                  # Sampling temperature

     - name: openrouter-gemini-2.5-flash
       display_name: Gemini 2.5 Flash (OpenRouter)
       use: langchain_openai:ChatOpenAI
       model: google/gemini-2.5-flash-preview
       api_key: $OPENAI_API_KEY          # OpenRouter still uses the OpenAI-compatible field name here
       base_url: https://openrouter.ai/api/v1

     - name: gpt-5-responses
       display_name: GPT-5 (Responses API)
       use: langchain_openai:ChatOpenAI
       model: gpt-5
       api_key: $OPENAI_API_KEY
       use_responses_api: true
       output_version: responses/v1
   ```

   OpenRouter 和类似的 OpenAI 兼容网关应使用 `langchain_openai:ChatOpenAI` 与 `base_url` 进行配置。如果你更希望使用供应商专属的环境变量名，请将 `api_key` 显式指向该变量（例如 `api_key: $OPENROUTER_API_KEY`）。

   如需通过 `/v1/responses` 路由 OpenAI 模型，请继续使用 `langchain_openai:ChatOpenAI`，并设置 `use_responses_api: true` 与 `output_version: responses/v1`。

   基于 CLI 的 provider 示例：

   ```yaml
   models:
     - name: gpt-5.4
       display_name: GPT-5.4 (Codex CLI)
       use: deerflow.models.openai_codex_provider:CodexChatModel
       model: gpt-5.4
       supports_thinking: true
       supports_reasoning_effort: true

     - name: claude-sonnet-4.6
       display_name: Claude Sonnet 4.6 (Claude Code OAuth)
       use: deerflow.models.claude_provider:ClaudeChatModel
       model: claude-sonnet-4-6
       max_tokens: 4096
       supports_thinking: true
   ```

   - Codex CLI 会读取 `~/.codex/auth.json`
   - Codex 的 Responses 端点当前会拒绝 `max_tokens` 和 `max_output_tokens`，因此 `CodexChatModel` 不暴露每次请求的 token 上限
   - Claude Code 支持 `CLAUDE_CODE_OAUTH_TOKEN`、`ANTHROPIC_AUTH_TOKEN`、`CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR`、`CLAUDE_CODE_CREDENTIALS_PATH`，或明文的 `~/.claude/.credentials.json`
   - 在 macOS 上，DeerFlow 不会自动探测 Keychain。如有需要，请显式导出 Claude Code 认证信息：

   ```bash
   eval "$(python3 scripts/export_claude_code_oauth.py --print-export)"
   ```

4. **为已配置的模型设置 API key**

   请选择以下任一种方式：

- 选项 A：编辑项目根目录下的 `.env` 文件（推荐）


   ```bash
   TAVILY_API_KEY=your-tavily-api-key
   OPENAI_API_KEY=your-openai-api-key
   # OpenRouter also uses OPENAI_API_KEY when your config uses langchain_openai:ChatOpenAI + base_url.
   # Add other provider keys as needed
   INFOQUEST_API_KEY=your-infoquest-api-key
   ```

- 选项 B：在你的 shell 中导出环境变量

   ```bash
   export OPENAI_API_KEY=your-openai-api-key
   ```

   对于基于 CLI 的 provider：
   - Codex CLI：`~/.codex/auth.json`
   - Claude Code OAuth：通过 env/文件显式交接，或使用 `~/.claude/.credentials.json`

- 选项 C：直接编辑 `config.yaml`（不建议在生产环境中使用）

   ```yaml
   models:
     - name: gpt-4
       api_key: your-actual-api-key-here  # Replace placeholder
   ```

### 运行应用

#### 选项 1：Docker（推荐）

**开发环境**（热重载、挂载源码）：

```bash
make docker-init    # Pull sandbox image (only once or when image updates)
make docker-start   # Start services (auto-detects sandbox mode from config.yaml)
```

`make docker-start` 仅会在 `config.yaml` 使用 provisioner 模式（`sandbox.use: deerflow.community.aio_sandbox:AioSandboxProvider` 且带有 `provisioner_url`）时启动 `provisioner`。
后端进程会在下一次访问配置时自动获取 `config.yaml` 中的变更，因此开发模式下更新模型元数据无需手动重启。

> [!TIP]
> 在 Linux 上，如果 Docker 命令因 `permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock` 失败，请将你的用户加入 `docker` 组并重新登录后再试。完整解决方案请参阅 [CONTRIBUTING.md](CONTRIBUTING.md#linux-docker-daemon-permission-denied)。

**生产环境**（本地构建镜像，挂载配置和数据）：

```bash
make up     # Build images and start all production services
make down   # Stop and remove containers
```

> [!NOTE]
> Agent runtime 当前运行在 Gateway 中。nginx 会将 `/api/langgraph/*` 重写到由 Gateway 提供的 LangGraph 兼容 API。

访问地址：http://localhost:2026

完整的 Docker 开发指南请参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

#### 选项 2：本地开发

如果你更喜欢在本地运行服务：

前提条件：请先完成上方“配置”步骤（`make config` 和模型 API keys）。`make dev` 需要一个有效的配置文件（默认是项目根目录下的 `config.yaml`；可通过 `DEER_FLOW_CONFIG_PATH` 修改）。

1. **检查前置条件**：
   ```bash
   make check  # Verifies Node.js 22+, pnpm, uv, nginx
   ```

2. **安装依赖**：
   ```bash
   make install  # Install backend + frontend dependencies
   ```

3. **（可选）预拉取 sandbox 镜像**：
   ```bash
   # Recommended if using Docker/Container-based sandbox
   make setup-sandbox
   ```

4. **启动服务**：
   ```bash
   make dev
   ```

5. **访问地址**：http://localhost:2026

### 高级
#### Sandbox 模式

DeerFlow 支持多种 sandbox 执行模式：
- **本地执行**（直接在宿主机上运行 sandbox 代码）
- **Docker 执行**（在隔离的 Docker 容器中运行 sandbox 代码）
- **带 Kubernetes 的 Docker 执行**（通过 provisioner 服务在 Kubernetes pods 中运行 sandbox 代码）

在 Docker 开发环境中，服务启动会遵循 `config.yaml` 中定义的 sandbox 模式。在 Local/Docker 模式下，不会启动 `provisioner`。

如何配置你选择的模式，请参见 [Sandbox 配置指南](backend/docs/CONFIGURATION.md#sandbox)。

#### MCP 服务器

DeerFlow 支持可配置的 MCP 服务器和 skills，以扩展其能力。
对于 HTTP/SSE MCP 服务器，支持 OAuth token 流程（`client_credentials`、`refresh_token`）。
详细说明请参见 [MCP Server 指南](backend/docs/MCP_SERVER.md)。

#### 消息渠道

DeerFlow 可以从消息应用接收任务。渠道一旦配置完成就会自动启动——无需公网 IP。

| 渠道 | 传输方式 | 难度 |
|---------|-----------|------------|
| Telegram | Bot API（long-polling） | 简单 |
| Slack | Socket Mode | 中等 |
| Feishu / Lark | WebSocket | 中等 |
| DingTalk | Stream Push（WebSocket） | 中等 |

**在 `config.yaml` 中的配置：**

```yaml
channels:
  # LangGraph-compatible Gateway API base URL (default: http://localhost:8001/api)
  langgraph_url: http://localhost:8001/api
  # Gateway API URL (default: http://localhost:8001)
  gateway_url: http://localhost:8001

  # Optional: global session defaults for all mobile channels
  session:
    assistant_id: lead_agent
    config:
      recursion_limit: 100
    context:
      thinking_enabled: true
      is_plan_mode: false
      subagent_enabled: false

  feishu:
    enabled: true
    app_id: $FEISHU_APP_ID
    app_secret: $FEISHU_APP_SECRET
    # domain: https://open.feishu.cn       # China (default)
    # domain: https://open.larksuite.com   # International

  slack:
    enabled: true
    bot_token: $SLACK_BOT_TOKEN     # xoxb-...
    app_token: $SLACK_APP_TOKEN     # xapp-... (Socket Mode)
    allowed_users: []               # empty = allow all

  telegram:
    enabled: true
    bot_token: $TELEGRAM_BOT_TOKEN
    allowed_users: []               # empty = allow all

    # Optional: per-channel / per-user session settings
    session:
      assistant_id: mobile_agent
      context:
        thinking_enabled: false
      users:
        "123456789":
          assistant_id: vip_agent
          config:
            recursion_limit: 150
          context:
            thinking_enabled: true
            subagent_enabled: true

  dingtalk:
    enabled: true
    client_id: $DINGTALK_CLIENT_ID             # ClientId depuis DingTalk Open Platform
    client_secret: $DINGTALK_CLIENT_SECRET     # ClientSecret depuis DingTalk Open Platform
    allowed_users: []                          # vide = tout le monde autorisé
    card_template_id: ""                       # Optionnel : ID de modèle AI Card pour l'effet machine à écrire en streaming
```

请在你的 `.env` 文件中设置对应的 API keys：

```bash
# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# Feishu / Lark
FEISHU_APP_ID=cli_xxxx
FEISHU_APP_SECRET=your_app_secret

# DingTalk
DINGTALK_CLIENT_ID=your_client_id
DINGTALK_CLIENT_SECRET=your_client_secret
```

**Telegram 配置**

1. 打开与 [@BotFather](https://t.me/BotFather) 的聊天，发送 `/newbot`，并复制 HTTP API token。
2. 在 `.env` 中设置 `TELEGRAM_BOT_TOKEN`，并在 `config.yaml` 中启用该渠道。

**Slack 配置**

1. 在 [api.slack.com/apps](https://api.slack.com/apps) 上创建一个 Slack App → Create New App → From scratch。
2. 在 **OAuth & Permissions** 中，添加 Bot Token Scopes：`app_mentions:read`、`chat:write`、`im:history`、`im:read`、`im:write`、`files:write`。
3. 启用 **Socket Mode** → 生成一个带 `connections:write` scope 的 App-Level Token（`xapp-…`）。
4. 在 **Event Subscriptions** 中，订阅 bot events：`app_mention`、`message.im`。
5. 在 `.env` 中设置 `SLACK_BOT_TOKEN` 和 `SLACK_APP_TOKEN`，并在 `config.yaml` 中启用该渠道。

**Feishu / Lark 配置**

1. 在 [Feishu Open Platform](https://open.feishu.cn/) 上创建一个应用 → 启用 **Bot** 能力。
2. 添加权限：`im:message`、`im:message.p2p_msg:readonly`、`im:resource`。
3. 在 **Events** 中订阅 `im.message.receive_v1`，并选择 **Long Connection** 模式。
4. 复制 App ID 和 App Secret。在 `.env` 中设置 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`，并在 `config.yaml` 中启用该渠道。

**DingTalk 配置**

1. 在 [DingTalk Open Platform](https://open.dingtalk.com/) 上创建一个应用，并启用 **Robot** 能力。
2. 在机器人配置页面中，将消息接收模式设置为 **Stream**。
3. 复制 `Client ID` 和 `Client Secret`。在 `.env` 中设置 `DINGTALK_CLIENT_ID` 和 `DINGTALK_CLIENT_SECRET`，并在 `config.yaml` 中启用该渠道。
4. *（可选）* 如需启用 AI Card 流式回复（打字机效果），请在 [DingTalk 卡片平台](https://open.dingtalk.com/document/dingstart/typewriter-effect-streaming-ai-card) 中创建一个 **AI Card** 模板，然后在 `config.yaml` 中将 `card_template_id` 设置为该模板 ID。你还需要申请 `Card.Streaming.Write` 和 `Card.Instance.Write` 权限。

**命令**

一旦某个渠道连接成功，你就可以直接在聊天中与 DeerFlow 交互：

| 命令 | 描述 |
|---------|-------------|
| `/new` | 开始一段新对话 |
| `/status` | 显示当前 thread 信息 |
| `/models` | 列出可用模型 |
| `/memory` | 查看 memory |
| `/help` | 显示帮助 |

> 未带命令前缀的消息会按普通聊天处理——DeerFlow 会创建一个 thread，并以对话方式回复。

#### LangSmith 追踪

DeerFlow 原生集成了 [LangSmith](https://smith.langchain.com) 以实现可观测性。启用后，所有 LLM 调用、agent 执行和工具执行都会被追踪，并可在 LangSmith 仪表板中查看。

请将以下几行添加到你的 `.env` 文件中：

```bash
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxx
LANGSMITH_PROJECT=xxx
```

对于 Docker 部署，追踪默认是关闭的。请在 `.env` 中设置 `LANGSMITH_TRACING=true` 和 `LANGSMITH_API_KEY` 以启用它。

## 从 Deep Research 到 Super Agent Harness

DeerFlow 最初是一个 Deep Research 框架——随后社区把它推向了更远。从发布以来，开发者已经把它用于远超研究本身的场景：构建数据管道、生成演示文稿、搭建仪表盘、自动化内容工作流。这些用法是我们起初从未预料到的。

这让我们意识到了一件重要的事：DeerFlow 不只是一个研究工具。它是一个 **harness**——一个为 agent 提供真正完成工作的基础设施的运行时。

所以我们从零开始重建了它。

DeerFlow 2.0 不再是一个需要你自己拼装的框架。它是一个开箱即用且完全可扩展的 super agent harness。它构建在 LangGraph 和 LangChain 之上，内置了 agent 开箱即用所需的一切：文件系统、memory、skills、sandbox 执行，以及为复杂多步骤任务进行规划和启动 sub-agents 的能力。

直接使用它。或者拆开它，把它变成你自己的。

## 核心功能

### Skills 与工具

Skills 让 DeerFlow 能够*几乎做任何事*。

标准的 Agent Skill 是一种结构化的能力模块——一个定义工作流、最佳实践以及相关资源引用的 Markdown 文件。DeerFlow 内置了用于研究、报告生成、演示文稿制作、网页创建、图像和视频生成等多种 skills。但真正的力量在于其可扩展性：添加你自己的 skills，替换内置 skills，或将它们组合成复合工作流。

Skills 会按需逐步加载——只有在任务需要时才会加载，而不是一次全部载入。这样可以保持上下文窗口轻量，即使面对对 token 数量敏感的模型也能良好运行。

当你通过 Gateway 安装 `.skill` 压缩包时，DeerFlow 现在会接受标准的可选 frontmatter 元数据，例如 `version`、`author` 和 `compatibility`，而不会拒绝那些本来有效的外部 skills。

工具也遵循同样的理念。DeerFlow 自带一组核心工具——网页搜索、网页抓取、文件操作、bash 执行——并支持通过 MCP 服务器和 Python 函数接入自定义工具。任何东西都可以替换。任何东西都可以添加。

Gateway 生成的后续建议现在也会在将响应解析为 JSON 数组之前，同时规范化模型的纯文本输出和富文本块/列表内容，因此各 provider 特有的内容包装不再会静默丢弃这些建议。

```
# Paths inside the sandbox container
/mnt/skills/public
├── research/SKILL.md
├── report-generation/SKILL.md
├── slide-creation/SKILL.md
├── web-page/SKILL.md
└── image-generation/SKILL.md

/mnt/skills/custom
└── your-custom-skill/SKILL.md      ← yours
```

#### Claude Code 集成

`claude-to-deerflow` skill 允许你直接从 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 与一个正在运行的 DeerFlow 实例交互。你可以发送研究任务、检查状态、管理 threads——全部都无需离开终端。

**安装 skill：**

```bash
npx skills add https://github.com/bytedance/deer-flow --skill claude-to-deerflow
```

然后请确保 DeerFlow 已在运行（默认地址为 `http://localhost:2026`），并在 Claude Code 中使用 `/claude-to-deerflow` 命令。

**你可以做什么：**
- 向 DeerFlow 发送消息并接收流式响应
- 选择执行模式：flash（快速）、standard、pro（规划）、ultra（sub-agents）
- 检查 DeerFlow 健康状态，列出模型/skills/agents
- 管理 threads 和对话历史
- 上传文件进行分析

**环境变量**（可选，用于自定义 endpoint）：

```bash
DEERFLOW_URL=http://localhost:2026            # Unified proxy base URL
DEERFLOW_GATEWAY_URL=http://localhost:2026    # Gateway API
DEERFLOW_LANGGRAPH_URL=http://localhost:2026/api/langgraph  # LangGraph API
```

完整 API 参考请见 [`skills/public/claude-to-deerflow/SKILL.md`](skills/public/claude-to-deerflow/SKILL.md)。

### Sub-Agents

复杂任务很少能一次完成。DeerFlow 会将其拆解。

主 agent 可以按需动态启动 sub-agents——每个都有自己划定的上下文、工具和停止条件。只要条件允许，sub-agents 就会并行运行，返回结构化结果，然后由主 agent 将它们整合为一致的输出。

这就是 DeerFlow 处理从几分钟到数小时任务的方式：一个研究任务可以扩展为十几个 sub-agents，每个探索不同角度，然后汇聚成一份报告——或一个网站——或一组带生成式视觉内容的幻灯片。一个 harness，多只手同时工作。

### Sandbox 与文件系统

DeerFlow 不只是*谈论*做事。它有属于自己的计算机。

每个任务都在一个隔离的 Docker 容器中运行，并拥有完整的文件系统——skills、workspace、uploads、outputs。agent 可以读取、写入和编辑文件。它会执行 bash 命令和代码。它会查看图像。全部都在 sandbox 中完成，全部可审计，session 之间零污染。

这就是“带工具访问的聊天机器人”和“拥有真实执行环境的 agent”之间的区别。

```
# Paths inside the sandbox container
/mnt/user-data/
├── uploads/          ← your files
├── workspace/        ← agents' working directory
└── outputs/          ← final deliverables
```

### Context Engineering

**Sub-Agent 的隔离上下文**：每个 sub-agent 都在自己的隔离上下文中运行。它既看不到主 agent 的上下文，也看不到其他 sub-agents 的上下文。其目标是确保每个 sub-agent 都专注于自身任务，不被无关信息干扰。

**摘要**：在单个 session 内，DeerFlow 会积极管理上下文——总结已完成的子任务，将中间结果卸载到文件系统，并压缩那些不再需要立即保留的信息。这样它就能在不撑爆上下文窗口的情况下，高效完成长时、多步骤任务。

### 长期记忆

大多数 agent 在对话结束后就会忘记一切。而 DeerFlow 会记住。

在不同 session 之间，DeerFlow 会构建关于你的个人资料、偏好以及累积知识的持久记忆。你用得越多，它就越了解你——你的写作风格、技术栈、重复性的工作流。记忆存储在本地，并始终由你掌控。

现在在应用 memory 更新时，会忽略重复的事实条目，因此重复的偏好和上下文不会再在多个 session 之间无限累积。

## 推荐模型

DeerFlow 对模型本身没有绑定——任何实现 OpenAI 兼容 API 的 LLM 都可以使用。不过，它在支持以下能力的模型上表现更佳：

- **长上下文窗口**（100k+ tokens），适用于深度研究和多步骤任务
- **推理能力**，适用于自适应规划和复杂任务拆解
- **多模态输入**，适用于图像和视频理解
- **可靠的 tool use**，用于稳定的函数调用和结构化输出

## 内置 Python 客户端

DeerFlow 可以作为嵌入式 Python 库使用，而无需启动完整的 HTTP 服务。`DeerFlowClient` 提供对所有 agent 和 Gateway 能力的进程内直接访问，并返回与 Gateway HTTP API 相同的响应 schema。HTTP Gateway 还公开了 `DELETE /api/threads/{thread_id}`，用于在删除 LangGraph thread 后删除 DeerFlow 管理的本地 thread 数据：

```python
from deerflow.client import DeerFlowClient

client = DeerFlowClient()

# Chat
response = client.chat("Analyze this paper for me", thread_id="my-thread")

# Streaming (LangGraph SSE protocol: values, messages-tuple, end)
for event in client.stream("hello"):
    if event.type == "messages-tuple" and event.data.get("type") == "ai":
        print(event.data["content"])

# Configuration & management — returns Gateway-aligned dicts
models = client.list_models()        # {"models": [...]} 
skills = client.list_skills()        # {"skills": [...]} 
client.update_skill("web-search", enabled=True)
client.upload_files("thread-1", ["./report.pdf"])  # {"success": True, "files": [...]}
```

所有返回 dict 的方法都会在 CI 中依据 Gateway 的 Pydantic 响应模型（`TestGatewayConformance`）进行校验，从而确保内置客户端始终与 HTTP API schema 保持同步。完整 API 文档请参见 `backend/packages/harness/deerflow/client.py`。

## 文档

- [贡献指南](CONTRIBUTING.md) - 开发环境搭建与工作流
- [配置指南](backend/docs/CONFIGURATION.md) - 安装和配置说明
- [架构总览](backend/CLAUDE.md) - 技术架构细节
- [后端架构](backend/README.md) - 后端架构与 API 参考

## ⚠️ 安全警告

### 不当部署可能引入安全风险

DeerFlow 具备一些高权限的关键能力，包括**执行系统命令、操作资源以及调用业务逻辑**。默认情况下，它被设计为**部署在受信任的本地环境中（仅通过 127.0.0.1 loopback 接口访问）**。如果你在不受信任的环境中部署该 agent——例如 LAN、公网云服务器或其他可从多个终端访问的环境——且没有采取严格的安全措施，就可能引入以下风险：

- **未授权调用**：agent 的功能可能被未授权第三方或恶意扫描器发现，从而触发大规模未授权请求，执行高风险操作（系统命令、文件读写），并造成严重后果。
- **法律与合规风险**：如果该 agent 被非法用于实施网络攻击、窃取数据或其他违法行为，可能会带来法律责任和合规风险。

### 安全建议

**注意：我们强烈建议将 DeerFlow 部署在受信任的本地网络环境中。** 如果你需要跨设备或跨网络部署，则必须实施严格的安全措施，例如：

- **IP 白名单**：使用 `iptables`，或部署带 ACL 的硬件防火墙/交换机，来**配置 IP 白名单规则**并拒绝其他所有 IP 地址访问。
- **认证网关**：配置反向代理（例如 nginx），并**在上游启用强认证**，阻止任何未认证访问。
- **网络隔离**：如果可能，请将 agent 和受信任设备放在**同一个专用 VLAN** 中，与其他网络设备隔离。
- **持续关注**：持续跟进 DeerFlow 项目的安全更新。

## 贡献

欢迎贡献！请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)，了解开发环境搭建、工作流和约定。

回归测试覆盖了 Docker sandbox 模式检测，以及 `backend/tests/` 中 provisioner 的 kubeconfig-path 处理测试。

## 许可证

本项目是开源项目，基于 [MIT 许可证](./LICENSE) 发布。

## 致谢

DeerFlow 建立在开源社区卓越成果之上。我们由衷感谢所有让 DeerFlow 成为可能的项目和贡献者。我们确实是站在巨人的肩膀上前行。

我们特别想向以下项目致以诚挚谢意，感谢它们带来的宝贵贡献：

- **[LangChain](https://github.com/langchain-ai/langchain)**：其出色的框架驱动了我们的 LLM 交互和 chains，实现了顺畅的集成与功能支持。
- **[LangGraph](https://github.com/langchain-ai/langgraph)**：其创新的多 agent 编排方式，对 DeerFlow 的复杂工作流起到了决定性作用。

这些项目展现了开源协作的变革性力量，我们也很自豪能建立在它们的基础之上。

### 核心贡献者

特别感谢 `DeerFlow` 的主要作者们，正是他们的愿景、热情与投入让这个项目成为现实：

- **[Daniel Walnut](https://github.com/hetaoBackend/)**
- **[Henry Li](https://github.com/magiccube/)**

你们始终如一的投入和专业能力推动着 DeerFlow 的成功。能够由你们掌舵这段旅程，我们深感荣幸。

## Star 历史

[![Star 历史图表](https://api.star-history.com/svg?repos=bytedance/deer-flow&type=Date)](https://star-history.com/#bytedance/deer-flow&Date)
