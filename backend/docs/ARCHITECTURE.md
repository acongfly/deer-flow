# 架构概览

本文档全面概述了 DeerFlow backend 的架构。

## 系统架构

```
┌──────────────────────────────────────────────────────────────────────────┐
│                              Client (Browser)                             │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                          Nginx (Port 2026)                               │
│                    Unified Reverse Proxy Entry Point                      │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │  /api/langgraph/*  →  Gateway LangGraph-compatible runtime (8001)  │  │
│  │  /api/*            →  Gateway REST APIs (8001)                     │  │
│  │  /*                →  Frontend (3000)                               │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
          ┌───────────────────────┴───────────────────────┐
          │                                               │
          ▼                                               ▼
┌─────────────────────────────────────────────┐ ┌─────────────────────┐
│              Gateway API                    │ │     Frontend        │
│              (Port 8001)                    │ │    (Port 3000)      │
│                                             │ │                     │
│  - LangGraph-compatible runs/threads API    │ │  - Next.js App      │
│  - Embedded Agent Runtime                   │ │  - React UI         │
│  - SSE Streaming                            │ │  - Chat Interface   │
│  - Checkpointing                            │ │                     │
│  - Models, MCP, Skills, Uploads, Artifacts  │ │                     │
│  - Thread Cleanup                           │ │                     │
└─────────────────────────────────────────────┘ └─────────────────────┘
          │
          ▼
┌──────────────────────────────────────────────────────────────────────────┐
│                         Shared Configuration                              │
│  ┌─────────────────────────┐  ┌────────────────────────────────────────┐ │
│  │      config.yaml        │  │      extensions_config.json            │ │
│  │  - Models               │  │  - MCP Servers                         │ │
│  │  - Tools                │  │  - Skills State                        │ │
│  │  - Sandbox              │  │                                        │ │
│  │  - Summarization        │  │                                        │ │
│  └─────────────────────────┘  └────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
```

## 组件细节

### Gateway 内嵌 Agent Runtime

Agent runtime 内嵌在 FastAPI Gateway 中，并构建于 LangGraph 之上，以实现稳健的多 agent 工作流编排。Nginx 会将 `/api/langgraph/*` 重写到 Gateway 原生的 `/api/*` 路由，因此无需单独运行 LangGraph server，也能保持对外 API 与 LangGraph SDK 客户端兼容。

**入口点**：`packages/harness/deerflow/agents/lead_agent/agent.py:make_lead_agent`

**核心职责：**
- 创建和配置 agent
- 管理 thread 状态
- 执行 middleware 链
- 编排工具执行
- 通过 SSE 提供实时响应流

**Graph registry**：`langgraph.json` 仍可供工具链、Studio 或直接兼容 LangGraph Server 的场景使用。
它不是默认的服务入口；脚本和 Docker 部署运行的是 Gateway 内嵌 runtime。

```json
{
  "agent": {
    "type": "agent",
    "path": "deerflow.agents:make_lead_agent"
  }
}
```

### Gateway API 服务

FastAPI 应用，提供 REST 端点以及公开的兼容 LangGraph 的 `/api/langgraph/*` runtime 路由。

**入口点**：`app/gateway/app.py`

**路由器：**
- `models.py` - `/api/models` - 模型列表与详情
- `thread_runs.py` / `runs.py` - `/api/threads/{id}/runs`、`/api/runs/*` - 兼容 LangGraph 的 runs 与流式传输
- `mcp.py` - `/api/mcp` - MCP server 配置
- `skills.py` - `/api/skills` - Skills 管理
- `uploads.py` - `/api/threads/{id}/uploads` - 文件上传
- `threads.py` - `/api/threads/{id}` - 在 LangGraph 删除后清理由 DeerFlow 管理的本地 thread 数据
- `artifacts.py` - `/api/threads/{id}/artifacts` - artifact 提供
- `suggestions.py` - `/api/threads/{id}/suggestions` - 后续建议生成

