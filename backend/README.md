# DeerFlow Backend

DeerFlow 是一个基于 LangGraph 的 AI super agent，具备 sandbox 执行、持久化 memory 以及可扩展的工具集成。后端使 AI agent 能够执行代码、浏览网页、管理文件、将任务委派给 subagent，并在对话间保留上下文——所有这些都运行在隔离的、按线程划分的环境中。

---

## 架构

```
                        ┌──────────────────────────────────────┐
                        │          Nginx (Port 2026)           │
                        │      Unified reverse proxy           │
                        └───────┬──────────────────┬───────────┘
                                │
            /api/langgraph/*    │    /api/* (other)
            rewritten to /api/* │
                                ▼
               ┌────────────────────────────────────────┐
               │        Gateway API (8001)              │
               │        FastAPI REST + agent runtime    │
               │                                        │
               │ Models, MCP, Skills, Memory, Uploads,  │
               │ Artifacts, Threads, Runs, Streaming    │
               │                                        │
               │ ┌────────────────────────────────────┐ │
               │ │ Lead Agent                         │ │
               │ │ Middleware Chain, Tools, Subagents │ │
               │ └────────────────────────────────────┘ │
               └────────────────────────────────────────┘
```

**请求路由**（通过 Nginx）：
- `/api/langgraph/*` → Gateway 兼容 LangGraph 的 API —— agent 交互、线程、流式传输
- `/api/*`（其他）→ Gateway API —— models、MCP、skills、memory、artifacts、uploads、线程本地清理
- `/`（非 API）→ Frontend —— Next.js Web 界面

---

## 核心组件

### Lead Agent

单个 LangGraph agent（`lead_agent`）是运行时入口，通过 `make_lead_agent(config)` 创建。它组合了：

- 具备 thinking 和 vision 支持的**动态模型选择**
- 用于处理横切关注点的 **Middleware 链**（9 个 middleware）
- 包含 sandbox、MCP、community 和内置工具的**工具系统**
- 用于并行任务执行的 **subagent 委派**
- 带有 skills 注入、memory 上下文和工作目录指引的 **system prompt**

### Middleware 链

Middlewares 按严格顺序执行，每个 middleware 处理一个特定关注点：

| # | Middleware | 作用 |
|---|-----------|------|
| 1 | **ThreadDataMiddleware** | 创建按线程隔离的目录（workspace、uploads、outputs） |
| 2 | **UploadsMiddleware** | 将新上传的文件注入到对话上下文中 |
| 3 | **SandboxMiddleware** | 获取用于代码执行的 sandbox 环境 |
| 4 | **SummarizationMiddleware** | 在接近 token 限制时压缩上下文（可选） |
| 5 | **TodoListMiddleware** | 在 plan mode 中跟踪多步骤任务（可选） |
| 6 | **TitleMiddleware** | 在首次交互后自动生成对话标题 |
| 7 | **MemoryMiddleware** | 将对话加入异步 memory 提取队列 |
| 8 | **ViewImageMiddleware** | 为支持 vision 的模型注入图像数据（条件启用） |
| 9 | **ClarificationMiddleware** | 拦截澄清请求并中断执行（必须最后） |

### Sandbox 系统

具备虚拟路径转换的按线程隔离执行：

- **抽象接口**：`execute_command`、`read_file`、`write_file`、`list_dir`
- **Providers**：`LocalSandboxProvider`（文件系统）和 `AioSandboxProvider`（Docker，位于 community/）。异步运行时路径使用异步 sandbox 生命周期钩子，因此启动、就绪轮询和释放不会阻塞事件循环。
- **虚拟路径**：`/mnt/user-data/{workspace,uploads,outputs}` → 线程专属物理目录
- **Skills 路径**：`/mnt/skills` → `deer-flow/skills/` 目录
- **Skills 加载**：递归发现 `skills/{public,custom}` 下嵌套的 `SKILL.md` 文件，并保留嵌套容器路径
- **文件写入安全性**：`str_replace` 按 `(sandbox.id, path)` 串行化读-改-写，因此即使虚拟路径相同，隔离的 sandboxes 也能保持并发
- **工具**：`bash`、`ls`、`read_file`、`write_file`、`str_replace`（`write_file` 默认覆盖，并暴露 `append` 用于文件末尾追加；使用 `LocalSandboxProvider` 时默认禁用 `bash`；若需要隔离的 shell 访问，请使用 `AioSandboxProvider`）

