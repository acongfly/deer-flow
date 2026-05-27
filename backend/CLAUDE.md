# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在处理此仓库中的代码时提供指导。

## 项目概览

DeerFlow 是一个基于 LangGraph 的 AI super agent 系统，采用全栈架构。后端提供了一个“super agent”，具备 sandbox 执行、持久化 memory、subagent 委派以及可扩展的工具集成——所有这些都运行在按线程隔离的环境中。

**架构**：
- **Gateway API**（端口 8001）：REST API 加内嵌的兼容 LangGraph 的 agent 运行时
- **Frontend**（端口 3000）：Next.js Web 界面
- **Nginx**（端口 2026）：统一的反向代理入口
- **Provisioner**（端口 8002，在 Docker 开发环境中可选）：仅当 sandbox 配置为 provisioner/Kubernetes 模式时启动

**运行时**：
- `make dev`、Docker dev 和生产环境都通过 `RunManager` + `run_agent()` + `StreamBridge`（`packages/harness/deerflow/runtime/`）在 Gateway 中运行 agent 运行时。Nginx 在 `/api/langgraph/*` 暴露该运行时，并将其重写到 Gateway 原生的 `/api/*` 路由上。

**项目结构**：
```
deer-flow/
├── Makefile                    # Root commands (check, install, dev, stop)
├── config.yaml                 # Main application configuration
├── extensions_config.json      # MCP servers and skills configuration
├── backend/                    # Backend application (this directory)
│   ├── Makefile               # Backend-only commands (dev, gateway, lint)
│   ├── langgraph.json         # LangGraph Studio graph configuration
│   ├── packages/
│   │   └── harness/           # deerflow-harness package (import: deerflow.*)
│   │       ├── pyproject.toml
│   │       └── deerflow/
│   │           ├── agents/            # LangGraph agent system
│   │           │   ├── lead_agent/    # Main agent (factory + system prompt)
│   │           │   ├── middlewares/   # 10 middleware components
│   │           │   ├── memory/        # Memory extraction, queue, prompts
│   │           │   └── thread_state.py # ThreadState schema
│   │           ├── sandbox/           # Sandbox execution system
│   │           │   ├── local/         # Local filesystem provider
│   │           │   ├── sandbox.py     # Abstract Sandbox interface
│   │           │   ├── tools.py       # bash, ls, read/write/str_replace
│   │           │   └── middleware.py  # Sandbox lifecycle management
│   │           ├── subagents/         # Subagent delegation system
│   │           │   ├── builtins/      # general-purpose, bash agents
│   │           │   ├── executor.py    # Background execution engine
│   │           │   └── registry.py    # Agent registry
│   │           ├── tools/builtins/    # Built-in tools (present_files, ask_clarification, view_image)
│   │           ├── mcp/               # MCP integration (tools, cache, client)
│   │           ├── models/            # Model factory with thinking/vision support
│   │           ├── skills/            # Skills discovery, loading, parsing
│   │           ├── config/            # Configuration system (app, model, sandbox, tool, etc.)
│   │           ├── community/         # Community tools (tavily, jina_ai, firecrawl, image_search, aio_sandbox)
│   │           ├── reflection/        # Dynamic module loading (resolve_variable, resolve_class)
│   │           ├── utils/             # Utilities (network, readability)
│   │           └── client.py          # Embedded Python client (DeerFlowClient)
│   ├── app/                   # Application layer (import: app.*)
│   │   ├── gateway/           # FastAPI Gateway API
│   │   │   ├── app.py         # FastAPI application
│   │   │   └── routers/       # FastAPI route modules (models, mcp, memory, skills, uploads, threads, artifacts, agents, suggestions, channels)
│   │   └── channels/          # IM platform integrations
│   ├── tests/                 # Test suite
│   └── docs/                  # Documentation
├── frontend/                   # Next.js frontend application
└── skills/                     # Agent skills directory
    ├── public/                # Public skills (committed)
    └── custom/                # Custom skills (gitignored)
```

## 重要开发指南

### 文档更新政策
**关键：每次代码变更后都必须更新 README.md 和 CLAUDE.md**

在进行代码更改时，你**必须**更新相关文档：
- 对用户可见的更改（功能、安装、使用说明）更新 `README.md`
- 对开发相关的更改（架构、命令、工作流、内部系统）更新 `CLAUDE.md`
- 始终让文档与代码库保持同步
- 确保所有文档内容准确且及时

## 命令

**根目录**（用于完整应用）：
```bash
make check      # Check system requirements
make install    # Install all dependencies (frontend + backend)
make dev        # Start all services (Gateway + Frontend + Nginx), with config.yaml preflight
make start      # Start production services locally
make stop       # Stop all services
```

**Backend 目录**（仅用于后端开发）：
```bash
make install    # Install backend dependencies
make dev        # Run Gateway API with reload (port 8001)
make gateway    # Run Gateway API only (port 8001)
make test       # Run all backend tests
make lint       # Lint with ruff
make format     # Format code with ruff
```

与 Docker/provisioner 行为相关的回归测试：
- `tests/test_docker_sandbox_mode_detection.py`（从 `config.yaml` 检测模式）
- `tests/test_provisioner_kubeconfig.py`（kubeconfig 文件/目录处理）

边界检查（harness → app 导入防火墙）：
- `tests/test_harness_boundary.py` —— 确保 `packages/harness/deerflow/` 永远不会从 `app.*` 导入

CI 会通过 [.github/workflows/backend-unit-tests.yml](../.github/workflows/backend-unit-tests.yml) 在每个 pull request 上运行这些回归测试。

## 架构

### Harness / App 拆分

后端被拆分为两层，并遵循严格的依赖方向：

- **Harness**（`packages/harness/deerflow/`）：可发布的 agent 框架包（`deerflow-harness`）。导入前缀：`deerflow.*`。包含 agent 编排、工具、sandbox、models、MCP、skills、config —— 构建和运行 agents 所需的一切。
- **App**（`app/`）：不发布的应用代码。导入前缀：`app.*`。包含 FastAPI Gateway API 和 IM 渠道集成（Feishu、Slack、Telegram、DingTalk）。

**依赖规则**：App 可以导入 deerflow，但 deerflow 绝不能导入 app。这个边界由 `tests/test_harness_boundary.py` 强制执行，并在 CI 中检查。