Web 对话删除流程会先通过兼容 LangGraph 的路由删除 Gateway 管理的 thread 状态，然后再由 Gateway 的 `threads.py` 路由通过 `Paths.delete_thread_dir()` 删除由 DeerFlow 管理的文件系统数据。

### Agent 架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           make_lead_agent(config)                        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            Middleware Chain                              │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │ 1. ThreadDataMiddleware  - Initialize workspace/uploads/outputs  │   │
│  │ 2. UploadsMiddleware     - Process uploaded files               │   │
│  │ 3. SandboxMiddleware     - Acquire sandbox environment          │   │
│  │ 4. SummarizationMiddleware - Context reduction (if enabled)     │   │
│  │ 5. TitleMiddleware       - Auto-generate titles                 │   │
│  │ 6. TodoListMiddleware    - Task tracking (if plan_mode)         │   │
│  │ 7. ViewImageMiddleware   - Vision model support                 │   │
│  │ 8. ClarificationMiddleware - Handle clarifications              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              Agent Core                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐   │
│  │      Model       │  │      Tools       │  │    System Prompt     │   │
│  │  (from factory)  │  │  (configured +   │  │  (with skills)       │   │
│  │                  │  │   MCP + builtin) │  │                      │   │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

### Thread 状态

`ThreadState` 在 LangGraph 的 `AgentState` 基础上扩展了额外字段：

```python
class ThreadState(AgentState):
    # Core state from AgentState
    messages: list[BaseMessage]

    # DeerFlow extensions
    sandbox: dict             # Sandbox environment info
    artifacts: list[str]      # Generated file paths
    thread_data: dict         # {workspace, uploads, outputs} paths
    title: str | None         # Auto-generated conversation title
    todos: list[dict]         # Task tracking (plan mode)
    viewed_images: dict       # Vision model image data
```

### Sandbox 系统

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           Sandbox Architecture                           │
└─────────────────────────────────────────────────────────────────────────┘

                      ┌─────────────────────────┐
                      │    SandboxProvider      │ (Abstract)
                      │  - acquire()            │
                      │  - get()                │
                      │  - release()            │
                      └────────────┬────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                                         │
              ▼                                         ▼
┌─────────────────────────┐              ┌─────────────────────────┐
│  LocalSandboxProvider   │              │  AioSandboxProvider     │
│  (packages/harness/deerflow/sandbox/local.py) │              │  (packages/harness/deerflow/community/)       │
│                         │              │                         │
│  - Singleton instance   │              │  - Docker-based         │
│  - Direct execution     │              │  - Isolated containers  │
│  - Development use      │              │  - Production use       │
└─────────────────────────┘              └─────────────────────────┘

                      ┌─────────────────────────┐
                      │        Sandbox          │ (Abstract)
                      │  - execute_command()    │
                      │  - read_file()          │
                      │  - write_file()         │
                      │  - list_dir()           │
                      └─────────────────────────┘
```

**虚拟路径映射：**

| 虚拟路径 | 物理路径 |
|-------------|---------------|
| `/mnt/user-data/workspace` | `backend/.deer-flow/threads/{thread_id}/user-data/workspace` |
| `/mnt/user-data/uploads` | `backend/.deer-flow/threads/{thread_id}/user-data/uploads` |
| `/mnt/user-data/outputs` | `backend/.deer-flow/threads/{thread_id}/user-data/outputs` |
| `/mnt/skills` | `deer-flow/skills/` |

### 工具系统

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            Tool Sources                                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   Built-in Tools    │  │  Configured Tools   │  │     MCP Tools       │
│  (packages/harness/deerflow/tools/)       │  │  (config.yaml)      │  │  (extensions.json)  │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ - present_files     │  │ - web_search        │  │ - github            │
│ - ask_clarification │  │ - web_fetch         │  │ - filesystem        │
│ - view_image        │  │ - bash              │  │ - postgres          │
│                     │  │ - read_file         │  │ - brave-search      │
│                     │  │ - write_file        │  │ - puppeteer         │
│                     │  │ - str_replace       │  │ - ...               │
│                     │  │ - ls                │  │                     │
└─────────────────────┘  └─────────────────────┘  └─────────────────────┘
           │                       │                       │
           └───────────────────────┴───────────────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │   get_available_tools() │
                      │   (packages/harness/deerflow/tools/__init__)  │
                      └─────────────────────────┘
```