### Subagent 系统

具备并发执行能力的异步任务委派：

- **内置 agents**：`general-purpose`（完整工具集）和 `bash`（命令专家，仅在可用 shell 访问时暴露）
- **并发**：每轮最多 3 个 subagent，超时时间 15 分钟
- **执行**：带有状态跟踪和 SSE 事件的后台线程池
- **流程**：Agent 调用 `task()` 工具 → executor 在后台运行 subagent → 轮询直到完成 → 返回结果

### Memory 系统

由 LLM 驱动、可在对话间保留上下文的持久化机制：

- **自动提取**：分析对话中的用户上下文、事实和偏好
- **结构化存储**：用户上下文（工作、个人、当前关注）、历史以及带置信度评分的事实
- **去抖更新**：批量更新以减少 LLM 调用（等待时间可配置）
- **System prompt 注入**：将关键事实和上下文注入到 agent prompt 中
- **存储**：带有基于 mtime 的缓存失效机制的 JSON 文件

### 工具生态

| 类别 | 工具 |
|----------|-------|
| **Sandbox** | `bash`、`ls`、`read_file`、`write_file`、`str_replace` |
| **内置** | `present_files`、`ask_clarification`、`view_image`、`task`（subagent） |
| **Community** | Tavily（Web 搜索）、Jina AI（网页抓取）、Firecrawl（抓取）、DuckDuckGo（图片搜索） |
| **MCP** | 任意 Model Context Protocol 服务器（stdio、SSE、HTTP 传输） |
| **Skills** | 通过 system prompt 注入的领域特定工作流 |

### Gateway API

提供用于 frontend 集成的 REST 端点的 FastAPI 应用：

| 路由 | 作用 |
|-------|------|
| `GET /api/models` | 列出可用的 LLM models |
| `GET/PUT /api/mcp/config` | 管理 MCP server 配置 |
| `GET/PUT /api/skills` | 列出并管理 skills |
| `POST /api/skills/install` | 从 `.skill` 压缩包安装 skill |
| `GET /api/memory` | 获取 memory 数据 |
| `POST /api/memory/reload` | 强制重新加载 memory |
| `GET /api/memory/config` | Memory 配置 |
| `GET /api/memory/status` | 合并后的配置 + 数据 |
| `POST /api/threads/{id}/uploads` | 上传文件（自动将 PDF/PPT/Excel/Word 转换为 Markdown，拒绝目录路径，并在单次请求中自动重命名重复文件名） |
| `GET /api/threads/{id}/uploads/list` | 列出已上传文件 |
| `DELETE /api/threads/{id}` | 在 LangGraph 删除线程后，删除由 DeerFlow 管理的本地线程数据；意外失败会在服务端记录日志，并返回通用的 500 detail |
| `GET /api/threads/{id}/artifacts/{path}` | 提供生成的 artifacts |

### IM Channels

IM bridge 支持 Feishu、Slack 和 Telegram。Slack 和 Telegram 仍然使用最终的 `runs.wait()` 响应路径，而 Feishu 现在通过 `runs.stream(["messages-tuple", "values"])` 进行流式传输，并在原位更新同一张线程卡片。

对于 Feishu 卡片更新，DeerFlow 会为每条入站消息存储运行中卡片的 `message_id`，并在 run 结束前持续 patch 同一张卡片，从而保留现有的 `OK` / `DONE` 反应流程。

---

## 快速开始

### 先决条件

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 包管理器
- 你所选 LLM provider 的 API 密钥

### 安装

```bash
cd deer-flow

# Copy configuration files
cp config.example.yaml config.yaml

# Install backend dependencies
cd backend
make install
```

### 配置

编辑项目根目录中的 `config.yaml`：