**导入约定**：
```python
# Harness internal
from deerflow.agents import make_lead_agent
from deerflow.models import create_chat_model

# App internal
from app.gateway.app import app
from app.channels.service import start_channel_service

# App → Harness (allowed)
from deerflow.config import get_app_config

# Harness → App (FORBIDDEN — enforced by test_harness_boundary.py)
# from app.gateway.routers.uploads import ...  # ← will fail CI
```

### Agent 系统

**Lead Agent**（`packages/harness/deerflow/agents/lead_agent/agent.py`）：
- 入口点：`make_lead_agent(config: RunnableConfig)`，注册于 `langgraph.json`
- 通过 `create_chat_model()` 实现动态模型选择，并支持 thinking/vision
- 工具通过 `get_available_tools()` 加载 —— 组合 sandbox、内置、MCP、community 和 subagent 工具
- System prompt 通过 `apply_prompt_template()` 生成，包含 skills、memory 和 subagent 说明

**ThreadState**（`packages/harness/deerflow/agents/thread_state.py`）：
- 在 `AgentState` 基础上扩展：`sandbox`、`thread_data`、`title`、`artifacts`、`todos`、`uploaded_files`、`viewed_images`
- 使用自定义 reducer：`merge_artifacts`（去重）、`merge_viewed_images`（合并/清空）

**运行时配置**（通过 `config.configurable`）：
- `thinking_enabled` - 启用模型的扩展 thinking
- `model_name` - 选择特定的 LLM model
- `is_plan_mode` - 启用 TodoList middleware
- `subagent_enabled` - 启用任务委派工具

### Middleware 链

Lead-agent 的 middlewares 按严格的追加顺序组装，位置分别在 `packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`（`build_lead_runtime_middlewares`）和 `packages/harness/deerflow/agents/lead_agent/agent.py`（`_build_middlewares`）：

1. **ThreadDataMiddleware** - 在用户隔离作用域下创建按线程划分的目录（`backend/.deer-flow/users/{user_id}/threads/{thread_id}/user-data/{workspace,uploads,outputs}`）；通过 `get_effective_user_id()` 解析 `user_id`（在无认证模式下回退到 `"default"`）；Web UI 删除线程时，现在会先执行 LangGraph 线程删除，再由 Gateway 清理本地线程目录
2. **UploadsMiddleware** - 跟踪并将新上传的文件注入到对话中
3. **SandboxMiddleware** - 获取 sandbox，并将 `sandbox_id` 存入 state
4. **DanglingToolCallMiddleware** - 为缺少响应的 AIMessage `tool_calls` 注入占位 `ToolMessage`（例如用户中断导致的情况），其中原始 provider tool-call 负载仅保留在 `additional_kwargs["tool_calls"]` 中
5. **LLMErrorHandlingMiddleware** - 在后续 middleware/工具阶段运行之前，将 provider/model 调用失败规范化为可恢复、面向 assistant 的错误
6. **GuardrailMiddleware** - 通过可插拔的 `GuardrailProvider` 协议在工具调用前做鉴权（可选，需在配置中启用 `guardrails.enabled`）。它会评估每个工具调用，并在拒绝时返回错误 `ToolMessage`。支持三类 provider：内置的 `AllowlistProvider`（零依赖）、OAP 策略 provider（例如 `aport-agent-guardrails`）或自定义 provider。设置、用法以及 provider 实现方法见 [docs/GUARDRAILS.md](docs/GUARDRAILS.md)。
7. **SandboxAuditMiddleware** - 在继续执行工具之前，对 sandbox 中的 shell/文件操作进行审计，用于安全日志记录
8. **ToolErrorHandlingMiddleware** - 将工具异常转换为错误 `ToolMessage`，使运行能够继续而不是中止
9. **SummarizationMiddleware** - 在接近 token 限制时进行上下文压缩（可选，需启用）
10. **TodoListMiddleware** - 通过 `write_todos` 工具进行任务跟踪（可选，在 plan_mode 下启用）
11. **TokenUsageMiddleware** - 在启用 token 跟踪时记录 token 使用指标（可选）；仅在启用 token 使用跟踪时，subagent 的使用量才会按 `tool_call_id` 缓存，并按消息位置而不是消息 id 合并回发起分派的 AIMessage 中
12. **TitleMiddleware** - 在首次完整交互后自动生成线程标题，并在向标题模型发起请求前规范化结构化消息内容
13. **MemoryMiddleware** - 将对话加入异步 memory 更新队列（仅过滤 user + 最终 AI 响应）
14. **ViewImageMiddleware** - 在调用 LLM 之前注入 base64 图像数据（仅在支持 vision 时启用）
15. **DeferredToolFilterMiddleware** - 在启用工具搜索之前，对已绑定模型隐藏 deferred 工具 schema（可选）
16. **SubagentLimitMiddleware** - 截断模型响应中过多的 `task` 工具调用，以强制执行 `MAX_CONCURRENT_SUBAGENTS` 限制（可选，在 `subagent_enabled` 时启用）
17. **LoopDetectionMiddleware** - 检测重复的工具调用循环；硬停止响应会在强制输出最终文本答案前清除结构化 `tool_calls` 以及原始 provider tool-call 元数据
18. **ClarificationMiddleware** - 拦截 `ask_clarification` 工具调用，并通过 `Command(goto=END)` 中断（必须最后）

### 配置系统

**主配置**（`config.yaml`）：

设置方式：将 `config.example.yaml` 复制为**项目根目录**中的 `config.yaml`。

**配置版本控制**：`config.example.yaml` 包含 `config_version` 字段。启动时，`AppConfig.from_file()` 会比较用户版本与示例版本；若过期则发出警告。缺少 `config_version` 视为版本 0。运行 `make config-upgrade` 可自动合并缺失字段。修改配置 schema 时，请提升 `config.example.yaml` 中的 `config_version`。

**配置缓存**：`get_app_config()` 会缓存已解析的配置，但当解析后的配置路径发生变化或文件 mtime 增加时会自动重新加载。这样 Gateway 和 LangGraph 在读取 `config.yaml` 修改时无需手动重启进程也能保持一致。

