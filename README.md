# 🦌 DeerFlow - 2.0

英文 | [中文](./README_zh.md) | [日本語](./README_ja.md) | [Français](./README_fr.md) | [Русский](./README_ru.md)

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](./backend/pyproject.toml)
[![Node.js](https://img.shields.io/badge/Node.js-22%2B-339933?logo=node.js&logoColor=white)](./Makefile)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

<a href="https://trendshift.io/repositories/14699" target="_blank"><img src="https://trendshift.io/api/badge/repositories/14699" alt="bytedance%2Fdeer-flow | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>
> 2026 年 2 月 28 日，在发布 2.0 版本后，DeerFlow 登上了 GitHub Trending 🏆 第 1 名。万分感谢我们了不起的社区——这是大家共同促成的！💪🔥

DeerFlow（**D**eep **E**xploration and **E**fficient **R**esearch **Flow**）是一个开源的 **超级 Agent Harness**，通过可扩展的 **技能（skills）** 来编排 **子 Agent（sub-agents）**、**记忆（memory）** 和 **沙箱（sandboxes）**，几乎可以完成任何任务。

https://github.com/user-attachments/assets/a8bcadc4-e040-4cf2-8fda-dd768b999c18

> [!NOTE]
> **DeerFlow 2.0 是一次从零开始的重写。** 它与 v1 没有任何代码共享。如果你在寻找原始的 Deep Research 框架，它仍在 [`1.x` 分支](https://github.com/bytedance/deer-flow/tree/main-1.x) 上维护——我们依然欢迎对该分支的贡献。当前的活跃开发已转移到 2.0。

## 官方网站

[<img width="2880" height="1600" alt="image" src="https://github.com/user-attachments/assets/a598c49f-3b2f-41ea-a052-05e21349188a" />](https://deerflow.tech)

了解更多信息，并在我们的[**官方网站**](https://deerflow.tech)上查看**真实演示**。

## 字节跳动火山引擎 Coding Plan

<img width="4808" height="2400" alt="英文方舟" src="https://github.com/user-attachments/assets/2ecc7b9d-50be-4185-b1f7-5542d222fb2d" />

- 我们强烈推荐使用 Doubao-Seed-2.0-Code、DeepSeek v3.2 和 Kimi 2.5 来运行 DeerFlow
- [了解更多](https://www.byteplus.com/en/activity/codingplan?utm_campaign=deer_flow&utm_content=deer_flow&utm_medium=devrel&utm_source=OWO&utm_term=deer_flow)
- [中国大陆地区的开发者请点击这里](https://www.volcengine.com/activity/codingplan?utm_campaign=deer_flow&utm_content=deer_flow&utm_medium=devrel&utm_source=OWO&utm_term=deer_flow)

## InfoQuest

DeerFlow 已全新集成由 BytePlus 自主研发的智能搜索与抓取工具集——[InfoQuest（支持免费在线体验）](https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest)

<a href="https://docs.byteplus.com/en/docs/InfoQuest/What_is_Info_Quest" target="_blank">
  <img
    src="https://sf16-sg.tiktokcdn.com/obj/eden-sg/hubseh7bsbps/20251208-160108.png"   alt="InfoQuest_banner"
  />
</a>

---

## 目录

- [🦌 DeerFlow - 2.0](#-deerflow---20)
  - [官方网站](#官方网站)
  - [字节跳动火山引擎 Coding Plan](#字节跳动火山引擎-coding-plan)
  - [InfoQuest](#infoquest)
  - [目录](#目录)
  - [一句话 Agent 安装](#一句话-agent-安装)
  - [快速开始](#快速开始)
    - [配置](#配置)
    - [运行应用](#运行应用)
      - [部署规格建议](#部署规格建议)
      - [方案 1：Docker（推荐）](#方案-1docker推荐)
      - [方案 2：本地开发](#方案-2本地开发)
    - [高级用法](#高级用法)
      - [沙箱模式](#沙箱模式)
      - [MCP 服务器](#mcp-服务器)
      - [IM 渠道](#im-渠道)
      - [LangSmith 追踪](#langsmith-追踪)
      - [Langfuse 追踪](#langfuse-追踪)
      - [同时使用两个提供方](#同时使用两个提供方)
  - [从 Deep Research 到超级 Agent Harness](#从-deep-research-到超级-agent-harness)
  - [核心特性](#核心特性)
    - [技能与工具](#技能与工具)
      - [Claude Code 集成](#claude-code-集成)
    - [子 Agent](#子-agent)
    - [沙箱与文件系统](#沙箱与文件系统)
    - [上下文工程](#上下文工程)
    - [长期记忆](#长期记忆)
  - [推荐模型](#推荐模型)
  - [内嵌 Python 客户端](#内嵌-python-客户端)
  - [文档](#文档)
  - [⚠️ 安全提示](#️-安全提示)
    - [不当部署可能引入安全风险](#不当部署可能引入安全风险)
    - [安全建议](#安全建议)
  - [贡献](#贡献)
  - [许可证](#许可证)
  - [致谢](#致谢)
    - [核心贡献者](#核心贡献者)
  - [Star 历史](#star-历史)

## 一句话 Agent 安装

如果你使用 Claude Code、Codex、Cursor、Windsurf 或其他编码代理，你可以用一句话把安装说明交给它：

```text
Help me clone DeerFlow if needed, then bootstrap it for local development by following https://raw.githubusercontent.com/bytedance/deer-flow/main/Install.md
```

这段提示词是为编码代理准备的。它会告诉代理在需要时克隆仓库、优先选择 Docker，并在结束时给出确切的下一条命令，以及用户仍需提供的缺失配置。

## 快速开始

### 配置

1. **克隆 DeerFlow 仓库**

   ```bash
   git clone https://github.com/bytedance/deer-flow.git
   cd deer-flow
   ```

2. **运行安装向导**

   在项目根目录（`deer-flow/`）下运行：

   ```bash
   make setup
   ```

   这会启动一个交互式向导，引导你选择 LLM 提供方、可选的网页搜索，以及诸如沙箱模式、bash 访问和文件写入工具等执行/安全偏好。它会生成一个最小化的 `config.yaml`，并将你的密钥写入 `.env`。整个过程大约需要 2 分钟。

   该向导也允许你配置一个可选的网页搜索提供方，或者暂时跳过。

   你可以随时运行 `make doctor` 来验证安装状态并获取可执行的修复提示。

   > **高级 / 手动配置**：如果你更喜欢直接编辑 `config.yaml`，请改为运行 `make config` 来复制完整模板。完整参考请查看 `config.example.yaml`，其中包含基于 CLI 的提供方（Codex CLI、Claude Code OAuth）、OpenRouter、Responses API 等配置。

   <details>
   <summary>手动模型配置示例</summary>

   ```yaml
   models:
     - name: gpt-4o
       display_name: GPT-4o
       use: langchain_openai:ChatOpenAI
       model: gpt-4o
       api_key: $OPENAI_API_KEY

     - name: openrouter-gemini-2.5-flash
       display_name: Gemini 2.5 Flash (OpenRouter)
       use: langchain_openai:ChatOpenAI
       model: google/gemini-2.5-flash-preview
       api_key: $OPENROUTER_API_KEY
       base_url: https://openrouter.ai/api/v1

     - name: gpt-5-responses
       display_name: GPT-5 (Responses API)
       use: langchain_openai:ChatOpenAI
       model: gpt-5
       api_key: $OPENAI_API_KEY
       use_responses_api: true
       output_version: responses/v1

     - name: qwen3-32b-vllm
       display_name: Qwen3 32B (vLLM)
       use: deerflow.models.vllm_provider:VllmChatModel
       model: Qwen/Qwen3-32B
       api_key: $VLLM_API_KEY
       base_url: http://localhost:8000/v1
       supports_thinking: true
       when_thinking_enabled:
         extra_body:
           chat_template_kwargs:
             enable_thinking: true
   ```

   OpenRouter 和类似的 OpenAI 兼容网关应使用 `langchain_openai:ChatOpenAI` 并配合 `base_url` 进行配置。如果你更喜欢使用提供方专属的环境变量名，请将 `api_key` 显式指向该变量（例如 `api_key: $OPENROUTER_API_KEY`）。

   如果要将 OpenAI 模型通过 `/v1/responses` 路由，请继续使用 `langchain_openai:ChatOpenAI`，并设置 `use_responses_api: true` 以及 `output_version: responses/v1`。

   对于 vLLM 0.19.0，请使用 `deerflow.models.vllm_provider:VllmChatModel`。对于 Qwen 风格的推理模型，DeerFlow 会通过 `extra_body.chat_template_kwargs.enable_thinking` 来切换推理模式，并在多轮工具调用对话中保留 vLLM 非标准的 `reasoning` 字段。旧版 `thinking` 配置会被自动规范化，以保持向后兼容。推理模型还可能要求服务端通过 `--reasoning-parser ...` 启动。如果你的本地 vLLM 部署接受任意非空 API key，你依然可以将 `VLLM_API_KEY` 设置为占位值。

   基于 CLI 的提供方示例：

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
   - Claude Code 接受 `CLAUDE_CODE_OAUTH_TOKEN`、`ANTHROPIC_AUTH_TOKEN`、`CLAUDE_CODE_CREDENTIALS_PATH` 或 `~/.claude/.credentials.json`
   - ACP agent 条目与模型提供方是分开的——如果你配置 `acp_agents.codex`，请将其指向类似 `npx -y @zed-industries/codex-acp` 的 Codex ACP 适配器
   - 在 macOS 上，如有需要，请显式导出 Claude Code 认证信息：

   ```bash
   eval "$(python3 scripts/export_claude_code_oauth.py --print-export)"
   ```

   API key 也可以手动设置到 `.env`（推荐）中，或在 shell 中导出：

   ```bash
   OPENAI_API_KEY=your-openai-api-key
   TAVILY_API_KEY=your-tavily-api-key
   ```

   </details>

### 运行应用

#### 部署规格建议

在选择如何运行 DeerFlow 时，可将下表作为实用起点：

| 部署目标 | 起始配置 | 推荐配置 | 说明 |
|---------|-----------|------------|-------|
| 本地评估 / `make dev` | 4 vCPU、8 GB RAM、20 GB 可用 SSD | 8 vCPU、16 GB RAM | 适合单个开发者，或使用托管模型 API 的单个轻量会话。`2 vCPU / 4 GB` 通常不够。 |
| Docker 开发 / `make docker-start` | 4 vCPU、8 GB RAM、25 GB 可用 SSD | 8 vCPU、16 GB RAM | 镜像构建、绑定挂载和沙箱容器比纯本地开发更需要资源余量。 |
| 长时间运行的服务器 / `make up` | 8 vCPU、16 GB RAM、40 GB 可用 SSD | 16 vCPU、32 GB RAM | 更适合共享使用、多 Agent 运行、报告生成或更重的沙箱工作负载。 |

- 这些数值仅覆盖 DeerFlow 本身。如果你还要托管本地 LLM，请单独为该服务评估资源。
- 对于持久化服务器，推荐的部署目标是 Linux + Docker。macOS 和 Windows 更适合作为开发或评估环境。
- 如果 CPU 或内存使用持续打满，请先减少并发运行数量，再升级到更高的规格档位。

#### 方案 1：Docker（推荐）

**开发环境**（热重载、源码挂载）：

```bash
make docker-init    # Pull sandbox image (only once or when image updates)
make docker-start   # Start services (auto-detects sandbox mode from config.yaml)
```

`make docker-start` 仅在 `config.yaml` 使用 provisioner 模式（`sandbox.use: deerflow.community.aio_sandbox:AioSandboxProvider` 且配置了 `provisioner_url`）时启动 `provisioner`。

Docker 构建默认使用上游 `uv` registry。如果你在受限网络中需要更快的镜像源，请在运行 `make docker-init` 或 `make docker-start` 之前导出 `UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple` 和 `NPM_REGISTRY=https://registry.npmmirror.com`。

后端进程会在下一次访问配置时自动读取 `config.yaml` 的变更，因此在开发过程中更新模型元数据无需手动重启。

> [!TIP]
> 在 Linux 上，如果基于 Docker 的命令因 `permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock` 失败，请将你的用户加入 `docker` 用户组，并重新登录后再试。完整修复方式请参见 [CONTRIBUTING.md](CONTRIBUTING.md#linux-docker-daemon-permission-denied)。

**生产环境**（本地构建镜像，挂载运行时配置和数据）：

```bash
make up     # Build images and start all production services
make down   # Stop and remove containers
```

访问地址：http://localhost:2026

统一的 nginx 端点默认采用同源方式，不会输出浏览器 CORS 头。如果你运行的是分离源或端口转发的浏览器客户端，请将 `GATEWAY_CORS_ORIGINS` 设置为以逗号分隔的精确来源，例如 `http://localhost:3000`；这样 Gateway 就会应用 CORS 允许列表以及匹配的 CSRF 来源校验。

详细的 Docker 开发指南请参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

#### 方案 2：本地开发

如果你更喜欢在本地运行服务：

前置条件：先完成上面的“配置”步骤（`make setup`）。`make dev` 要求项目根目录下存在有效的 `config.yaml`。设置 `DEER_FLOW_PROJECT_ROOT` 可以显式定义该根目录，设置 `DEER_FLOW_CONFIG_PATH` 可以指向特定的配置文件。运行时状态默认位于项目根目录下的 `.deer-flow`，可通过 `DEER_FLOW_HOME` 修改；技能目录默认位于项目根目录下的 `skills/`，可通过 `DEER_FLOW_SKILLS_PATH` 修改。启动前请运行 `make doctor` 验证安装状态。
在 Windows 上，请通过 Git Bash 运行本地开发流程。原生 `cmd.exe` 和 PowerShell 不支持这些基于 bash 的服务脚本，而 WSL 也无法保证可用，因为某些脚本依赖 Git for Windows 提供的 `cygpath` 等工具。

1. **检查前置条件**：
   ```bash
   make check  # Verifies Node.js 22+, pnpm, uv, nginx
   ```

2. **安装依赖**：
   ```bash
   make install  # Install backend + frontend dependencies + pre-commit hooks
   ```

3. **（可选）预先拉取沙箱镜像**：
   ```bash
   # Recommended if using Docker/Container-based sandbox
   make setup-sandbox
   ```

4. **（可选）为本地评审加载示例记忆数据**：
   ```bash
   python scripts/load_memory_sample.py
   ```
   这会把示例夹具复制到默认的本地运行时记忆文件中，使评审者可以立即测试 `Settings > Memory`。
   最简评审流程请参见 [backend/docs/MEMORY_SETTINGS_REVIEW.md](backend/docs/MEMORY_SETTINGS_REVIEW.md)。

5. **启动服务**：
   ```bash
   make dev
   ```

6. **访问地址**：http://localhost:2026

#### 启动模式

DeerFlow 在 Gateway API 内部运行 Agent 运行时。开发模式启用热重载；生产模式使用预构建的前端。

| | **本地前台** | **本地守护进程** | **Docker 开发** | **Docker 生产** |
|---|---|---|---|---|
| **开发** | `./scripts/serve.sh --dev`<br/>`make dev` | `./scripts/serve.sh --dev --daemon`<br/>`make dev-daemon` | `./scripts/docker.sh start`<br/>`make docker-start` | — |
| **生产** | `./scripts/serve.sh --prod`<br/>`make start` | `./scripts/serve.sh --prod --daemon`<br/>`make start-daemon` | — | `./scripts/deploy.sh`<br/>`make up` |

| 操作 | 本地 | Docker 开发 | Docker 生产 |
|---|---|---|---|
| **停止** | `./scripts/serve.sh --stop`<br/>`make stop` | `./scripts/docker.sh stop`<br/>`make docker-stop` | `./scripts/deploy.sh down`<br/>`make down` |
| **重启** | `./scripts/serve.sh --restart [flags]` | `./scripts/docker.sh restart` | — |

Gateway 负责 `/api/langgraph/*`，并在 nginx 后面将这些公开的 LangGraph 兼容路径转换为它原生的 `/api/*` 路由。

#### Docker 生产部署

`deploy.sh` 支持分开执行构建与启动：

```bash
# One-step (build + start)
deploy.sh

# Two-step (build once, start later)
deploy.sh build              # build all images
deploy.sh start              # start pre-built images

# Stop
deploy.sh down
```

### 高级用法
#### 沙箱模式

DeerFlow 支持多种沙箱执行模式：
- **本地执行**（直接在宿主机上运行沙箱代码）
- **Docker 执行**（在隔离的 Docker 容器中运行沙箱代码）
- **带 Kubernetes 的 Docker 执行**（通过 provisioner 服务在 Kubernetes pod 中运行沙箱代码）

对于 Docker 开发，服务启动会遵循 `config.yaml` 中的沙箱模式。在本地 / Docker 模式下，不会启动 `provisioner`。

请参见 [沙箱配置指南](backend/docs/CONFIGURATION.md#sandbox) 来配置你偏好的模式。

#### MCP 服务器

DeerFlow 支持可配置的 MCP 服务器和技能，以扩展其能力。
对于 HTTP/SSE MCP 服务器，支持 OAuth token 流程（`client_credentials`、`refresh_token`）。
详细说明请参见 [MCP 服务器指南](backend/docs/MCP_SERVER.md)。

#### IM 渠道

DeerFlow 支持从即时通讯应用接收任务。只要完成配置，这些渠道就会自动启动——其中任何一种都不要求公网 IP。

| 渠道 | 传输方式 | 难度 |
|---------|-----------|------------|
| Telegram | Bot API（长轮询） | 简单 |
| Slack | Socket Mode | 中等 |
| Feishu / Lark | WebSocket | 中等 |
| WeChat | Tencent iLink（长轮询） | 中等 |
| WeCom | WebSocket | 中等 |
| DingTalk | Stream Push（WebSocket） | 中等 |

**`config.yaml` 中的配置：**

```yaml
channels:
  # LangGraph-compatible Gateway API base URL (default: http://localhost:8001/api)
  langgraph_url: http://localhost:8001/api
  # Gateway API URL (default: http://localhost:8001)
  gateway_url: http://localhost:8001

  # Optional: global session defaults for all mobile channels
  session:
    assistant_id: lead_agent  # or a custom agent name; custom agents are routed via lead_agent + agent_name
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

  wecom:
    enabled: true
    bot_id: $WECOM_BOT_ID
    bot_secret: $WECOM_BOT_SECRET

  slack:
    enabled: true
    bot_token: $SLACK_BOT_TOKEN     # xoxb-...
    app_token: $SLACK_APP_TOKEN     # xapp-... (Socket Mode)
    allowed_users: []               # empty = allow all

  telegram:
    enabled: true
    bot_token: $TELEGRAM_BOT_TOKEN
    allowed_users: []               # empty = allow all

  wechat:
    enabled: false
    bot_token: $WECHAT_BOT_TOKEN
    ilink_bot_id: $WECHAT_ILINK_BOT_ID
    qrcode_login_enabled: true      # optional: allow first-time QR bootstrap when bot_token is absent
    allowed_users: []               # empty = allow all
    polling_timeout: 35
    state_dir: ./.deer-flow/wechat/state
    max_inbound_image_bytes: 20971520
    max_outbound_image_bytes: 20971520
    max_inbound_file_bytes: 52428800
    max_outbound_file_bytes: 52428800

    # Optional: per-channel / per-user session settings
    session:
      assistant_id: mobile-agent  # custom agent names are also supported here
      context:
        thinking_enabled: false
      users:
        "123456789":
          assistant_id: vip-agent
          config:
            recursion_limit: 150
          context:
            thinking_enabled: true
            subagent_enabled: true

  dingtalk:
    enabled: true
    client_id: $DINGTALK_CLIENT_ID             # Client ID of your DingTalk application
    client_secret: $DINGTALK_CLIENT_SECRET     # Client Secret of your DingTalk application
    allowed_users: []                          # empty = allow all
    card_template_id: ""                       # Optional: AI Card template ID for streaming typewriter effect
```

说明：
- `assistant_id: lead_agent` 会直接调用默认的 LangGraph assistant。
- 如果 `assistant_id` 被设置为自定义 agent 名称，DeerFlow 仍会通过 `lead_agent` 进行路由，并将该值注入为 `agent_name`，从而让该自定义 agent 的 SOUL/config 在 IM 渠道中生效。
- IM 渠道工作进程会在内部调用 Gateway 的 LangGraph 兼容 API，并自动附加进程内的内部认证信息，以及创建 thread 和 run 所需的 CSRF cookie/header 组合。

在你的 `.env` 文件中设置相应的 API key：

```bash
# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ

# Slack
SLACK_BOT_TOKEN=xoxb-...
SLACK_APP_TOKEN=xapp-...

# Feishu / Lark
FEISHU_APP_ID=cli_xxxx
FEISHU_APP_SECRET=your_app_secret

# WeChat iLink
WECHAT_BOT_TOKEN=your_ilink_bot_token
WECHAT_ILINK_BOT_ID=your_ilink_bot_id

# WeCom
WECOM_BOT_ID=your_bot_id
WECOM_BOT_SECRET=your_bot_secret

# DingTalk
DINGTALK_CLIENT_ID=your_client_id
DINGTALK_CLIENT_SECRET=your_client_secret
```

**Telegram 配置**

1. 与 [@BotFather](https://t.me/BotFather) 对话，发送 `/newbot`，并复制 HTTP API token。
2. 在 `.env` 中设置 `TELEGRAM_BOT_TOKEN`，并在 `config.yaml` 中启用该渠道。

**Slack 配置**

1. 在 [api.slack.com/apps](https://api.slack.com/apps) 创建 Slack App → Create New App → From scratch。
2. 在 **OAuth & Permissions** 下添加 Bot Token Scopes：`app_mentions:read`、`chat:write`、`im:history`、`im:read`、`im:write`、`files:write`。
3. 启用 **Socket Mode** → 生成一个带 `connections:write` scope 的 App-Level Token（`xapp-…`）。
4. 在 **Event Subscriptions** 下订阅 bot 事件：`app_mention`、`message.im`。
5. 在 `.env` 中设置 `SLACK_BOT_TOKEN` 和 `SLACK_APP_TOKEN`，并在 `config.yaml` 中启用该渠道。

**Feishu / Lark 配置**

1. 在 [Feishu Open Platform](https://open.feishu.cn/) 创建应用 → 启用 **Bot** 能力。
2. 添加权限：`im:message`、`im:message.p2p_msg:readonly`、`im:resource`。
3. 在 **Events** 下订阅 `im.message.receive_v1`，并选择 **Long Connection** 模式。
4. 复制 App ID 和 App Secret。在 `.env` 中设置 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`，并在 `config.yaml` 中启用该渠道。

**WeChat 配置**

1. 在 `config.yaml` 中启用 `wechat` 渠道。
2. 要么在 `.env` 中设置 `WECHAT_BOT_TOKEN`，要么设置 `qrcode_login_enabled: true` 以启用首次二维码引导。
3. 当未提供 `bot_token` 且启用了二维码引导时，请查看后端日志中 iLink 返回的二维码内容，并完成绑定流程。
4. 二维码流程成功后，DeerFlow 会将获取到的 token 持久化到 `state_dir` 中，供后续重启使用。
5. 对于 Docker Compose 部署，请将 `state_dir` 放在持久化卷上，以便 `get_updates_buf` 游标和保存的认证状态在重启后仍然保留。

**WeCom 配置**

1. 在 WeCom AI Bot 平台创建一个机器人，并获取 `bot_id` 和 `bot_secret`。
2. 在 `config.yaml` 中启用 `channels.wecom`，并填写 `bot_id` / `bot_secret`。
3. 在 `.env` 中设置 `WECOM_BOT_ID` 和 `WECOM_BOT_SECRET`。
4. 确保后端依赖包含 `wecom-aibot-python-sdk`。该渠道使用 WebSocket 长连接，不需要公网回调 URL。
5. 当前集成支持接收文本、图片和文件消息。Agent 最终生成的图片/文件也会回传到 WeCom 会话中。

**DingTalk 配置**

1. 在 [DingTalk Developer Console](https://open.dingtalk.com/) 中创建一个 DingTalk 应用，并启用 **Robot** 能力。
2. 在机器人配置页面将消息接收模式设置为 **Stream Mode**。
3. 复制 `Client ID` 和 `Client Secret`，在 `.env` 中设置 `DINGTALK_CLIENT_ID` 和 `DINGTALK_CLIENT_SECRET`，并在 `config.yaml` 中启用该渠道。
4. *（可选）* 若要启用流式 AI Card 回复（打字机效果），请在 [DingTalk Card Platform](https://open.dingtalk.com/document/dingstart/typewriter-effect-streaming-ai-card) 创建一个 **AI Card** 模板，然后在 `config.yaml` 中将 `card_template_id` 设置为该模板 ID。你还需要申请 `Card.Streaming.Write` 和 `Card.Instance.Write` 权限。


当 DeerFlow 在 Docker Compose 中运行时，IM 渠道会在 `gateway` 容器内执行。在这种情况下，不要将 `channels.langgraph_url` 或 `channels.gateway_url` 指向 `localhost`；请使用诸如 `http://gateway:8001/api` 和 `http://gateway:8001` 这样的容器服务名，或设置 `DEER_FLOW_CHANNELS_LANGGRAPH_URL` 和 `DEER_FLOW_CHANNELS_GATEWAY_URL`。

**命令**

当某个渠道连接成功后，你可以直接在聊天中与 DeerFlow 交互：

| 命令 | 说明 |
|---------|-------------|
| `/new` | 开始新的对话 |
| `/status` | 显示当前 thread 信息 |
| `/models` | 列出可用模型 |
| `/memory` | 查看记忆 |
| `/help` | 显示帮助 |

> 没有命令前缀的消息会被视为普通聊天——DeerFlow 会创建一个 thread 并以对话方式回复。

#### LangSmith 追踪

DeerFlow 内置了 [LangSmith](https://smith.langchain.com) 可观测性集成。启用后，所有 LLM 调用、Agent 运行和工具执行都会被追踪，并可在 LangSmith 仪表板中查看。

将以下内容添加到你的 `.env` 文件中：

```bash
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxx
LANGSMITH_PROJECT=xxx
```

#### Langfuse 追踪

DeerFlow 也支持 [Langfuse](https://langfuse.com) 对 LangChain 兼容运行的可观测性。

将以下内容添加到你的 `.env` 文件中：

```bash
LANGFUSE_TRACING=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

如果你使用的是自托管 Langfuse 实例，请将 `LANGFUSE_BASE_URL` 设置为你的部署 URL。

**追踪关联字段。** 每次 Agent 运行都会附带 Langfuse 保留的 trace 属性，因此 Sessions 和 Users 页面会自动显示相关信息：

- `session_id` = LangGraph `thread_id` —— 将同一会话的所有 trace 归为一组
- `user_id` = `get_effective_user_id()` 返回的有效用户（在无认证模式下回退为 `default`）
- `trace_name` = assistant id（默认为 `lead-agent`）
- `tags` = `[env:<DEER_FLOW_ENV>, model:<model_name>]`（未设置时省略）

这些字段会在图调用根部被注入到 `RunnableConfig.metadata` 中，覆盖 Gateway 路径（`runtime/runs/worker.py::run_agent`）和内嵌路径（`client.py::DeerFlowClient.stream`），因此任何与 LangChain 兼容的 callback 都可以读取它们。设置 `DEER_FLOW_ENV`（或 `ENVIRONMENT`）即可按部署环境为 trace 打标签。

#### 同时使用两个提供方

如果同时启用了 LangSmith 和 Langfuse，DeerFlow 会附加两个 tracing callback，并将相同的模型活动上报到两个系统。

如果某个提供方被显式启用但缺少必需凭证，或者其 callback 初始化失败，那么 DeerFlow 会在模型创建期间初始化 tracing 时快速失败，并在错误消息中指出导致失败的提供方。

对于 Docker 部署，默认禁用 tracing。如需启用，请在 `.env` 中设置 `LANGSMITH_TRACING=true` 和 `LANGSMITH_API_KEY`。

## 从 Deep Research 到超级 Agent Harness

DeerFlow 最初是一个 Deep Research 框架——而社区把它带到了更远的地方。自发布以来，开发者们将它远远拓展出了“研究”范畴：构建数据流水线、生成幻灯片、搭建仪表盘、自动化内容工作流。这些都是我们当初未曾预料到的。

这让我们意识到一件重要的事：DeerFlow 不仅仅是一个研究工具。它是一个 **harness**——一个为 Agent 提供基础设施、让它们真正把工作做完的运行时。

所以我们从头重建了它。

DeerFlow 2.0 不再是一个需要你自己拼装的框架。它是一个超级 Agent Harness——开箱即用，同时具备完整可扩展性。它构建于 LangGraph 和 LangChain 之上，开箱提供 Agent 所需的一切：文件系统、记忆、技能、具备沙箱感知的执行能力，以及为复杂多步骤任务进行规划并生成子 Agent 的能力。

你可以直接使用它。也可以把它拆开，改造成属于你自己的系统。

## 核心特性

### 技能与工具

技能是 DeerFlow 几乎能做任何事的关键。

标准的 Agent Skill 是一种结构化能力模块——通常是一个 Markdown 文件，用来定义工作流、最佳实践以及对支持资源的引用。DeerFlow 内置了用于研究、报告生成、幻灯片创建、网页制作、图片和视频生成等能力的技能。但真正的力量来自可扩展性：你可以添加自己的技能、替换内置技能，或者将它们组合成复合工作流。

技能采用渐进式加载——只有任务需要时才会载入，而不是一次性全部加载。这让上下文窗口保持精简，也使 DeerFlow 即便在 token 敏感的模型上依然运行良好。

当你通过 Gateway 安装 `.skill` 归档时，DeerFlow 会接受标准的可选 frontmatter 元数据（例如 `version`、`author` 和 `compatibility`），而不会拒绝本来有效的外部技能。

工具遵循相同的理念。DeerFlow 自带一套核心工具集——网页搜索、网页抓取、文件操作、bash 执行——并通过 MCP 服务器和 Python 函数支持自定义工具。任何东西都可以替换，任何东西都可以扩展。

Gateway 生成的后续建议现在会在解析 JSON 数组响应前，统一规范普通字符串模型输出和 block/list 风格的富内容，从而避免因提供方特定的内容包装器而悄悄丢失建议。

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

`claude-to-deerflow` 技能让你可以直接在 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 中与正在运行的 DeerFlow 实例交互。发送研究任务、查看状态、管理 threads——全程无需离开终端。

**安装该技能**：

```bash
npx skills add https://github.com/bytedance/deer-flow --skill claude-to-deerflow
```

然后确保 DeerFlow 正在运行（默认地址为 `http://localhost:2026`），并在 Claude Code 中使用 `/claude-to-deerflow` 命令。

**你可以做什么**：
- 向 DeerFlow 发送消息并获取流式响应
- 选择执行模式：flash（快速）、standard、pro（规划）、ultra（子 Agent）
- 检查 DeerFlow 健康状态，列出模型/技能/agents
- 管理 threads 和对话历史
- 上传文件进行分析

**环境变量**（可选，用于自定义端点）：

```bash
DEERFLOW_URL=http://localhost:2026            # Unified proxy base URL
DEERFLOW_GATEWAY_URL=http://localhost:2026    # Gateway API
DEERFLOW_LANGGRAPH_URL=http://localhost:2026/api/langgraph  # LangGraph API
```

完整 API 参考请参见 [`skills/public/claude-to-deerflow/SKILL.md`](skills/public/claude-to-deerflow/SKILL.md)。

### 子 Agent

复杂任务很少能一次完成。DeerFlow 会对其进行拆解。

主 Agent 可以动态生成子 Agent——每个子 Agent 都拥有自己的作用域上下文、工具和终止条件。子 Agent 会在可能的情况下并行运行，返回结构化结果，而主 Agent 会将所有内容综合成连贯的输出。当启用 token 使用量追踪时，已完成子 Agent 的使用量会回溯记到发起调度的步骤上。

这就是 DeerFlow 处理耗时从几分钟到几小时任务的方式：一个研究任务可能会分裂成十几个子 Agent，各自探索不同方向，然后汇聚成一份报告——或者一个网站——或者一套带生成式视觉内容的幻灯片。一个 harness，多双手协作。

### 沙箱与文件系统

DeerFlow 不只是“说”自己能做事。它有属于自己的计算机。

每个任务都会获得独立的执行环境，并拥有完整的文件系统视图——技能、工作区、上传内容、输出结果一应俱全。Agent 可以读取、写入和编辑文件；它可以查看图像，并且在安全配置下还能执行 shell 命令。

使用 `AioSandboxProvider` 时，shell 执行会在隔离容器内运行。使用 `LocalSandboxProvider` 时，文件工具仍会映射到宿主机上按 thread 划分的目录，但默认禁用宿主机 `bash`，因为它并不是安全的隔离边界。只有在完全可信的本地工作流中才应重新启用宿主机 bash。

这正是“具备工具访问权限的聊天机器人”和“拥有真实执行环境的 Agent”之间的区别。

```
# Paths inside the sandbox container
/mnt/user-data/
├── uploads/          ← your files
├── workspace/        ← agents' working directory
└── outputs/          ← final deliverables
```

### 上下文工程

**隔离的子 Agent 上下文**：每个子 Agent 都在自己隔离的上下文中运行。这意味着子 Agent 无法看到主 Agent 或其他子 Agent 的上下文。这一点很重要，因为它能确保子 Agent 专注于当前任务，而不会被主 Agent 或其他子 Agent 的上下文分散注意力。

**摘要化**：在单个会话中，DeerFlow 会积极管理上下文——总结已完成的子任务、将中间结果卸载到文件系统中、压缩那些不再需要立即关注的信息。这样它就能在长时间、多步骤任务中保持敏锐，而不会耗尽上下文窗口。

**严格的工具调用恢复**：当提供方或中间件中断工具调用循环时，DeerFlow 现在会在强制停止的 assistant 消息上剥离提供方级别的原始工具调用元数据，并在下一次模型调用前为悬空的调用注入占位工具结果。这可以防止严格校验 `tool_call_id` 序列的 OpenAI 兼容推理模型因为历史记录格式错误而失败。

### 长期记忆

大多数 Agent 在对话结束后就会忘记一切。而 DeerFlow 会记住。

跨会话地，DeerFlow 会持续构建关于你的个人画像、偏好和累积知识的持久记忆。你使用得越多，它就越了解你——你的写作风格、技术栈、重复出现的工作流。记忆存储在本地，并始终由你掌控。

记忆更新现在会在应用阶段跳过重复的事实条目，因此重复的偏好和上下文不会在跨会话过程中无限累积。

## 推荐模型

DeerFlow 与模型无关——任何实现了 OpenAI 兼容 API 的 LLM 都可以使用。不过，它在支持以下能力的模型上表现最佳：

- **长上下文窗口**（100k+ tokens），适合深度研究和多步骤任务
- **推理能力**，适合自适应规划和复杂拆解
- **多模态输入**，适合图像理解和视频理解
- **强工具使用能力**，适合可靠的函数调用和结构化输出

## 内嵌 Python 客户端

DeerFlow 可以作为内嵌 Python 库使用，而无需运行完整的 HTTP 服务。`DeerFlowClient` 提供对所有 Agent 与 Gateway 能力的进程内直接访问，并返回与 HTTP Gateway API 相同的响应 schema。HTTP Gateway 还暴露了 `DELETE /api/threads/{thread_id}` 用于在 LangGraph thread 本身已删除后，移除 DeerFlow 管理的本地 thread 数据：

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

所有返回 dict 的方法都会在 CI 中根据 Gateway 的 Pydantic 响应模型进行校验（`TestGatewayConformance`），以确保内嵌客户端始终与 HTTP API schema 保持同步。完整 API 文档请参见 `backend/packages/harness/deerflow/client.py`。

## 文档

- [贡献指南](CONTRIBUTING.md) - 开发环境搭建与工作流
- [配置指南](backend/docs/CONFIGURATION.md) - 安装与配置说明
- [架构概览](backend/CLAUDE.md) - 技术架构细节
- [后端架构](backend/README.md) - 后端架构与 API 参考

## ⚠️ 安全提示

### 不当部署可能引入安全风险

DeerFlow 拥有若干高权限能力，包括**系统命令执行、资源操作以及业务逻辑调用**，并且默认设计为**部署在本地可信环境中（仅通过 127.0.0.1 回环接口访问）**。如果你在不受信任的环境中部署该 Agent——例如局域网、公有云服务器，或其他可被多个端点访问的环境——却没有采取严格的安全措施，可能会引入以下安全风险：

- **未经授权的非法调用**：Agent 功能可能被未授权的第三方或恶意互联网扫描器发现，从而触发大规模未授权请求，执行系统命令、文件读写等高风险操作，并可能造成严重安全后果。
- **合规与法律风险**：如果 Agent 被非法调用以实施网络攻击、窃取数据或其他非法活动，可能导致法律责任和合规风险。

### 安全建议

**注意：我们强烈建议将 DeerFlow 部署在本地可信网络环境中。** 如果你需要跨设备或跨网络部署，就必须实施严格的安全措施，例如：

- **IP 白名单**：使用 `iptables`，或部署带访问控制列表（ACL）的硬件防火墙 / 交换机，来**配置 IP 白名单规则**并拒绝所有其他 IP 地址访问。
- **认证网关**：配置反向代理（如 nginx），并**启用强预认证**，阻止任何未认证访问。
- **网络隔离**：在可能的情况下，将 Agent 和受信任设备放置在**同一个专用 VLAN** 中，并与其他网络设备隔离。
- **保持更新**：持续关注 DeerFlow 安全特性的更新。

## 贡献

欢迎贡献！开发环境搭建、工作流与规范请参见 [CONTRIBUTING.md](CONTRIBUTING.md)。

回归测试覆盖了 `backend/tests/` 中关于 Docker 沙箱模式检测以及 provisioner kubeconfig 路径处理的测试。
Gateway 的制品服务现在会强制将活动网页内容类型（`text/html`、`application/xhtml+xml`、`image/svg+xml`）作为附件下载，而不是内联渲染，从而降低生成制品的 XSS 风险。

## 许可证

本项目为开源项目，并依据 [MIT 许可证](./LICENSE) 发布。

## 致谢

DeerFlow 建立在开源社区的卓越成果之上。对于所有让 DeerFlow 成为可能的项目与贡献者，我们都怀有深深的感激。毫无疑问，我们是站在巨人的肩膀上前行。

我们谨向以下项目致以诚挚感谢，感谢它们所做出的宝贵贡献：

- **[LangChain](https://github.com/langchain-ai/langchain)**：其卓越的框架为我们的 LLM 交互与链式调用提供动力，实现了无缝集成与功能支持。
- **[LangGraph](https://github.com/langchain-ai/langgraph)**：其创新的多 Agent 编排方式，对于实现 DeerFlow 的复杂工作流起到了关键作用。

这些项目展现了开源协作的变革性力量，我们很自豪能够构建在它们的基础之上。

### 核心贡献者

衷心感谢 `DeerFlow` 的核心作者们，正是他们的愿景、热情与投入让这个项目得以落地：

- **[Daniel Walnut](https://github.com/hetaoBackend/)**
- **[Henry Li](https://github.com/magiccube/)**

你们坚定不移的投入和专业能力，是 DeerFlow 成功背后的核心驱动力。能够与你们一同踏上这段旅程，我们深感荣幸。

## Star 历史

[![Star 历史图表](https://api.star-history.com/svg?repos=bytedance/deer-flow&type=Date)](https://star-history.com/#bytedance/deer-flow&Date)