```yaml
models:
  - name: gpt-4o
    display_name: GPT-4o
    use: langchain_openai:ChatOpenAI
    model: gpt-4o
    api_key: $OPENAI_API_KEY
    supports_thinking: false
    supports_vision: true

  - name: gpt-5-responses
    display_name: GPT-5 (Responses API)
    use: langchain_openai:ChatOpenAI
    model: gpt-5
    api_key: $OPENAI_API_KEY
    use_responses_api: true
    output_version: responses/v1
    supports_vision: true
```

设置你的 API 密钥：

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### 运行

**完整应用**（在项目根目录中）：

```bash
make dev  # Starts Gateway + Frontend + Nginx
```

访问地址：http://localhost:2026

**仅后端**（在 backend 目录中）：

```bash
# Gateway API + embedded agent runtime
make dev
```

直接访问：Gateway 位于 http://localhost:8001

---

## 项目结构

```
backend/
├── src/
│   ├── agents/                  # Agent system
│   │   ├── lead_agent/         # Main agent (factory, prompts)
│   │   ├── middlewares/        # 9 middleware components
│   │   ├── memory/             # Memory extraction & storage
│   │   └── thread_state.py    # ThreadState schema
│   ├── gateway/                # FastAPI Gateway API
│   │   ├── app.py             # Application setup
│   │   └── routers/           # 6 route modules
│   ├── sandbox/                # Sandbox execution
│   │   ├── local/             # Local filesystem provider
│   │   ├── sandbox.py         # Abstract interface
│   │   ├── tools.py           # bash, ls, read/write/str_replace
│   │   └── middleware.py      # Sandbox lifecycle
│   ├── subagents/              # Subagent delegation
│   │   ├── builtins/          # general-purpose, bash agents
│   │   ├── executor.py        # Background execution engine
│   │   └── registry.py        # Agent registry
│   ├── tools/builtins/         # Built-in tools
│   ├── mcp/                    # MCP protocol integration
│   ├── models/                 # Model factory
│   ├── skills/                 # Skill discovery & loading
│   ├── config/                 # Configuration system
│   ├── community/              # Community tools & providers
│   ├── reflection/             # Dynamic module loading
│   └── utils/                  # Utilities
├── docs/                       # Documentation
├── tests/                      # Test suite
├── langgraph.json              # LangGraph graph registry for tooling/Studio compatibility
├── pyproject.toml              # Python dependencies
├── Makefile                    # Development commands
└── Dockerfile                  # Container build
```

`langgraph.json` 并不是默认的服务入口点。脚本和 Docker 部署运行的是 Gateway 内嵌运行时；该文件保留用于 LangGraph 工具、Studio 或直接兼容 LangGraph Server。

---

## 配置

### 主配置（`config.yaml`）

放在项目根目录中。以 `$` 开头的配置值会解析为环境变量。

关键部分：
- `models` - 带有类路径、API 密钥、thinking/vision 标志的 LLM 配置
- `tools` - 带有模块路径和分组的工具定义
- `tool_groups` - 工具的逻辑分组
- `sandbox` - 执行环境 provider
- `skills` - skills 目录路径
- `title` - 自动标题生成设置
- `summarization` - 上下文总结设置
- `subagents` - Subagent 系统（启用/禁用）
- `memory` - Memory 系统设置（启用、存储、去抖、事实数量限制）

Provider 说明：
- `models[*].use` 通过模块路径引用 provider 类（例如 `langchain_openai:ChatOpenAI`）。
- 如果缺少 provider 模块，DeerFlow 现在会返回带有安装指引的可操作错误（例如 `uv add langchain-google-genai`）。

### 扩展配置（`extensions_config.json`）

将 MCP servers 和 skill 状态放在同一个文件中：

```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {"GITHUB_TOKEN": "$GITHUB_TOKEN"}
    },
    "secure-http": {
      "enabled": true,
      "type": "http",
      "url": "https://api.example.com/mcp",
      "oauth": {
        "enabled": true,
        "token_url": "https://auth.example.com/oauth/token",
        "grant_type": "client_credentials",
        "client_id": "$MCP_OAUTH_CLIENT_ID",
        "client_secret": "$MCP_OAUTH_CLIENT_SECRET"
      }
    }
  },
  "skills": {
    "pdf-processing": {"enabled": true}
  }
}
```

### 环境变量