**配置热重载边界**：Gateway 依赖在每次请求时都会通过 `get_app_config()` 获取配置，因此像 `models[*].max_tokens`、`summarization.*`、`title.*`、`memory.*`、`subagents.*`、`tools[*]` 以及 agent system prompt 这样的按运行生效字段，会在下一条消息时采纳 `config.yaml` 的修改。`AppConfig` 刻意**不会**缓存到 `app.state` 中——`lifespan()` 会保留一个本地 `startup_config` 变量，用于一次性的启动工作（日志级别、channels、`langgraph_runtime` 引擎），并将其显式传递给 `langgraph_runtime(app, startup_config)`。以下基础设施字段**必须重启**：

| 字段 | 为什么必须重启 |
|---|---|
| `database.*` | `init_engine_from_config()` 只会在 `langgraph_runtime()` 启动时运行一次；SQLAlchemy engine 会持有连接池。 |
| `checkpointer.*`（包括 SQLite WAL/journal 设置） | `make_checkpointer()` 只在启动时绑定一次持久化 checkpointer。 |
| `run_events.*` | `make_run_event_store()` 会在启动时决定使用内存实现还是 SQL 实现。 |
| `stream_bridge.*` | `make_stream_bridge()` 只会构建一次 bridge 对象。 |
| `sandbox.use` | `get_sandbox_provider()` 会缓存 provider 单例（`_default_sandbox_provider`）；新的类路径只有在下次进程启动时才会生效。 |
| `log_level` | `apply_logging_level()` 仅在 `app.py` 启动时调用；它会修改 root logger 的级别，而 `get_app_config()` 返回新的 `AppConfig` 不会重新触发该逻辑。 |
| `channels.*` IM 平台凭据 | `start_channel_service()` 只会在启动期间调用一次；配置变更时不会重建在线 channels。 |

配置优先级：
1. 显式传入的 `config_path` 参数
2. `DEER_FLOW_CONFIG_PATH` 环境变量
3. 当前目录（backend/）中的 `config.yaml`
4. 父目录（项目根目录——**推荐位置**）中的 `config.yaml`

以 `$` 开头的配置值会被解析为环境变量（例如 `$OPENAI_API_KEY`）。
`ModelConfig` 还声明了 `use_responses_api` 和 `output_version`，以便在继续使用 `langchain_openai:ChatOpenAI` 的同时，显式启用 OpenAI `/v1/responses`。

**扩展配置**（`extensions_config.json`）：

MCP servers 和 skills 统一配置在项目根目录中的 `extensions_config.json`：

配置优先级：
1. 显式传入的 `config_path` 参数
2. `DEER_FLOW_EXTENSIONS_CONFIG_PATH` 环境变量
3. 当前目录（backend/）中的 `extensions_config.json`
4. 父目录（项目根目录——**推荐位置**）中的 `extensions_config.json`

### Gateway API（`app/gateway/`）

运行在 8001 端口上的 FastAPI 应用，健康检查为 `GET /health`。设置 `GATEWAY_ENABLE_DOCS=false` 可在生产环境中禁用 `/docs`、`/redoc` 和 `/openapi.json`（默认：启用）。

默认情况下，当请求经由 2026 端口的 nginx 进入时，CORS 为同源。拆分域名或通过端口转发访问的浏览器客户端必须通过 `GATEWAY_CORS_ORIGINS`（逗号分隔的精确 origin）显式启用；Gateway 的 `CORSMiddleware` 和 `CSRFMiddleware` 都会读取该变量，以确保浏览器的 CORS 与认证 origin 校验保持一致。

**路由器**：

| 路由器 | 端点 |
|--------|-----------|
| **Models** (`/api/models`) | `GET /` - 列出 models；`GET /{name}` - model 详情 |
| **MCP** (`/api/mcp`) | `GET /config` - 获取配置；`PUT /config` - 更新配置（保存到 extensions_config.json） |
| **Skills** (`/api/skills`) | `GET /` - 列出 skills；`GET /{name}` - 详情；`PUT /{name}` - 更新 enabled；`POST /install` - 从 `.skill` 压缩包安装（接受标准可选 frontmatter，如 `version`、`author`、`compatibility`） |
| **Memory** (`/api/memory`) | `GET /` - memory 数据；`POST /reload` - 强制重载；`GET /config` - 配置；`GET /status` - 配置 + 数据 |
| **Uploads** (`/api/threads/{id}/uploads`) | `POST /` - 上传文件（自动转换 PDF/PPT/Excel/Word）；`GET /list` - 列表；`DELETE /{filename}` - 删除 |
| **Threads** (`/api/threads/{id}`) | `DELETE /` - 在 LangGraph 删除线程后移除 DeerFlow 管理的本地线程数据；意外失败会在服务端记录日志，并返回通用的 500 detail |
| **Artifacts** (`/api/threads/{id}/artifacts`) | `GET /{path}` - 提供 artifacts；主动内容类型（`text/html`、`application/xhtml+xml`、`image/svg+xml`）始终会被强制作为下载附件，以降低 XSS 风险；对其他文件类型，`?download=true` 也会强制下载 |
| **Suggestions** (`/api/threads/{id}/suggestions`) | `POST /` - 生成后续问题；在 JSON 解析前会规范化富文本列表/块模型内容 |
| **Thread Runs** (`/api/threads/{id}/runs`) | `POST /` - 创建后台 run；`POST /stream` - 创建 + SSE 流；`POST /wait` - 创建 + 阻塞；`GET /` - 列出 runs；`GET /{rid}` - run 详情；`POST /{rid}/cancel` - 取消；`GET /{rid}/join` - 连接 SSE；`GET /{rid}/messages` - 分页消息 `{data, has_more}`；`GET /{rid}/events` - 完整事件流；`GET /../messages` - 带反馈的线程消息；`GET /../token-usage` - 聚合 token |
| **Feedback** (`/api/threads/{id}/runs/{rid}/feedback`) | `PUT /` - upsert 反馈；`DELETE /` - 删除用户反馈；`POST /` - 创建反馈；`GET /` - 列出反馈；`GET /stats` - 聚合统计；`DELETE /{fid}` - 删除特定项 |
| **Runs** (`/api/runs`) | `POST /stream` - 无状态 run + SSE；`POST /wait` - 无状态 run + 阻塞；`GET /{rid}/messages` - 按 run_id 分页消息 `{data, has_more}`（cursor：`after_seq`/`before_seq`）；`GET /{rid}/feedback` - 按 run_id 列出反馈 |