### 模型工厂

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Model Factory                                   │
│                     (packages/harness/deerflow/models/factory.py)                              │
└─────────────────────────────────────────────────────────────────────────┘

config.yaml:
┌─────────────────────────────────────────────────────────────────────────┐
│ models:                                                                  │
│   - name: gpt-4                                                         │
│     display_name: GPT-4                                                 │
│     use: langchain_openai:ChatOpenAI                                    │
│     model: gpt-4                                                        │
│     api_key: $OPENAI_API_KEY                                            │
│     max_tokens: 4096                                                    │
│     supports_thinking: false                                            │
│     supports_vision: true                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │   create_chat_model()   │
                      │  - name: str            │
                      │  - thinking_enabled     │
                      └────────────┬────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │   resolve_class()       │
                      │  (reflection system)    │
                      └────────────┬────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │   BaseChatModel         │
                      │  (LangChain instance)   │
                      └─────────────────────────┘
```

**支持的 Provider：**
- OpenAI (`langchain_openai:ChatOpenAI`)
- Anthropic (`langchain_anthropic:ChatAnthropic`)
- DeepSeek (`langchain_deepseek:ChatDeepSeek`)
- 通过 LangChain integrations 接入的自定义 provider

### MCP 集成

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          MCP Integration                                 │
│                        (packages/harness/deerflow/mcp/manager.py)                              │
└─────────────────────────────────────────────────────────────────────────┘

extensions_config.json:
┌─────────────────────────────────────────────────────────────────────────┐
│ {                                                                        │
│   "mcpServers": {                                                       │
│     "github": {                                                         │
│       "enabled": true,                                                  │
│       "type": "stdio",                                                  │
│       "command": "npx",                                                 │
│       "args": ["-y", "@modelcontextprotocol/server-github"],           │
│       "env": {"GITHUB_TOKEN": "$GITHUB_TOKEN"}                          │
│     }                                                                   │
│   }                                                                     │
│ }                                                                       │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
                      ┌─────────────────────────┐
                      │  MultiServerMCPClient   │
                      │  (langchain-mcp-adapters)│
                      └────────────┬────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
       ┌───────────┐        ┌───────────┐        ┌───────────┐
       │  stdio    │        │   SSE     │        │   HTTP    │
       │ transport │        │ transport │        │ transport │
       └───────────┘        └───────────┘        └───────────┘
```

### Skills 系统

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Skills System                                   │
│                       (packages/harness/deerflow/skills/loader.py)                             │
└─────────────────────────────────────────────────────────────────────────┘

目录结构：
┌─────────────────────────────────────────────────────────────────────────┐
│ skills/                                                                  │
│ ├── public/                        # Public skills (committed)           │
│ │   ├── pdf-processing/                                                 │
│ │   │   └── SKILL.md                                                    │
│ │   ├── frontend-design/                                                │
│ │   │   └── SKILL.md                                                    │
│ │   └── ...                                                             │
│ └── custom/                        # Custom skills (gitignored)          │
│     └── user-installed/                                                 │
│         └── SKILL.md                                                    │
└─────────────────────────────────────────────────────────────────────────┘

`SKILL.md` 格式：
┌─────────────────────────────────────────────────────────────────────────┐
│ ---                                                                      │
│ name: PDF Processing                                                     │
│ description: Handle PDF documents efficiently                            │
│ license: MIT                                                            │
│ allowed-tools:                                                          │
│   - read_file                                                           │
│   - write_file                                                          │
│   - bash                                                                │
│ ---                                                                      │
│                                                                          │
│ # Skill Instructions                                                     │
│ Content injected into system prompt...                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