- `DEER_FLOW_CONFIG_PATH` - 覆盖 `config.yaml` 位置
- `DEER_FLOW_EXTENSIONS_CONFIG_PATH` - 覆盖 `extensions_config.json` 位置
- Model API 密钥：`OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`DEEPSEEK_API_KEY` 等
- Tool API 密钥：`TAVILY_API_KEY`、`GITHUB_TOKEN` 等

### LangSmith Tracing

DeerFlow 内置了 [LangSmith](https://smith.langchain.com) 集成，用于可观测性。启用后，所有 LLM 调用、agent runs、工具执行和 middleware 处理都会被追踪，并可在 LangSmith 仪表板中查看。

**设置：**

1. 在 [smith.langchain.com](https://smith.langchain.com) 注册并创建一个项目。
2. 将以下内容添加到项目根目录中的 `.env` 文件：

```bash
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=lsv2_pt_xxxxxxxxxxxxxxxx
LANGSMITH_PROJECT=xxx
```

**旧版变量：** 也支持 `LANGCHAIN_TRACING_V2`、`LANGCHAIN_API_KEY`、`LANGCHAIN_PROJECT` 和 `LANGCHAIN_ENDPOINT` 变量以保持向后兼容。当两者都设置时，`LANGSMITH_*` 变量优先。

### Langfuse Tracing

DeerFlow 还支持 [Langfuse](https://langfuse.com) 对兼容 LangChain 的运行进行可观测性追踪。

将以下内容添加到你的 `.env` 文件：

```bash
LANGFUSE_TRACING=true
LANGFUSE_PUBLIC_KEY=pk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_SECRET_KEY=sk-lf-xxxxxxxxxxxxxxxx
LANGFUSE_BASE_URL=https://cloud.langfuse.com
```

如果你使用的是自托管 Langfuse 部署，请将 `LANGFUSE_BASE_URL` 设置为你的 Langfuse 主机。

### 双 Provider 行为

如果同时启用了 LangSmith 和 Langfuse，DeerFlow 会初始化并附加两者的 callbacks，使同一份运行数据同时上报到两个系统。

如果某个 provider 被显式启用但缺少必需凭据，或者无法初始化 provider callback，DeerFlow 会在创建模型期间初始化 tracing 时抛出错误，而不是静默禁用 tracing。

**Docker：** 在 `docker-compose.yaml` 中，默认禁用 tracing（`LANGSMITH_TRACING=false`）。要在容器化部署中启用 tracing，请在你的 `.env` 中设置 `LANGSMITH_TRACING=true` 和/或 `LANGFUSE_TRACING=true`，并同时提供所需凭据。

---

## 开发

### 命令

```bash
make install    # Install dependencies
make dev        # Run Gateway API + embedded agent runtime (port 8001)
make gateway    # Run Gateway API without reload (port 8001)
make lint       # Run linter (ruff)
make format     # Format code (ruff)
```

### 代码风格

- **Linter/Formatter**：`ruff`
- **行长度**：240 个字符
- **Python**：3.12+，带类型提示
- **引号**：双引号
- **缩进**：4 个空格

### 测试

```bash
uv run pytest
```

---

## 技术栈

- **LangGraph**（1.0.6+）- Agent 框架与多 agent 编排
- **LangChain**（1.2.3+）- LLM 抽象与工具系统
- **FastAPI**（0.115.0+）- Gateway REST API
- **langchain-mcp-adapters** - Model Context Protocol 支持
- **agent-sandbox** - 沙箱化代码执行
- **markitdown** - 多格式文档转换
- **tavily-python** / **firecrawl-py** - Web 搜索与抓取

---

## 文档

- [配置指南](docs/CONFIGURATION.md)
- [架构细节](docs/ARCHITECTURE.md)
- [API 参考](docs/API.md)
- [文件上传](docs/FILE_UPLOAD.md)
- [路径示例](docs/PATH_EXAMPLES.md)
- [上下文总结](docs/summarization.md)
- [Plan Mode](docs/plan_mode_usage.md)
- [安装指南](docs/SETUP.md)

---

## 许可证

请参阅项目根目录中的 [LICENSE](../LICENSE) 文件。

## 贡献

贡献指南请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。