**RunManager / RunStore 契约**：
- `RunManager.get()` 是异步的；直接调用方必须 `await` 它。
- 配置持久化 `RunStore` 后，`get()` 和 `list_by_thread()` 会从 store 中补全历史 runs。对于相同的 `run_id`，内存中的记录优先，以便 task、中止和流控制状态仍能附着在活动的本地 runs 上。
- `cancel()` 和 `create_or_reject(..., multitask_strategy="interrupt"|"rollback")` 会通过 `RunStore.update_status()` 持久化 interrupted 状态，与正常的 `set_status()` 状态变更保持一致。
- 仅由 store 补全的 runs 只可作为可读历史。如果当前 worker 没有该 run 的内存 task/control 状态，取消 API 可能返回 409，因为此 worker 无法停止该任务。

通过 nginx 代理：`/api/langgraph/*` → Gateway 内嵌的兼容 LangGraph 运行时，其他 `/api/*` → Gateway REST APIs。

### Sandbox 系统（`packages/harness/deerflow/sandbox/`）

**接口**：抽象 `Sandbox`，包含 `execute_command`、`read_file`、`write_file`、`list_dir`
**Provider 模式**：`SandboxProvider` 提供 `acquire`、`acquire_async`、`get`、`release` 生命周期。异步 agent/工具路径会调用异步 sandbox 生命周期钩子，因此 Docker sandbox 的创建、发现、跨进程锁、就绪轮询和释放都不会阻塞事件循环。
**实现**：
- `LocalSandboxProvider` - 本地文件系统执行。`acquire(thread_id)` 返回按线程划分的 `LocalSandbox`（id 为 `local:{thread_id}`），其 `path_mappings` 会将 `/mnt/user-data/{workspace,uploads,outputs}` 和 `/mnt/acp-workspace` 解析到该线程在宿主机上的目录，因此公开的 `Sandbox` API 能以与 AIO 一致的方式遵守 `/mnt/user-data` 契约。`acquire()` / `acquire(None)` 会为没有线程上下文的调用方保留旧的通用单例（id 为 `local`）。按线程划分的 sandboxes 保存在一个 LRU 缓存中（默认 256 项），并受 `threading.Lock` 保护。
- `AioSandboxProvider`（`packages/harness/deerflow/community/`）- 基于 Docker 的隔离

**虚拟路径系统**：
- Agent 看到的是：`/mnt/user-data/{workspace,uploads,outputs}`、`/mnt/skills`
- 物理路径：`backend/.deer-flow/users/{user_id}/threads/{thread_id}/user-data/...`、`deer-flow/skills/`
- 转换：`LocalSandboxProvider` 会在 acquire 时为 user-data 前缀构建按线程划分的 `PathMapping`；`tools.py` 保留 `replace_virtual_path()` / `replace_virtual_paths_in_command()` 作为纵深防御层（也用于路径校验）。AIO 会将这些目录以相同的虚拟路径挂载到容器内，因此两种实现都能原生接受 `/mnt/user-data/...`。
- 检测：`is_local_sandbox()` 同时接受 `sandbox_id == "local"`（旧版 / 无线程）和 `sandbox_id.startswith("local:")`（按线程）

**Sandbox 工具**（位于 `packages/harness/deerflow/sandbox/tools.py`）：
- `bash` - 执行命令，支持路径转换和错误处理
- `ls` - 目录列表（树形格式，最多 2 层）
- `read_file` - 读取文件内容，可选行范围
- `write_file` - 写入/追加文件，自动创建目录；默认覆盖，并在面向模型的 schema 中暴露 `append` 参数用于文件末尾写入
- `str_replace` - 子串替换（单次或全部匹配）；同一路径的串行化作用域限定为 `(sandbox.id, path)`，因此隔离的 sandboxes 在同一进程中不会因相同虚拟路径而相互争用

### Subagent 系统（`packages/harness/deerflow/subagents/`）

**内置 Agents**：`general-purpose`（除 `task` 外的所有工具）和 `bash`（命令专家）
**执行**：双线程池 —— `_scheduler_pool`（3 个 worker）+ `_execution_pool`（3 个 worker）
**并发**：`MAX_CONCURRENT_SUBAGENTS = 3` 由 `SubagentLimitMiddleware` 强制执行（在 `after_model` 中截断过多工具调用），超时时间 15 分钟
**流程**：`task()` 工具 → `SubagentExecutor` → 后台线程 → 每 5 秒轮询 → SSE 事件 → 结果
**事件**：`task_started`、`task_running`、`task_completed` / `task_failed` / `task_timed_out`

### 工具系统（`packages/harness/deerflow/tools/`）

`get_available_tools(groups, include_mcp, model_name, subagent_enabled)` 组装以下内容：
1. **配置定义的工具** - 通过 `resolve_variable()` 从 `config.yaml` 解析
2. **MCP 工具** - 来自已启用的 MCP servers（懒初始化，基于 mtime 的缓存失效）
3. **内置工具**：
   - `present_files` - 让输出文件对用户可见（仅 `/mnt/user-data/outputs`）
   - `ask_clarification` - 请求澄清（由 ClarificationMiddleware 拦截 → 中断）
   - `view_image` - 以 base64 读取图像（仅当模型支持 vision 时添加）
   - `setup_agent` - 仅用于 bootstrap：持久化全新的自定义 agent 的 `SOUL.md` 和 `config.yaml`。仅在 `is_bootstrap=True` 时绑定。
   - `update_agent` - 仅用于 custom-agent：在普通聊天中持久化对当前 agent 的自更新，更新其 `SOUL.md` / `config.yaml`（部分更新 + 原子写入）。在设置了 `agent_name` 且 `is_bootstrap=False` 时绑定。
4. **Subagent 工具**（若启用）：
   - `task` - 委派给 subagent（description、prompt、subagent_type）

