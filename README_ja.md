# 🦌 DeerFlow - 2.0

[英语](./README.md) | [中文](./README_zh.md) | 日语 | [法语](./README_fr.md) | [俄语](./README_ru.md)

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](./backend/pyproject.toml)
[![Node.js](https://img.shields.io/badge/Node.js-22%2B-339933?logo=node.js&logoColor=white)](./Makefile)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

<a href="https://trendshift.io/repositories/14699" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14699" alt="bytedance%2Fdeer-flow | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
> 2026年2月28日，随着 2.0 版本发布，DeerFlow 荣登 GitHub Trending 🏆 第 1 名。感谢这个出色的社区！💪🔥

DeerFlow（**D**eep **E**xploration and **E**fficient **R**esearch **Flow**）是一个开源的**超级智能体 harness**，集成了 **sub-agents**、**memory** 和 **sandbox**，并可通过可扩展的 **skills** 执行各种任务。

https://github.com/user-attachments/assets/a8bcadc4-e040-4cf2-8fda-dd768b999c18

> [!NOTE]
> **DeerFlow 2.0 是一次从零开始的彻底重写。** 它与 v1 不共享代码。如果你在寻找原始的 Deep Research 框架，它仍在 [`1.x` 分支](https://github.com/bytedance/deer-flow/tree/main-1.x) 中持续维护。当前开发已转向 2.0。

## 官方网站

[<img width="2880" height="1600" alt="image" src="https://github.com/user-attachments/assets/a598c49f-3b2f-41ea-a052-05e21349188a" />](https://deerflow.tech)

**真实演示**可在[**官方网站**](https://deerflow.tech)查看。

## ByteDance Volcengine Coding Plan

<img width="4808" height="2400" alt="英文方舟" src="https://github.com/user-attachments/assets/2ecc7b9d-50be-4185-b1f7-5542d222fb2d" />

- 强烈推荐使用 Doubao-Seed-2.0-Code、DeepSeek v3.2 和 Kimi 2.5 运行 DeerFlow
- [点击查看详情](https://www.byteplus.com/en/activity/codingplan?utm_campaign=deer_flow&utm_content=deer_flow&utm_medium=devrel&utm_source=OWO&utm_term=deer_flow)
- [中国大陆开发者请点击这里](https://www.volcengine.com/activity/codingplan?utm_campaign=deer_flow&utm_content=deer_flow&utm_medium=devrel&utm_source=OWO&utm_term=deer_flow)

## InfoQuest

DeerFlow 现已集成由 BytePlus 自主开发的智能搜索与抓取工具套件「[InfoQuest（支持免费在线体验）](https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest)」。

<a href="https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest" target="_blank">
  <img
    src="https://sf16-sg.tiktokcdn.com/obj/eden-sg/hubseh7bsbps/20251208-160108.png"   alt="InfoQuest_banner"
  />
</a>

---

## 目录

- [🦌 DeerFlow - 2.0](#-deerflow---20)
  - [官方网站](#官方网站)
  - [InfoQuest](#infoquest)
  - [目录](#目录)
  - [用一句话让 Coding Agent 完成安装](#用一句话让-coding-agent-完成安装)
  - [快速开始](#快速开始)
    - [配置](#配置)
    - [运行应用](#运行应用)
      - [选项 1：Docker（推荐）](#选项-1docker推荐)
      - [选项 2：本地开发](#选项-2本地开发)
    - [高级配置](#高级配置)
      - [Sandbox 模式](#sandbox-模式)
      - [MCP 服务器](#mcp-服务器)
      - [IM 渠道](#im-渠道)
      - [LangSmith 链路追踪](#langsmith-链路追踪)
  - [从 Deep Research 到 Super Agent Harness](#从-deep-research-到-super-agent-harness)
  - [核心特性](#核心特性)
    - [Skills 与 Tools](#skills-与-tools)
      - [Claude Code 集成](#claude-code-集成)
    - [Sub-agents](#sub-agents)
    - [Sandbox 与文件系统](#sandbox-与文件系统)
    - [Context Engineering](#context-engineering)
    - [长期记忆](#长期记忆)
  - [推荐模型](#推荐模型)
  - [内嵌 Python 客户端](#内嵌-python-客户端)
  - [文档](#文档)
  - [⚠️ 安全注意事项](#️-安全注意事项)
  - [参与贡献](#参与贡献)
  - [许可证](#许可证)
  - [致谢](#致谢)
    - [核心贡献者](#核心贡献者)
  - [Star 历史](#star-历史)

## 用一句话让 Coding Agent 完成安装

如果你正在使用 Claude Code、Codex、Cursor、Windsurf 等 coding agent，可以直接把下面这句话原样发给它。

```text
DeerFlow がまだ clone されていなければ先に clone してから、https://raw.githubusercontent.com/bytedance/deer-flow/main/Install.md に従ってローカル開発環境を初期化してください
```

这条提示词是给 coding agent 用的。如有需要，它会先 clone 仓库；如果可以使用 Docker，则优先用 Docker 完成初始设置；最后只会返回下一条启动命令以及仍缺失的配置项。

## 快速开始

### 配置

1. **克隆 DeerFlow 仓库**

   ```bash
   git clone https://github.com/bytedance/deer-flow.git
   cd deer-flow
   ```

2. **生成本地配置文件**

   在项目根目录（`deer-flow/`）执行以下命令：

   ```bash
   make config
   ```

   该命令会基于提供的模板创建本地配置文件。

3. **配置要使用的模型**

   编辑 `config.yaml`，至少定义一个模型：

   ```yaml
   models:
     - name: gpt-4                       # 内部識別子
       display_name: GPT-4               # 表示名
       use: langchain_openai:ChatOpenAI  # LangChainクラスパス
       model: gpt-4                      # API用モデル識別子
       api_key: $OPENAI_API_KEY          # APIキー（推奨：環境変数を使用）
       max_tokens: 4096                  # リクエストあたりの最大トークン数
       temperature: 0.7                  # サンプリング温度

     - name: openrouter-gemini-2.5-flash
       display_name: Gemini 2.5 Flash (OpenRouter)
       use: langchain_openai:ChatOpenAI
       model: google/gemini-2.5-flash-preview
       api_key: $OPENAI_API_KEY          # OpenRouterもここではOpenAI互換のフィールド名を使用
       base_url: https://openrouter.ai/api/v1
   ```

   对于 OpenRouter 和 OpenAI 兼容网关，使用 `langchain_openai:ChatOpenAI` 与 `base_url` 进行配置即可。如果你想使用 provider 专属的环境变量名，也可以在 `api_key` 中显式指定该变量（例如：`api_key: $OPENROUTER_API_KEY`）。

4. **为已配置的模型设置 API key**

   请选择以下任一方式：

- 选项 A：编辑项目根目录下的 `.env` 文件（推荐）

   ```bash
   TAVILY_API_KEY=your-tavily-api-key
   OPENAI_API_KEY=your-openai-api-key
   # OpenRouterもlangchain_openai:ChatOpenAI + base_url使用時はOPENAI_API_KEYを使用します。
   # 必要に応じて他のプロバイダーキーを追加
   INFOQUEST_API_KEY=your-infoquest-api-key
   ```

- 选项 B：在 shell 中导出环境变量

   ```bash
   export OPENAI_API_KEY=your-openai-api-key
   ```

- 选项 C：直接编辑 `config.yaml`（不建议用于生产环境）

   ```yaml
   models:
     - name: gpt-4
       api_key: your-actual-api-key-here  # プレースホルダーを置換
   ```

### 运行应用

#### 选项 1：Docker（推荐）

**开发环境**（热重载、挂载源代码）：

```bash
make docker-init    # サンドボックスイメージをプル（初回またはイメージ更新時のみ）
make docker-start   # サービスを開始（config.yamlからサンドボックスモードを自動検出）
```

`make docker-start` 仅会在 `config.yaml` 使用 provisioner 模式（`sandbox.use: deerflow.community.aio_sandbox:AioSandboxProvider` 与 `provisioner_url`）时启动 `provisioner`。

**生产环境**（在本地构建镜像，并挂载运行时配置与数据）：

```bash
make up     # イメージをビルドして全本番サービスを開始
make down   # コンテナを停止して削除
```

> [!NOTE]
> Agent 运行时当前在 Gateway 内执行。`/api/langgraph/*` 会由 nginx 重写到 Gateway 的 LangGraph-compatible API。

访问地址：http://localhost:2026

更详细的 Docker 开发指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

#### 选项 2：本地开发

如果要在本地运行服务：

前提条件：请先完成上面的“配置”步骤（`make config` 和模型 API key）。`make dev` 需要有效的配置文件（默认是项目根目录下的 `config.yaml`，也可通过 `DEER_FLOW_CONFIG_PATH` 覆盖）。

1. **检查前置依赖**：
   ```bash
   make check  # Node.js 22+、pnpm、uv、nginxを検証
   ```

2. **安装依赖**：
   ```bash
   make install  # バックエンド＋フロントエンドの依存関係をインストール
   ```

3. **（可选）预拉取 sandbox 镜像**：
   ```bash
   # Docker/コンテナベースのサンドボックス使用時に推奨
   make setup-sandbox
   ```

4. **启动服务**：
   ```bash
   make dev
   ```

5. **访问地址**：http://localhost:2026

### 高级配置
#### Sandbox 模式

DeerFlow 支持多种 sandbox 执行模式：
- **本地执行**（直接在主机上运行 sandbox 代码）
- **Docker 执行**（在隔离的 Docker 容器内运行 sandbox 代码）
- **通过 Kubernetes 的 Docker 执行**（经由 provisioner 服务在 Kubernetes Pod 中运行 sandbox 代码）

在 Docker 开发环境中，服务启动会遵循 `config.yaml` 中的 sandbox 模式。对于本地/Docker 模式，不会启动 `provisioner`。

有关你所偏好模式的配置方式，请参阅 [Sandbox 配置指南](backend/docs/CONFIGURATION.md#sandbox)。

#### MCP 服务器

DeerFlow 支持可配置的 MCP 服务器与 skills 来扩展能力。
对于 HTTP/SSE MCP 服务器，支持 OAuth token 流程（`client_credentials`、`refresh_token`）。
详细步骤请参阅 [MCP 服务器指南](backend/docs/MCP_SERVER.md)。

#### IM 渠道

DeerFlow 支持从消息应用接收任务。完成配置后，各渠道会自动启动，并且都不需要公网 IP。

| 渠道 | 传输方式 | 难度 |
|---------|-----------|------------|
| Telegram | Bot API（长轮询） | 简单 |
| Slack | Socket Mode | 中等 |
| Feishu / Lark | WebSocket | 中等 |
| DingTalk | Stream Push（WebSocket） | 中等 |

**在 `config.yaml` 中配置：**

```yaml
channels:
  # LangGraph-compatible Gateway API base URL（デフォルト: http://localhost:8001/api）
  langgraph_url: http://localhost:8001/api
  # Gateway API URL（デフォルト: http://localhost:8001）
  gateway_url: http://localhost:8001

  # オプション: 全モバイルチャネルのグローバルセッションデフォルト
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
    app_token: $SLACK_APP_TOKEN     # xapp-...（Socket Mode）
    allowed_users: []               # 空 = 全員許可

  telegram:
    enabled: true
    bot_token: $TELEGRAM_BOT_TOKEN
    allowed_users: []               # 空 = 全員許可

    # オプション: チャネル/ユーザーごとのセッション設定
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
    client_id: $DINGTALK_CLIENT_ID             # DingTalk Open PlatformのClientId
    client_secret: $DINGTALK_CLIENT_SECRET     # DingTalk Open PlatformのClientSecret
    allowed_users: []                          # 空 = 全員許可
    card_template_id: ""                       # オプション：ストリーミングタイプライター効果用のAIカードテンプレートID
```

在 `.env` 文件中设置对应的 API key：

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

**Telegram 设置**

1. 与 [@BotFather](https://t.me/BotFather) 对话，发送 `/newbot`，然后复制 HTTP API token。
2. 在 `.env` 中设置 `TELEGRAM_BOT_TOKEN`，并在 `config.yaml` 中启用该渠道。

**Slack 设置**

1. 在 [api.slack.com/apps](https://api.slack.com/apps) 创建 Slack 应用 → Create New App → From scratch。
2. 在 **OAuth & Permissions** 中添加 Bot token scopes：`app_mentions:read`、`chat:write`、`im:history`、`im:read`、`im:write`、`files:write`。
3. 启用 **Socket Mode** → 创建带有 `connections:write` scope 的 App-Level token（`xapp-…`）。
4. 在 **Event Subscriptions** 中订阅 bot events：`app_mention`、`message.im`。
5. 在 `.env` 中设置 `SLACK_BOT_TOKEN` 与 `SLACK_APP_TOKEN`，并在 `config.yaml` 中启用该渠道。

**Feishu / Lark 设置**

1. 在 [Feishu Open Platform](https://open.feishu.cn/) 创建应用 → 启用 **机器人** 功能。
2. 添加权限：`im:message`、`im:message.p2p_msg:readonly`、`im:resource`。
3. 在 **事件** 中订阅 `im.message.receive_v1`，并选择 **长连接** 模式。
4. 复制 App ID 与 App Secret。在 `.env` 中设置 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`，并在 `config.yaml` 中启用该渠道。

**DingTalk 设置**

1. 在 [DingTalk Open Platform](https://open.dingtalk.com/) 创建应用，并启用 **机器人** 功能。
2. 在机器人配置页面，将消息接收模式设置为 **Stream 模式**。
3. 复制 `Client ID` 和 `Client Secret`。在 `.env` 中设置 `DINGTALK_CLIENT_ID` 与 `DINGTALK_CLIENT_SECRET`，并在 `config.yaml` 中启用该渠道。
4. *（可选）* 若要启用流式 AI 卡片回复（打字机效果），请在 [DingTalk 卡片平台](https://open.dingtalk.com/document/dingstart/typewriter-effect-streaming-ai-card) 中创建 **AI 卡片** 模板，并将模板 ID 填入 `config.yaml` 的 `card_template_id`。还需要申请 `Card.Streaming.Write` 和 `Card.Instance.Write` 权限。

**命令**

连接渠道后，你可以直接在聊天中与 DeerFlow 交互：

| 命令 | 说明 |
|---------|-------------|
| `/new` | 开始新会话 |
| `/status` | 显示当前线程信息 |
| `/models` | 列出可用模型 |
| `/memory` | 显示记忆 |
| `/help` | 显示帮助 |

> 没有命令前缀的消息会被视为普通聊天，DeerFlow 会创建线程，并以对话形式回复。

#### LangSmith 链路追踪

DeerFlow 内置了 [LangSmith](https://smith.langchain.com) 可观测性。启用后，所有 LLM 调用、agent 执行和 tool 执行都会被追踪，并可在 LangSmith 仪表板中查看。

在 `.env` 文件中添加以下内容：

```bash
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxx
LANGSMITH_PROJECT=xxx
```

在 Docker 部署中，追踪默认处于关闭状态。可通过在 `.env` 中设置 `LANGSMITH_TRACING=true` 和 `LANGSMITH_API_KEY` 来启用。

## 从 Deep Research 到 Super Agent Harness

DeerFlow 起初是一个 Deep Research 框架，而社区将它推进到了更大的规模。自发布以来，开发者已经把它用在研究之外的场景：构建数据管道、生成幻灯片、搭建仪表板、自动化内容工作流。这些都超出了我们的最初预期。

这说明了一件重要的事：DeerFlow 不只是一个研究工具。它是一个**harness**——为 agent 真正完成工作提供基础设施的运行时。

因此，我们从零开始重建了它。

DeerFlow 2.0 不再是一个东拼西凑的框架，而是一个开箱即用、完全可扩展的 super agent harness。它构建在 LangGraph 和 LangChain 之上，默认提供 agent 所需的一切：文件系统、memory、skills、sandbox 执行，以及面向复杂多步骤任务的规划与 sub-agent 生成能力。

你可以直接使用；也可以拆开后改造成你自己的系统。

## 核心特性

### Skills 与 Tools

正是 skills 让 DeerFlow *几乎无所不能*。

标准的 agent skill 是结构化的功能模块——以 Markdown 文件形式定义工作流、最佳实践以及对支持资源的引用。DeerFlow 内置了研究、报告生成、幻灯片制作、网页创建、图像与视频生成等 skills。但真正的力量来自扩展性：你可以添加自己的 skill、替换内置 skill，并将它们组合成复合工作流。

Skills 会渐进加载——只有在任务需要时才会加载，而不是一次性全部载入。这能让上下文窗口保持轻量，使 DeerFlow 即使在对 token 敏感的模型上也能良好运行。

通过 Gateway 安装 `.skill` 归档时，DeerFlow 接受 `version`、`author`、`compatibility` 等标准的可选 frontmatter 元数据，不会拒绝有效的外部 skills。

Tools 也遵循同样的理念。DeerFlow 内置一组核心 tools——Web 搜索、Web 抓取、文件操作、bash 执行——并支持通过 MCP 服务器和 Python 函数扩展自定义 tools。任何部分都可以替换，也可以继续添加。

Gateway 生成的后续建议会在解析 JSON 数组响应之前，同时规范化纯字符串模型输出和块/列表形式的富内容，因此 provider 特定的内容包装不会再悄悄丢弃建议。

```
# サンドボックスコンテナ内のパス
/mnt/skills/public
├── research/SKILL.md
├── report-generation/SKILL.md
├── slide-creation/SKILL.md
├── web-page/SKILL.md
└── image-generation/SKILL.md

/mnt/skills/custom
└── your-custom-skill/SKILL.md      ← あなたのカスタムスキル
```

#### Claude Code 集成

借助 `claude-to-deerflow` skill，你可以直接从 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 与正在运行的 DeerFlow 实例交互。发送研究任务、检查状态、管理线程——全部都无需离开终端。

**安装 skill：**

```bash
npx skills add https://github.com/bytedance/deer-flow --skill claude-to-deerflow
```

请确保 DeerFlow 正在运行（默认地址为 `http://localhost:2026`），然后在 Claude Code 中使用 `/claude-to-deerflow` 命令。

**你可以做什么：**
- 向 DeerFlow 发送消息并获取流式响应
- 选择运行模式：flash（高速）、standard、pro（规划）、ultra（sub-agent）
- 对 DeerFlow 执行健康检查，列出模型/skills/agents
- 管理线程和对话历史
- 上传文件以供分析

**环境变量**（可选，用于自定义端点）：

```bash
DEERFLOW_URL=http://localhost:2026            # 統合プロキシベースURL
DEERFLOW_GATEWAY_URL=http://localhost:2026    # Gateway API
DEERFLOW_LANGGRAPH_URL=http://localhost:2026/api/langgraph  # LangGraph API
```

完整的 API 参考请参阅 [`skills/public/claude-to-deerflow/SKILL.md`](skills/public/claude-to-deerflow/SKILL.md)。

### Sub-agents

复杂任务不会只沿着单一路径推进，DeerFlow 会把它拆开。

lead agent 可以按需即时生成 sub-agents——每个都拥有自己的作用域上下文、tools 和结束条件。sub-agents 会尽可能并行运行，返回结构化结果，再由 lead agent 将一切整合为一致的输出。

这就是 DeerFlow 处理需要几分钟到几小时任务的方式：一个研究任务可以展开为十几个 sub-agents，分别从不同角度探索，最后汇聚成一份报告——或者一个网站——或者一套带生成式视觉内容的幻灯片。一个 harness，许多双手。

### Sandbox 与文件系统

DeerFlow 不只是*谈论*事情。它拥有自己的计算机。

每个任务都在一个具备完整文件系统的隔离 Docker 容器中运行——包含 skills、workspace、uploads 和 outputs。agent 可以读、写、编辑文件；执行 bash 命令；编写代码；查看图像。一切都被 sandbox 化，一切都可审计，而且会话之间零污染。

这正是“拥有工具访问的聊天机器人”和“拥有真实执行环境的 agent”之间的区别。

```
# サンドボックスコンテナ内のパス
/mnt/user-data/
├── uploads/          ← あなたのファイル
├── workspace/        ← エージェントの作業ディレクトリ
└── outputs/          ← 最終成果物
```

### Context Engineering

**隔离的 sub-agent 上下文**：每个 sub-agent 都在自己隔离的上下文中运行。因此，sub-agent 无法看到主 agent 或其他 sub-agent 的上下文。这一点很重要，因为它能让 sub-agent 专注于眼前任务，而不会被主 agent 或其他 sub-agent 的上下文分散注意力。

**摘要化**：在一个会话中，DeerFlow 会主动管理上下文——总结已完成的子任务，把中间结果卸载到文件系统，并压缩那些已不再直接相关的内容。这样它就能在不超出上下文窗口的前提下，在漫长的多步骤任务中始终保持清晰。

### 长期记忆

大多数 agent 在对话结束后就会忘掉一切。DeerFlow 会记住。

跨会话地，DeerFlow 会为你的个人资料、偏好和累计知识构建持久记忆。你用得越多，它就越了解你——你的写作风格、技术栈以及重复出现的工作流。记忆保存在本地，并由你掌控。

现在，在应用记忆更新时会跳过重复的事实条目，因此重复的偏好或上下文不会在跨会话过程中无限累积。

## 推荐模型

DeerFlow 不依赖任何特定模型——任何实现 OpenAI 兼容 API 的 LLM 都可以运行它。不过，在支持以下能力的模型上表现最佳：

- **长上下文窗口**（10 万 tokens 以上）：适合深度研究与多步骤任务
- **推理能力**：适合自适应规划和复杂拆解
- **多模态输入**：适合图像理解与视频理解
- **强大的工具使用能力**：适合可靠的 function calling 和结构化输出

## 内嵌 Python 客户端

DeerFlow 也可以作为内嵌 Python 库使用，而无需运行完整的 HTTP 服务。`DeerFlowClient` 提供了对全部 agent 与 Gateway 功能的进程内直接访问，并返回与 HTTP Gateway API 相同的响应 schema：

```python
from deerflow.client import DeerFlowClient

client = DeerFlowClient()

# チャット
response = client.chat("Analyze this paper for me", thread_id="my-thread")

# ストリーミング（LangGraph SSEプロトコル：values、messages-tuple、end）
for event in client.stream("hello"):
    if event.type == "messages-tuple" and event.data.get("type") == "ai":
        print(event.data["content"])

# 設定＆管理 — Gateway準拠のdictを返す
models = client.list_models()        # {"models": [...]}
skills = client.list_skills()        # {"skills": [...]}
client.update_skill("web-search", enabled=True)
client.upload_files("thread-1", ["./report.pdf"])  # {"success": True, "files": [...]}
```

所有返回 dict 的方法都会在 CI 中针对 Gateway 的 Pydantic 响应模型进行校验（`TestGatewayConformance`），以确保内嵌客户端与 HTTP API schema 保持同步。完整 API 文档请参阅 `backend/packages/harness/deerflow/client.py`。

## 文档

- [贡献指南](CONTRIBUTING.md) - 开发环境设置与工作流
- [配置指南](backend/docs/CONFIGURATION.md) - 安装与配置步骤
- [架构概览](backend/CLAUDE.md) - 技术架构细节
- [后端架构](backend/README.md) - 后端架构与 API 参考

## ⚠️ 安全注意事项

### 不当部署可能带来安全风险

DeerFlow 具备**执行系统命令、操作资源、调用业务逻辑**等高权限关键能力，默认设计为**部署在本地可信环境中（仅允许 127.0.0.1 回环访问）**。如果将 agent 部署在不受信任的局域网、公共云服务器，或可被多个端点访问的网络环境中，而又没有采取严格的安全措施，可能会带来如下安全风险：

- **未授权的非法调用**：agent 的能力可能被未授权第三方或恶意互联网扫描器发现，并触发未授权批量请求来执行系统命令、读写文件等高风险操作，从而造成严重安全问题。
- **合规与法律风险**：如果 agent 被滥用于网络攻击、数据窃取等违法行为，可能会引发法律责任和合规风险。

### 安全建议

**注意：强烈建议将 DeerFlow 部署在本地可信网络环境中。** 如果必须进行跨设备、跨网络部署，则应实施以下严格的安全措施：

- **配置 IP 白名单**：使用 `iptables`，或部署带有 ACL 功能的硬件防火墙 / 交换机，**设置 IP 白名单规则**，拒绝其他所有 IP 地址的访问。
- **前置认证**：配置反向代理（如 nginx），并**启用强前置认证**，阻止未认证访问。
- **网络隔离**：如有可能，将 agent 与可信设备放在**同一个专用 VLAN** 中，与其他网络设备隔离。
- **持续关注更新**：请持续关注 DeerFlow 安全能力的更新。

## 参与贡献

欢迎贡献！关于开发环境设置、工作流和相关指南，请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

回归测试覆盖范围包括 `backend/tests/` 中的 Docker sandbox 模式检测，以及 provisioner kubeconfig-path 处理测试。

## 许可证

本项目是开源项目，基于 [MIT 许可证](./LICENSE) 提供。

## 致谢

DeerFlow 建立在开源社区的杰出成果之上。我们衷心感谢所有让 DeerFlow 成为可能的项目和贡献者。可以说，我们正站在巨人的肩膀上。

我们由衷感谢以下项目的重要贡献：

- **[LangChain](https://github.com/langchain-ai/langchain)**：其出色的框架为 LLM 交互与链式调用提供了支撑，实现了无缝集成与丰富能力。
- **[LangGraph](https://github.com/langchain-ai/langgraph)**：其在多 agent 编排上的创新方法，为 DeerFlow 实现复杂工作流作出了巨大贡献。

这些项目体现了开源协作的变革力量，我们也为能够构建在它们的基础之上而感到自豪。

### 核心贡献者

向 `DeerFlow` 的核心作者致以诚挚谢意。正是他们的愿景、热情与奉献，赋予了这个项目生命：

- **[Daniel Walnut](https://github.com/hetaoBackend/)**
- **[Henry Li](https://github.com/magiccube/)**

他们坚定不移的投入和专业能力，是 DeerFlow 成功的驱动力。我们很荣幸能与他们一同走在这段旅程的前列。

## Star 历史

[![Star History 图表](https://api.star-history.com/svg?repos=bytedance/deer-flow&type=Date)](https://star-history.com/#bytedance/deer-flow&Date)