### 请求流

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Request Flow Example                             │
│                    User sends message to agent                           │
└─────────────────────────────────────────────────────────────────────────┘

1. Client → Nginx
   POST /api/langgraph/threads/{thread_id}/runs
   {"input": {"messages": [{"role": "user", "content": "Hello"}]}}

2. Nginx → Gateway API (8001)
   `/api/langgraph/*` is rewritten to Gateway's LangGraph-compatible `/api/*` routes

3. Gateway embedded runtime
   a. Load/create thread state
   b. Execute middleware chain:
      - ThreadDataMiddleware: Set up paths
      - UploadsMiddleware: Inject file list
      - SandboxMiddleware: Acquire sandbox
      - SummarizationMiddleware: Check token limits
      - TitleMiddleware: Generate title if needed
      - TodoListMiddleware: Load todos (if plan mode)
      - ViewImageMiddleware: Process images
      - ClarificationMiddleware: Check for clarifications

   c. Execute agent:
      - Model processes messages
      - May call tools (bash, web_search, etc.)
      - Tools execute via sandbox
      - Results added to messages

   d. Stream response via SSE

4. Client receives streaming response
```

## 数据流

### 文件上传流程

```
1. Client uploads file
   POST /api/threads/{thread_id}/uploads
   Content-Type: multipart/form-data

2. Gateway receives file
   - Validates file
   - Stores in .deer-flow/threads/{thread_id}/user-data/uploads/
   - If document: converts to Markdown via markitdown

3. Returns response
   {
     "files": [{
       "filename": "doc.pdf",
       "path": ".deer-flow/.../uploads/doc.pdf",
       "virtual_path": "/mnt/user-data/uploads/doc.pdf",
       "artifact_url": "/api/threads/.../artifacts/mnt/.../doc.pdf"
     }]
   }

4. Next agent run
   - UploadsMiddleware lists files
   - Injects file list into messages
   - Agent can access via virtual_path
```

### Thread 清理流程

```
1. Client deletes conversation via the LangGraph-compatible Gateway route
   DELETE /api/langgraph/threads/{thread_id}

2. Web UI follows up with Gateway cleanup
   DELETE /api/threads/{thread_id}

3. Gateway removes local DeerFlow-managed files
   - Deletes .deer-flow/threads/{thread_id}/ recursively
   - Missing directories are treated as a no-op
   - Invalid thread IDs are rejected before filesystem access
```

### 配置重载

```
1. Client updates MCP config
   PUT /api/mcp/config

2. Gateway writes extensions_config.json
   - Updates mcpServers section
   - File mtime changes

3. MCP Manager detects change
   - get_cached_mcp_tools() checks mtime
   - If changed: reinitializes MCP client
   - Loads updated server configurations

4. Next agent run uses new tools
```

## 安全性考量

### Sandbox 隔离

- Agent 代码在 sandbox 边界内执行
- Local sandbox：直接执行（仅用于开发）
- Docker sandbox：容器隔离（推荐用于生产环境）
- 文件操作中会防止路径遍历

### API 安全

- Thread 隔离：每个 thread 都有单独的数据目录
- 文件校验：上传内容会检查路径安全性
- 环境变量解析：敏感信息不会存储在配置中

### MCP 安全

- 每个 MCP server 都在独立进程中运行
- 环境变量在运行时解析
- 各 server 可独立启用/禁用

## 性能考量

### 缓存

- MCP 工具会缓存，并通过文件 mtime 失效
- 配置只加载一次，在文件变化时重新加载
- Skills 在启动时解析一次，并缓存在内存中

### 流式传输

- 使用 SSE 进行实时响应流式传输
- 减少首个 token 的等待时间
- 让长时间操作具备进度可见性

### 上下文管理

- Summarization middleware 会在接近上限时压缩上下文
- 支持可配置触发器：tokens、messages 或 fraction
- 在摘要旧消息的同时保留最近消息