**Community 工具**（`packages/harness/deerflow/community/`）：
- `tavily/` - Web 搜索（默认 5 个结果）和网页抓取（4KB 限制）
- `jina_ai/` - 通过 Jina reader API 抓取网页，并提取可读文本
- `firecrawl/` - 通过 Firecrawl API 进行网页抓取

**ACP agent 工具**：
- `invoke_acp_agent` - 调用来自 `config.yaml` 的外部 ACP 兼容 agents
- ACP launcher 必须是真正的 ACP adapter。标准 `codex` CLI 本身并不兼容 ACP；请配置包装器，例如 `npx -y @zed-industries/codex-acp` 或已安装的 `codex-acp` 二进制
- 缺失 ACP 可执行文件时，现在会返回可操作的错误信息，而不是原始的 `[Errno 2]`
- 每个 ACP agent 都使用按线程划分的工作区：`{base_dir}/users/{user_id}/threads/{thread_id}/acp-workspace/`。Lead agent 可通过虚拟路径 `/mnt/acp-workspace/`（只读）访问该工作区。在 docker sandbox 模式下，该目录会以只读方式挂载到容器内的 `/mnt/acp-workspace`；在 local sandbox 模式下，路径转换由 `tools.py` 处理
- `image_search/` - 通过 DuckDuckGo 进行图片搜索

### MCP 系统（`packages/harness/deerflow/mcp/`）

- 使用 `langchain-mcp-adapters` 的 `MultiServerMCPClient` 管理多服务器
- **懒初始化**：工具在首次使用时通过 `get_cached_mcp_tools()` 加载
- **缓存失效**：通过比较 mtime 检测配置文件变化
- **传输方式**：stdio（基于命令）、SSE、HTTP
- **OAuth（HTTP/SSE）**：支持 token endpoint 流程（`client_credentials`、`refresh_token`），并自动刷新 token + 注入 Authorization header
- **运行时更新**：Gateway API 会保存到 extensions_config.json；LangGraph 通过 mtime 检测变化

### Skills 系统（`packages/harness/deerflow/skills/`）

- **位置**：`deer-flow/skills/{public,custom}/`
- **格式**：包含 `SKILL.md` 的目录（YAML frontmatter：name、description、license、allowed-tools）
- **加载**：`load_skills()` 会递归扫描 `skills/{public,custom}` 下的 `SKILL.md`，解析元数据，并从 extensions_config.json 读取启用状态
- **注入**：已启用的 skills 会带着容器路径列入 agent system prompt
- **安装**：`POST /api/skills/install` 会将 `.skill` ZIP 压缩包解压到 `custom/` 目录

### Model Factory（`packages/harness/deerflow/models/factory.py`）

- `create_chat_model(name, thinking_enabled)` 通过反射从配置实例化 LLM
- 支持 `thinking_enabled` 标志，并可为每个 model 提供 `when_thinking_enabled` 覆盖
- 支持通过 `when_thinking_enabled.extra_body.chat_template_kwargs.enable_thinking` 为 vLLM 风格的 thinking 开关启用 Qwen 推理模型，同时为了向后兼容也会规范化旧版 `thinking` 配置
- 支持 `supports_vision` 标志，用于图像理解模型
- 以 `$` 开头的配置值会解析为环境变量
- 缺失 provider 模块时，会由反射解析器给出可操作的安装提示（例如 `uv add langchain-google-genai`）

### vLLM Provider（`packages/harness/deerflow/models/vllm_provider.py`）

- `VllmChatModel` 继承 `langchain_openai:ChatOpenAI`，用于 vLLM 0.19.0 的 OpenAI 兼容端点
- 在完整响应、流式增量以及后续 tool-call 回合中保留 vLLM 非标准的 assistant `reasoning` 字段
- 面向在 vLLM 0.19.0 Qwen 推理模型上通过 `extra_body.chat_template_kwargs.enable_thinking` 启用 thinking 的配置设计，同时也接受旧版 `thinking` 别名

### IM Channels 系统（`app/channels/`）

将外部消息平台（Feishu、Slack、Telegram、DingTalk）通过 LangGraph Server 桥接到 DeerFlow agent。

**架构**：Channels 通过 `langgraph-sdk` HTTP client（与 frontend 相同）与 Gateway 通信，从而确保线程由服务端创建和管理。内部 SDK client 会注入进程本地的内部认证，以及匹配的 CSRF cookie/header 对，因此 channel worker 发出的会修改线程/run 状态的请求无需依赖浏览器会话 cookie，也能被 Gateway 接受。

**组件**：
- `message_bus.py` - 异步发布/订阅枢纽（`InboundMessage` → queue → dispatcher；`OutboundMessage` → callbacks → channels）
- `store.py` - 基于 JSON 文件的持久化映射：`channel_name:chat_id[:topic_id]` → `thread_id`（根对话的键为 `channel:chat`，线程化对话的键为 `channel:chat:topic`）
- `manager.py` - 核心 dispatcher：通过 `client.threads.create()` 创建线程，路由命令，使 Slack/Telegram 走 `client.runs.wait()`，并让 Feishu 使用 `client.runs.stream(["messages-tuple", "values"])` 进行增量外发更新
- `base.py` - 抽象 `Channel` 基类（start/stop/send 生命周期）
- `service.py` - 根据 `config.yaml` 管理所有已配置 channels 的生命周期
- `slack.py` / `feishu.py` / `telegram.py` / `dingtalk.py` - 平台特定实现（`feishu.py` 会在内存中跟踪运行中卡片的 `message_id`，并原位 patch 同一张卡片；当配置了 `card_template_id` 时，`dingtalk.py` 可选用 AI Card 流式更新实现原位刷新）

**消息流**：
1. 外部平台 → Channel 实现 → `MessageBus.publish_inbound()`
2. `ChannelManager._dispatch_loop()` 从队列中消费
3. 对于聊天：通过 Gateway 兼容 LangGraph 的 API 查找/创建线程
4. Feishu 聊天：`runs.stream()` → 累积 AI 文本 → 发布多次 outbound 更新（`is_final=False`）→ 发布最终 outbound（`is_final=True`）
5. Slack/Telegram 聊天：`runs.wait()` → 提取最终响应 → 发布 outbound
6. Feishu channel 会先发送一张运行中的回复卡片，然后对每次 outbound 更新 patch 同一张卡片（卡片 JSON 设置 `config.update_multi=true` 以满足 Feishu patch API 的要求）
7. DingTalk AI Card 模式（配置了 `card_template_id` 时）：`runs.stream()` → 使用初始文本创建卡片 → 通过 `PUT /v1.0/card/streaming` 流式更新 → 在 `is_final=True` 时完成。若卡片创建或流式更新失败，则回退到 `sampleMarkdown`
8. 对于命令（`/new`、`/status`、`/models`、`/memory`、`/help`）：在本地处理或查询 Gateway API
9. Outbound → channel callbacks → 平台回复

