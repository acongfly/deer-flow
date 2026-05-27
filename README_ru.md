# 🦌 DeerFlow - 2.0

[英语](./README.md) | [中文](./README_zh.md) | [日语](./README_ja.md) | [法语](./README_fr.md) | 俄语

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](./backend/pyproject.toml)
[![Node.js](https://img.shields.io/badge/Node.js-22%2B-339933?logo=node.js&logoColor=white)](./Makefile)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

<a href="https://trendshift.io/repositories/14699" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14699" alt="bytedance%2Fdeer-flow | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

> 2026 年 2 月 28 日，DeerFlow 发布 2 之后登上 GitHub Trending 🏆 #1。非常感谢我们的社区——这一切都离不开你们！💪🔥

DeerFlow（**D**eep **E**xploration and **E**fficient **R**esearch **Flow**）是一个开源的 **Super Agent Harness**，用于编排 **Sub-Agents**、**Memory** 和 **Sandbox**，从而解决几乎任何任务。所有能力都建立在可扩展的 **Skills** 之上。

https://github.com/user-attachments/assets/a8bcadc4-e040-4cf2-8fda-dd768b999c18

> [!NOTE]
> **DeerFlow 2.0 是从零重写的项目。** 它与 v1 没有任何共用代码。如果你需要原版 Deep Research 框架——它仍然在 [`1.x`](https://github.com/bytedance/deer-flow/tree/main-1.x) 分支中，也同样欢迎贡献。当前活跃开发集中在 2.0。

## 官网

[<img width="2880" height="1600" alt="image" src="https://github.com/user-attachments/assets/a598c49f-3b2f-41ea-a052-05e21349188a" />](https://deerflow.tech)

更多信息和在线实时演示请访问[**官网**](https://deerflow.tech)。

## 字节跳动火山引擎 Coding Plan

<img width="4808" height="2400" alt="英文方舟" src="https://github.com/user-attachments/assets/2ecc7b9d-50be-4185-b1f7-5542d222fb2d" />

- 我们推荐使用 Doubao-Seed-2.0-Code、DeepSeek v3.2 和 Kimi 2.5 来运行 DeerFlow
- [了解更多](https://www.byteplus.com/en/activity/codingplan?utm_campaign=deer_flow&utm_content=deer_flow&utm_medium=devrel&utm_source=OWO&utm_term=deer_flow)
- [面向中国大陆开发者](https://www.volcengine.com/activity/codingplan?utm_campaign=deer_flow&utm_content=deer_flow&utm_medium=devrel&utm_source=OWO&utm_term=deer_flow)

## InfoQuest

DeerFlow 已集成 BytePlus 的智能搜索与爬取工具集——[InfoQuest（提供免费在线访问）](https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest)

<a href="https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest" target="_blank">
  <img
    src="https://sf16-sg.tiktokcdn.com/obj/eden-sg/hubseh7bsbps/20251208-160108.png"
    alt="InfoQuest_banner"
  />
</a>

---

## 目录

- [🦌 DeerFlow - 2.0](#-deerflow---20)
  - [官网](#官网)
  - [InfoQuest](#infoquest)
  - [目录](#目录)
  - [给 coding agent 的一句话安装指令](#给-coding-agent-的一句话安装指令)
  - [快速开始](#快速开始)
    - [配置](#配置)
    - [启动](#启动)
      - [方式 1：Docker（推荐）](#方式-1docker推荐)
      - [方式 2：本地开发](#方式-2本地开发)
    - [补充内容](#补充内容)
      - [Sandbox 模式](#sandbox-模式)
      - [MCP 服务器](#mcp-服务器)
      - [消息应用](#消息应用)
      - [LangSmith 跟踪](#langsmith-跟踪)
  - [从 Deep Research 到 Super Agent Harness](#从-deep-research-到-super-agent-harness)
  - [核心特性](#核心特性)
    - [Skills & Tools](#skills--tools)
      - [与 Claude Code 集成](#与-claude-code-集成)
    - [Sub-Agents](#sub-agents)
    - [Sandbox 与文件系统](#sandbox-与文件系统)
    - [Context Engineering](#context-engineering)
    - [长期记忆](#长期记忆)
  - [推荐模型](#推荐模型)
  - [内置 Python 客户端](#内置-python-客户端)
  - [文档](#文档)
  - [⚠️ 安全](#️-安全)
  - [参与开发](#参与开发)
  - [许可证](#许可证)
  - [鸣谢](#鸣谢)
    - [核心贡献者](#核心贡献者)
  - [Star 历史](#star-历史)

## 给 coding agent 的一句话安装指令

如果你正在使用 Claude Code、Codex、Cursor、Windsurf 或其他 coding agent，只需把下面这句话发给它：

```text
Если DeerFlow еще не клонирован, сначала клонируй его, а затем подготовь локальное окружение разработки по инструкции https://raw.githubusercontent.com/bytedance/deer-flow/main/Install.md
```

这条 prompt 是给 coding agent 用的。它要求 agent 在需要时先克隆仓库，在可用时优先选择 Docker，并在最后返回准确的启动命令以及仍然缺失的配置项列表。

## 快速开始

### 配置

1. **克隆 DeerFlow 仓库**

   ```bash
   git clone https://github.com/bytedance/deer-flow.git
   cd deer-flow
   ```

2. **生成本地配置**

   在项目根目录（`deer-flow/`）中运行：

   ```bash
   make config
   ```

   该命令会基于模板生成本地配置文件。

3. **配置模型**

   编辑 `config.yaml`，并至少设置一个模型：

   ```yaml
   models:
     - name: gpt-4                       # Внутренний идентификатор
       display_name: GPT-4               # Отображаемое имя
       use: langchain_openai:ChatOpenAI  # Путь к классу LangChain
       model: gpt-4                      # Идентификатор модели для API
       api_key: $OPENAI_API_KEY          # API-ключ (рекомендуется: переменная окружения)
       max_tokens: 4096                  # Максимальное количество токенов на запрос
       temperature: 0.7                  # Температура сэмплирования

     - name: openrouter-gemini-2.5-flash
       display_name: Gemini 2.5 Flash (OpenRouter)
       use: langchain_openai:ChatOpenAI
       model: google/gemini-2.5-flash-preview
       api_key: $OPENAI_API_KEY
       base_url: https://openrouter.ai/api/v1

     - name: gpt-5-responses
       display_name: GPT-5 (Responses API)
       use: langchain_openai:ChatOpenAI
       model: gpt-5
       api_key: $OPENAI_API_KEY
       use_responses_api: true
       output_version: responses/v1
   ```

   OpenRouter 和类似的 OpenAI 兼容网关通过带有 `base_url` 参数的 `langchain_openai:ChatOpenAI` 进行配置。对于 CLI provider：

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
   - Claude Code 支持 `CLAUDE_CODE_OAUTH_TOKEN`、`ANTHROPIC_AUTH_TOKEN` 或 `~/.claude/.credentials.json`
   - 在 macOS 上，如有需要请显式导出 Claude Code 认证信息：

   ```bash
   eval "$(python3 scripts/export_claude_code_oauth.py --print-export)"
   ```

4. **指定 API keys**

   - **方式 A**：在项目根目录创建 `.env` 文件（推荐）

   ```bash
   TAVILY_API_KEY=your-tavily-api-key
   OPENAI_API_KEY=your-openai-api-key
   INFOQUEST_API_KEY=your-infoquest-api-key
   ```

   - **方式 B**：在终端中设置环境变量

   ```bash
   export OPENAI_API_KEY=your-openai-api-key
   ```

   - **方式 C**：直接写入 `config.yaml`（不推荐用于生产环境）

### 启动

#### 方式 1：Docker（推荐）

**开发环境**（hot-reload、挂载源码）：

```bash
make docker-init    # Загрузить образ Sandbox (один раз или при обновлении)
make docker-start   # Запустить сервисы
```

**生产环境**（本地构建镜像）：

```bash
make up     # Собрать образы и запустить все сервисы
make down   # Остановить и удалить контейнеры
```

> [!TIP]
> 在 Linux 上，如果 Docker daemon 出现 `permission denied` 错误，请把当前用户加入 `docker` 组并重新登录。详见 [CONTRIBUTING.md](CONTRIBUTING.md#linux-docker-daemon-permission-denied)。

地址：http://localhost:2026

#### 方式 2：本地开发

1. **检查依赖项**:
   ```bash
   make check  # Проверяет Node.js 22+, pnpm, uv, nginx
   ```

2. **安装依赖**:
   ```bash
   make install
   ```

3. **（可选）提前拉取 Sandbox 镜像**:
   ```bash
   make setup-sandbox
   ```

4. **启动服务**:
   ```bash
   make dev
   ```

5. **地址**: http://localhost:2026

### 补充内容

#### Sandbox 模式

DeerFlow 支持多种执行模式：
- **本地执行** —— 代码直接在宿主机上运行
- **Docker** —— 代码在隔离的 Docker 容器中运行
- **Docker + Kubernetes** —— 通过 provisioner 在 Kubernetes Pod 中执行

更多信息请参见 [Sandbox 配置指南](backend/docs/CONFIGURATION.md#sandbox)。

#### MCP 服务器

DeerFlow 支持可配置的 MCP 服务器以扩展能力。对于 HTTP/SSE MCP 服务器，还支持 OAuth tokens（`client_credentials`、`refresh_token`）。详见 [MCP 服务器指南](backend/docs/MCP_SERVER.md)。

#### 消息应用

DeerFlow 可以直接从消息应用中接收任务。配置完成后，各个渠道会自动启动，不需要公网 IP。

| 渠道 | 传输方式 | 复杂度 |
|-------|-----------|-----------|
| Telegram | Bot API (long-polling) | 简单 |
| Slack | Socket Mode | 中等 |
| Feishu / Lark | WebSocket | 中等 |
| DingTalk | Stream Push (WebSocket) | 中等 |

**`config.yaml` 中的配置：**

```yaml
channels:
  feishu:
    enabled: true
    app_id: $FEISHU_APP_ID
    app_secret: $FEISHU_APP_SECRET
    # domain: https://open.feishu.cn       # China (default)
    # domain: https://open.larksuite.com   # International

  slack:
    enabled: true
    bot_token: $SLACK_BOT_TOKEN
    app_token: $SLACK_APP_TOKEN
    allowed_users: []

  telegram:
    enabled: true
    bot_token: $TELEGRAM_BOT_TOKEN
    allowed_users: []

  dingtalk:
    enabled: true
    client_id: $DINGTALK_CLIENT_ID             # ClientId с DingTalk Open Platform
    client_secret: $DINGTALK_CLIENT_SECRET     # ClientSecret с DingTalk Open Platform
    allowed_users: []                          # пусто = разрешить всем
    card_template_id: ""                       # Опционально: ID шаблона AI Card для потокового эффекта печатной машинки
```

**Telegram 配置**

1. 给 [@BotFather](https://t.me/BotFather) 发送消息，执行 `/newbot`，然后复制 HTTP API token。
2. 在 `.env` 中设置 `TELEGRAM_BOT_TOKEN`，并在 `config.yaml` 中启用该渠道。

**DingTalk 配置**

1. 在 [DingTalk Open Platform](https://open.dingtalk.com/) 创建应用，并启用 **机器人** 能力。
2. 在机器人设置页面将消息接收模式设为 **Stream**。
3. 复制 `Client ID` 和 `Client Secret`。在 `.env` 中设置 `DINGTALK_CLIENT_ID` 和 `DINGTALK_CLIENT_SECRET`，并在 `config.yaml` 中启用该渠道。
4. *（可选）* 如需启用流式 AI Card 回复（打字机效果），请在 [DingTalk 卡片平台](https://open.dingtalk.com/document/dingstart/typewriter-effect-streaming-ai-card) 创建 **AI Card** 模板，然后在 `config.yaml` 中将 `card_template_id` 设置为该模板 ID。同时还需要申请 `Card.Streaming.Write` 和 `Card.Instance.Write` 权限。

**可用命令**

| 命令 | 说明 |
|---------|----------|
| `/new` | 开始新对话 |
| `/status` | 显示当前 thread 信息 |
| `/models` | 可用模型列表 |
| `/memory` | 查看 memory |
| `/help` | 显示帮助 |

> 不带命令的消息会被当作普通聊天处理——DeerFlow 会创建 thread 并作出回复。

#### LangSmith 跟踪

DeerFlow 内置了与 [LangSmith](https://smith.langchain.com) 的集成，用于可观测性。启用后，所有 LLM 调用、agent 运行和工具执行都会被跟踪并显示在 LangSmith 仪表板中。

在项目根目录的 `.env` 文件中添加：

```bash
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxx
LANGSMITH_PROJECT=deer-flow
```

`LANGSMITH_ENDPOINT` 默认为 `https://api.smith.langchain.com`，如有需要可以覆盖。已弃用的 `LANGCHAIN_*` 变量（`LANGCHAIN_TRACING_V2`、`LANGCHAIN_API_KEY` 等）也为了向后兼容而继续支持；当两者都设置时，`LANGSMITH_*` 优先。

在 Docker 部署中，跟踪默认关闭。若要启用，请在 `.env` 中设置 `LANGSMITH_TRACING=true` 和 `LANGSMITH_API_KEY`。

## 从 Deep Research 到 Super Agent Harness

DeerFlow 最初是一个 Deep Research 框架，而社区后来把它带到了远超这一定位的地方。发布之后，开发者们用它来构建流水线、生成演示文稿、搭建仪表板、自动化内容生产。很多用途都超出了我们的预期。

我们逐渐意识到：DeerFlow 不只是一个 research 工具。它是一个 **harness**：一个为 agent 提供所需基础设施的 runtime。

因此，我们把一切都从头重写了。

DeerFlow 2.0 是一个开箱即用的 Super Agent Harness。Batteries included，并且完全可扩展。它基于 LangGraph 和 LangChain 构建，默认就具备 agent 所需的一切：文件系统、memory、skills、sandbox 执行，以及为复杂多步骤任务规划和启动 sub-agents 的能力。

可以直接拿来用。也可以拆开后按你的需求重新改造。

## 核心特性

### Skills & Tools

Skills 是 DeerFlow 几乎无所不能的关键。

Agent Skill 是一种结构化模块：一个描述工作流、最佳实践和资源链接的 Markdown 文件。DeerFlow 自带用于研究、报告生成、幻灯片制作、网页、图像和视频生成的内置 skills。但更重要的是扩展性：你可以添加自己的 skills、替换内置 skills，或者把它们组合成复合工作流。

Skills 会按需加载，只有任务真正需要时才会载入。这样可以保持上下文窗口整洁。

```
# Пути внутри контейнера sandbox
/mnt/skills/public
├── research/SKILL.md
├── report-generation/SKILL.md
├── slide-creation/SKILL.md
├── web-page/SKILL.md
└── image-generation/SKILL.md

/mnt/skills/custom
└── your-custom-skill/SKILL.md      ← ваш skill
```

#### 与 Claude Code 集成

`claude-to-deerflow` skill 让你可以直接在 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 中使用 DeerFlow。你可以在不离开终端的情况下发送任务、检查状态并管理 threads。

**安装 skill：**

```bash
npx skills add https://github.com/bytedance/deer-flow --skill claude-to-deerflow
```

**你可以做的事情：**
- 向 DeerFlow 发送消息并接收流式响应
- 选择执行模式：flash（快速）、standard、pro（planning）、ultra（sub-agents）
- 检查 DeerFlow 状态，查看模型、skills 和 agents
- 管理 threads 和对话历史
- 上传文件进行分析

完整 API 参考见 [`skills/public/claude-to-deerflow/SKILL.md`](skills/public/claude-to-deerflow/SKILL.md)。

### Sub-Agents

复杂任务很少能一次完成。DeerFlow 会先将其拆解。

Lead agent 会动态启动 sub-agents，每个都有自己隔离的上下文、工具和完成条件。Sub-agents 并行运行，返回结构化结果，最后由 lead agent 汇总成统一的最终输出。

这就是 DeerFlow 能处理耗时数分钟乃至数小时任务的方式：一个 research 任务会分叉成十几个 sub-agents，每个都深入自己负责的部分，最后汇合成一份报告、一个网站，或一套带生成视觉内容的幻灯片。一个 harness，多路并行。

### Sandbox 与文件系统

DeerFlow 不只是*说*自己能做事。它有一台属于自己的计算机。

每个任务都会在隔离的 Docker 容器中执行，并带有完整的文件系统：skills、workspace、uploads、outputs。agent 可以读取、写入和编辑文件；执行 bash 命令并编写代码；查看图像。一切都相互隔离、完全透明，不会在会话之间相互干扰。

这正是“能使用工具的聊天机器人”和“拥有真实执行环境的 agent”之间的差别。

```
# Пути внутри контейнера sandbox
/mnt/user-data/
├── uploads/          ← ваши файлы
├── workspace/        ← рабочая директория агентов
└── outputs/          ← результаты
```

### Context Engineering

**隔离上下文**：每个 sub-agent 都在自己的上下文中工作，看不到主 agent 或其他 sub-agents 的上下文。这样 agent 就能专注于自己的任务。

**上下文管理**：在单个会话内部，DeerFlow 会积极压缩上下文并总结已完成的子任务，把中间结果卸载到文件系统中，压缩已不再重要的内容。即使在长链路多步骤任务中，上下文窗口也不会轻易溢出。

### 长期记忆

大多数 agent 会在对话结束后忘记一切。DeerFlow 会记住。

DeerFlow 会在多个会话之间保留你的个人资料、偏好和积累的知识。你使用得越多，它就越了解你：你的风格、技术栈和重复出现的工作流。所有内容都保存在本地，并始终由你掌控。

## 推荐模型

DeerFlow 可通过 OpenAI 兼容 API 与任何 LLM 配合使用。最佳搭配通常是支持以下能力的模型：

- **大上下文窗口**（100k+ tokens）——适合 deep research 和多步骤任务
- **Reasoning capabilities** —— 适合自适应规划和复杂拆解
- **多模态输入** —— 适合处理图像和视频
- **强大的 tool-use** —— 适合可靠的函数调用和结构化响应

## 内置 Python 客户端

DeerFlow 可以直接作为 Python 库在代码中使用——无需启动 HTTP 服务。`DeerFlowClient` 提供对全部 agent 与 Gateway 能力的访问，并返回与 HTTP Gateway API 相同的响应 schema：

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

## 文档

- [参与指南](CONTRIBUTING.md) — 开发环境设置、工作流和指南
- [配置指南](backend/docs/CONFIGURATION.md) — 配置说明
- [架构概览](backend/CLAUDE.md) — 技术细节
- [后端架构](backend/README.md) — 后端与 API 参考

## ⚠️ 安全

### 不正确的部署可能导致安全风险

DeerFlow 具备关键的高权限能力，包括**执行系统命令、资源操作和业务逻辑调用**。默认情况下，它面向**本地可信环境部署（仅通过回环地址 127.0.0.1 访问）**。如果你在不可信环境中部署 agent——例如局域网、公网云服务器或其他可被多设备访问的环境——却没有采取严格的安全措施，可能会导致以下风险：

- **未授权调用**：agent 功能可能被未授权的第三方或恶意扫描器发现，从而触发大规模未授权请求，执行高风险操作（系统命令、文件读写），并带来严重安全后果。
- **法律与合规风险**：如果 agent 被非法用于网络攻击、数据窃取或其他违法行为，可能会带来法律责任和合规风险。

### 安全建议

**注意：我们强烈建议仅在本地可信网络中部署 DeerFlow。** 如果你确实需要跨设备或跨网络部署，务必实施严格的安全措施，例如：

- **IP 地址白名单**：使用 `iptables` 或硬件防火墙 / 带 ACL 的交换机等，**配置 IP 白名单规则**，阻止其他所有地址访问。
- **认证网关**：配置反向代理（nginx 等），并**启用严格的前置认证**，禁止任何未授权访问。
- **网络隔离**：如果可能，请将 agent 和可信设备放在**同一个专用 VLAN** 中，并与其他网络隔离。
- **关注更新**：定期跟踪 DeerFlow 项目的安全更新。

## 参与开发

欢迎贡献！开发环境设置、工作流和指南请见 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

本项目基于 [MIT 许可证](./LICENSE) 发布。

## 鸣谢

DeerFlow 站在开源社区的肩膀上。感谢所有让它成为可能的项目和开发者。

特别感谢：

- **[LangChain](https://github.com/langchain-ai/langchain)** — 用于与 LLM 交互和构建链式流程的框架。
- **[LangGraph](https://github.com/langchain-ai/langgraph)** — 支撑 DeerFlow 复杂工作流的多 agent 编排能力。

### 核心贡献者

没有这些作者，就不会有 DeerFlow：

- **[Daniel Walnut](https://github.com/hetaoBackend/)**
- **[Henry Li](https://github.com/magiccube/)**

## Star 历史

[![Star 历史图表](https://api.star-history.com/svg?repos=bytedance/deer-flow&type=Date)](https://star-history.com/#bytedance/deer-flow&Date)