**配置**（`config.yaml` -> `channels`）：
- `langgraph_url` - 兼容 LangGraph 的 Gateway API 基础 URL（默认：`http://localhost:8001/api`）
- `gateway_url` - 用于辅助命令的 Gateway API URL（默认：`http://localhost:8001`）
- 在 Docker Compose 中，IM channels 运行在 `gateway` 容器内，因此 `localhost` 指向该容器自身。请将 `langgraph_url` 设为 `http://gateway:8001/api`，`gateway_url` 设为 `http://gateway:8001`，或者设置 `DEER_FLOW_CHANNELS_LANGGRAPH_URL` / `DEER_FLOW_CHANNELS_GATEWAY_URL`。
- 各 channel 配置：`feishu`（app_id、app_secret）、`slack`（bot_token、app_token）、`telegram`（bot_token）、`dingtalk`（client_id、client_secret，以及可选的 `card_template_id` 用于 AI Card 流式更新）

### Memory 系统（`packages/harness/deerflow/agents/memory/`）

**组件**：
- `updater.py` - 基于 LLM 的 memory 更新，带事实提取、基于空白归一化的事实去重（比较前会去掉首尾空白），以及原子文件 I/O
- `queue.py` - 去抖更新队列（按线程去重、可配置等待时间）；会在入队时捕获 `user_id`，确保其跨越 `threading.Timer` 边界后仍可用
- `prompt.py` - 用于 memory 更新的 prompt 模板
- `storage.py` - 基于文件、按用户隔离的存储；缓存以 `(user_id, agent_name)` 元组为键

**按用户隔离**：
- Memory 按用户存储在 `{base_dir}/users/{user_id}/memory.json`
- 每个 agent、每个用户的 memory 位于 `{base_dir}/users/{user_id}/agents/{agent_name}/memory.json`
- 自定义 agent 定义（`SOUL.md` + `config.yaml`）也按用户存储在 `{base_dir}/users/{user_id}/agents/{agent_name}/`。旧版共享布局 `{base_dir}/agents/{agent_name}/` 仍保留为只读回退路径，供尚未迁移的安装使用
- `user_id` 通过 `deerflow.runtime.user_context` 中的 `get_effective_user_id()` 解析
- 在无认证模式下，`user_id` 默认是 `"default"`（常量 `DEFAULT_USER_ID`）
- 配置中使用绝对 `storage_path` 会退出按用户隔离机制
- **迁移**：运行 `PYTHONPATH=. python scripts/migrate_user_isolation.py` 可将旧版 `memory.json`、`threads/` 和 `agents/` 迁移到按用户隔离的布局。支持 `--dry-run`（预览变更）和 `--user-id USER_ID`（将无主的旧数据分配给某个用户，默认为 `default`）。

**数据结构**（存储于 `{base_dir}/users/{user_id}/memory.json`）：
- **用户上下文**：`workContext`、`personalContext`、`topOfMind`（1-3 句摘要）
- **历史**：`recentMonths`、`earlierContext`、`longTermBackground`
- **事实**：离散事实，包含 `id`、`content`、`category`（preference/knowledge/context/behavior/goal）、`confidence`（0-1）、`createdAt`、`source`

**工作流**：
1. `MemoryMiddleware` 过滤消息（用户输入 + 最终 AI 响应），通过 `get_effective_user_id()` 捕获 `user_id`，并将对话连同捕获到的 `user_id` 一起入队
2. 队列执行去抖（默认 30 秒），批量更新，并按线程去重
3. 后台线程调用 LLM 提取上下文更新和事实，使用存储的 `user_id`（而不是 timer 线程中不可用的 contextvar）
4. 以原子方式应用更新（临时文件 + rename），同时使缓存失效，并在追加前跳过重复的事实内容
5. 下一次交互会将前 15 条事实和上下文注入 system prompt 的 `<memory>` 标签中

针对 updater 的重点回归测试位于 `backend/tests/test_memory_updater.py`。

**配置**（`config.yaml` → `memory`）：
- `enabled` / `injection_enabled` - 总开关
- `storage_path` - memory.json 的路径（绝对路径会退出按用户隔离机制）
- `debounce_seconds` - 处理前等待时间（默认：30）
- `model_name` - 用于更新的 LLM（null = 默认 model）
- `max_facts` / `fact_confidence_threshold` - 事实存储限制（100 / 0.7）
- `max_injection_tokens` - prompt 注入的 token 限制（2000）

### Reflection 系统（`packages/harness/deerflow/reflection/`）

- `resolve_variable(path)` - 导入模块并返回变量（例如 `module.path:variable_name`）
- `resolve_class(path, base_class)` - 导入类并根据基类进行校验

### Tracing 系统（`packages/harness/deerflow/tracing/`）

同时支持 LangSmith 和 Langfuse。相关接线位于两层：

- `factory.py::build_tracing_callbacks()` —— 返回当前通过环境变量（`LANGSMITH_TRACING`、`LANGFUSE_TRACING` 等）启用的 providers 对应的 LangChain `CallbackHandler` 列表。对于图内运行，这些 handlers 会附加在**graph 调用根部**（`make_lead_agent` 和 `DeerFlowClient.stream` 都会在调用 graph 前将它们追加到 `config["callbacks"]` 中），从而让一次运行生成一条 trace，并将所有节点 / LLM / 工具调用作为子 span。对于独立调用方——即任何在此类 graph 之外调用模型的组件（例如 `MemoryUpdater`）——则保留 `create_chat_model` 默认的 `attach_tracing=True`，回退到模型级 callback 附加方式。
- `metadata.py::build_langfuse_trace_metadata()` —— 为 `RunnableConfig.metadata` 构建 Langfuse 保留的 trace 属性。Langfuse v4 的 `langchain.CallbackHandler` 会将这些属性提升到根 trace 上（见其 `_parse_langfuse_trace_attributes`），但只有在它看到 `on_chain_start(parent_run_id=None)` 时才会这么做——这也正是为什么 callbacks 必须位于 graph 根部，而不是 model 上。

**Trace 属性注入点**：`runtime/runs/worker.py::run_agent`（gateway 路径）和 `client.py::DeerFlowClient.stream`（embedded 路径）都会在构建 graph 前将 metadata 合并到 `config["metadata"]` 中。调用方提供的键会通过 `setdefault` 获得优先级，因此外部传入的 `session_id` 覆盖会被保留。字段映射如下：

| Langfuse 字段 | 来源 |
|-----------------------|----------------------------------------------|
| `langfuse_session_id` | LangGraph `thread_id` |
| `langfuse_user_id`    | `get_effective_user_id()`（无认证模式下为 `default`） |
| `langfuse_trace_name` | `RunRecord.assistant_id` / client `agent_name`（默认 `lead-agent`） |
| `langfuse_tags`       | `env:<DEER_FLOW_ENV>` + `model:<model_name>` |

当 Langfuse 不在启用的 provider 列表中时，返回 `{}` —— 仅使用 LangSmith 的部署不会受到影响。设置 `DEER_FLOW_ENV`（或 `ENVIRONMENT`）可按部署环境为 trace 打标签。测试位于 `tests/test_tracing_factory.py`、`tests/test_tracing_metadata.py`、`tests/test_worker_langfuse_metadata.py` 和 `tests/test_client_langfuse_metadata.py`。

### 配置 Schema

**`config.yaml`** 关键部分：
- `models[]` - LLM 配置，包含 `use` 类路径、`supports_thinking`、`supports_vision` 及 provider 特定字段
- vLLM 推理模型应使用 `deerflow.models.vllm_provider:VllmChatModel`；对于 Qwen 风格解析器，优先使用 `when_thinking_enabled.extra_body.chat_template_kwargs.enable_thinking`，同时 DeerFlow 也会规范化旧版 `thinking` 别名
- `tools[]` - 工具配置，包含 `use` 变量路径和 `group`
- `tool_groups[]` - 工具的逻辑分组
- `sandbox.use` - sandbox provider 类路径
- `skills.path` / `skills.container_path` - skills 目录在宿主机和容器中的路径
- `title` - 自动标题生成（enabled、max_words、max_chars、prompt_template）
- `summarization` - 上下文总结（enabled、触发条件、保留策略）
- `subagents.enabled` - subagent 委派的总开关
- `memory` - memory 系统（enabled、storage_path、debounce_seconds、model_name、max_facts、fact_confidence_threshold、injection_enabled、max_injection_tokens）

**`extensions_config.json`**：
- `mcpServers` - server 名称 → 配置的映射（enabled、type、command、args、env、url、headers、oauth、description）
- `skills` - skill 名称 → 状态的映射（enabled）

两者都可以通过 Gateway API 端点或 `DeerFlowClient` 方法在运行时修改。

### Embedded Client（`packages/harness/deerflow/client.py`）

`DeerFlowClient` 在无需 HTTP 服务的情况下，提供对所有 DeerFlow 能力的直接进程内访问。所有返回类型都与 Gateway API 的响应 schema 对齐，因此消费方代码在 HTTP 模式和 embedded 模式下都能一致工作。

**架构**：导入与 Gateway API 相同的 `deerflow` 模块。共享相同的配置文件和数据目录。不依赖 FastAPI。

**Agent 对话**：
- `chat(message, thread_id)` —— 同步方式，按 message-id 累积流式增量并返回最终 AI 文本
- `stream(message, thread_id)` —— 订阅 LangGraph `stream_mode=["values", "messages", "custom"]` 并产出 `StreamEvent`：
  - `"values"` —— 完整状态快照（title、messages、artifacts）；已通过 `messages` 模式传递的 AI 文本**不会**在此重新合成，以避免重复投递
  - `"messages-tuple"` —— 按块更新：对于 AI 文本，这是一个**增量**（按 `id` 拼接以重建完整消息）；工具调用和工具结果各只会发出一次
  - `"custom"` —— 从 `StreamWriter` 转发而来
  - `"end"` —— 流结束（携带按 message id 仅计数一次的累计 `usage`）
- Agent 通过 `create_agent()` + `_build_middlewares()` 懒创建，与 `make_lead_agent` 相同
- 支持 `checkpointer` 参数，以实现跨轮次的状态持久化
- `reset_agent()` 会强制重新创建 agent（例如在 memory 或 skill 变更后）
- 完整设计见 [docs/STREAMING.md](docs/STREAMING.md)：包括为什么 Gateway 与 DeerFlowClient 是并行路径、LangGraph 的 `stream_mode` 语义、按 id 去重的不变量，以及回归测试策略

**Gateway 等效方法**（替代 Gateway API）：

| 类别 | 方法 | 返回格式 |
|----------|---------|---------------|
| Models | `list_models()`, `get_model(name)` | `{"models": [...]}`, `{name, display_name, ...}` |
| MCP | `get_mcp_config()`, `update_mcp_config(servers)` | `{"mcp_servers": {...}}` |
| Skills | `list_skills()`, `get_skill(name)`, `update_skill(name, enabled)`, `install_skill(path)` | `{"skills": [...]}` |
| Memory | `get_memory()`, `reload_memory()`, `get_memory_config()`, `get_memory_status()` | dict |
| Uploads | `upload_files(thread_id, files)`, `list_uploads(thread_id)`, `delete_upload(thread_id, filename)` | `{"success": true, "files": [...]}`, `{"files": [...], "count": N}` |
| Artifacts | `get_artifact(thread_id, path)` → `(bytes, mime_type)` | tuple |

**与 Gateway 的关键差异**：Upload 接收本地 `Path` 对象而非 HTTP `UploadFile`，并会在复制前拒绝目录路径；当文档转换必须在活动事件循环内运行时，它会复用单个 worker。Artifact 返回 `(bytes, mime_type)`，而不是 HTTP Response。新的、仅 Gateway 提供的线程清理路由会在 LangGraph 删除线程后删除 `.deer-flow/threads/{thread_id}`；目前还没有对应的 `DeerFlowClient` 方法。`update_mcp_config()` 和 `update_skill()` 会自动使缓存的 agent 失效。

**测试**：`tests/test_client.py`（77 个单元测试，包括 `TestGatewayConformance`），`tests/test_client_live.py`（实时集成测试，需要 config.yaml）

**Gateway 一致性测试**（`TestGatewayConformance`）：验证每个返回 dict 的 client 方法都符合对应的 Gateway Pydantic 响应模型。每个测试都会用 Gateway 模型去解析 client 输出——如果 Gateway 新增了 client 未提供的必需字段，Pydantic 会抛出 `ValidationError`，CI 就能捕获这种漂移。覆盖范围：`ModelsListResponse`、`ModelResponse`、`SkillsListResponse`、`SkillResponse`、`SkillInstallResponse`、`McpConfigResponse`、`UploadResponse`、`MemoryConfigResponse`、`MemoryStatusResponse`。

## 开发工作流

### 测试驱动开发（TDD）——强制要求

**每个新功能或 bug 修复都必须附带单元测试。没有例外。**

- 在 `backend/tests/` 中编写测试，并遵循现有命名约定 `test_<feature>.py`
- 在变更前后都运行完整测试套件：`make test`
- 测试通过之前，功能不能视为完成
- 对于轻量级的配置/工具模块，优先编写不依赖外部服务的纯单元测试
- 如果某个模块在测试中引发循环导入问题，请在 `tests/conftest.py` 中添加 `sys.modules` mock（见 `deerflow.subagents.executor` 的现有示例）

```bash
# Run all tests
make test

# Run a specific test file
PYTHONPATH=. uv run pytest tests/test_<feature>.py -v
```

### 运行完整应用

在**项目根目录**中：
```bash
make dev
```

这会启动所有服务，并使应用可通过 `http://localhost:2026` 访问。

**所有启动模式：**

| | **本地前台** | **本地守护进程** | **Docker 开发环境** | **Docker 生产环境** |
|---|---|---|---|---|
| **开发** | `./scripts/serve.sh --dev`<br/>`make dev` | `./scripts/serve.sh --dev --daemon`<br/>`make dev-daemon` | `./scripts/docker.sh start`<br/>`make docker-start` | — |
| **生产** | `./scripts/serve.sh --prod`<br/>`make start` | `./scripts/serve.sh --prod --daemon`<br/>`make start-daemon` | — | `./scripts/deploy.sh`<br/>`make up` |

| 操作 | 本地 | Docker 开发环境 | Docker 生产环境 |
|---|---|---|---|
| **停止** | `./scripts/serve.sh --stop`<br/>`make stop` | `./scripts/docker.sh stop`<br/>`make docker-stop` | `./scripts/deploy.sh down`<br/>`make down` |
| **重启** | `./scripts/serve.sh --restart [flags]` | `./scripts/docker.sh restart` | — |

**Nginx 路由**：
- `/api/langgraph/*` → Gateway 内嵌运行时（8001），重写到 `/api/*`
- `/api/*`（其他）→ Gateway API（8001）
- `/`（非 API）→ Frontend（3000）

### 分别运行后端服务

在 **backend** 目录中：

```bash
# Gateway API
make gateway
```

直接访问（不经过 nginx）：
- Gateway：`http://localhost:8001`

### Frontend 配置

Frontend 使用环境变量连接后端服务：
- `NEXT_PUBLIC_LANGGRAPH_BASE_URL` - 默认为 `/api/langgraph`（经由 nginx）
- `NEXT_PUBLIC_BACKEND_BASE_URL` - 默认为空字符串（经由 nginx）

当从根目录使用 `make dev` 时，frontend 会自动通过 nginx 连接。

## 关键特性

### 文件上传

支持自动文档转换的多文件上传：
- 端点：`POST /api/threads/{thread_id}/uploads`
- 支持：PDF、PPT、Excel、Word 文档（通过 `markitdown` 转换）
- 在复制前拒绝目录输入，以确保上传保持全有或全无
- 当在活动事件循环中调用时，每个请求只复用一个转换 worker
- 文件存储在按线程隔离的目录中
- 单次上传请求中出现重复文件名时，会自动追加 `_N` 后缀重命名，避免后续文件截断前面的文件
- Agent 通过 `UploadsMiddleware` 获取上传文件列表

详见 [docs/FILE_UPLOAD.md](docs/FILE_UPLOAD.md)。

### Plan Mode

用于复杂多步骤任务的 TodoList middleware：
- 通过运行时配置控制：`config.configurable.is_plan_mode = True`
- 提供 `write_todos` 工具用于任务跟踪
- 同一时间仅允许一个任务处于 in_progress，支持实时更新

详见 [docs/plan_mode_usage.md](docs/plan_mode_usage.md)。

### 上下文总结

在接近 token 限制时自动总结对话：
- 在 `config.yaml` 中通过 `summarization` 键配置
- 触发类型：tokens、messages，或最大输入的比例
- 在总结旧消息时保留较新的消息

详见 [docs/summarization.md](docs/summarization.md)。

### Vision 支持

对于 `supports_vision: true` 的 models：
- `ViewImageMiddleware` 处理对话中的图像
- `view_image_tool` 会被加入 agent 的工具集
- 图像会自动转换为 base64 并注入到 state 中

## 代码风格

- 使用 `ruff` 进行 lint 和格式化
- 行长度：240 个字符
- Python 3.12+，带类型提示
- 双引号、空格缩进

## 文档

详见 `docs/` 目录中的详细文档：
- [CONFIGURATION.md](docs/CONFIGURATION.md) - 配置选项
- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - 架构细节
- [API.md](docs/API.md) - API 参考
- [SETUP.md](docs/SETUP.md) - 安装指南
- [FILE_UPLOAD.md](docs/FILE_UPLOAD.md) - 文件上传功能
- [PATH_EXAMPLES.md](docs/PATH_EXAMPLES.md) - 路径类型与用法
- [summarization.md](docs/summarization.md) - 上下文总结
- [plan_mode_usage.md](docs/plan_mode_usage.md) - 带 TodoList 的 Plan Mode
