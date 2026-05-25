# API 参考

本文档提供 DeerFlow backend API 的完整参考。

## 概述

DeerFlow backend 暴露两组 API：

1. **兼容 LangGraph 的 API** - Agent 交互、线程与流式传输（`/api/langgraph/*`）
2. **Gateway API** - Models、MCP、skills、上传与 artifacts（`/api/*`）

所有 API 都通过位于 2026 端口的 Nginx 反向代理访问。

## 兼容 LangGraph 的 API

基础 URL：`/api/langgraph`

对外提供的兼容 LangGraph 的 API 遵循 LangGraph SDK 约定。在统一的 nginx 部署中，Gateway 接管 `/api/langgraph/*`，并将这些路径转换到其原生 `/api/*` 的 run、thread 与 streaming 路由。

### Threads

#### 创建 Thread

```http
POST /api/langgraph/threads
Content-Type: application/json
```

**请求体：**
```json
{
  "metadata": {}
}
```

**响应：**
```json
{
  "thread_id": "abc123",
  "created_at": "2024-01-15T10:30:00Z",
  "metadata": {}
}
```

#### 获取 Thread 状态

```http
GET /api/langgraph/threads/{thread_id}/state
```

**响应：**
```json
{
  "values": {
    "messages": [...],
    "sandbox": {...},
    "artifacts": [...],
    "thread_data": {...},
    "title": "Conversation Title"
  },
  "next": [],
  "config": {...}
}
```

### Runs

#### 创建 Run

执行带输入的 agent。

```http
POST /api/langgraph/threads/{thread_id}/runs
Content-Type: application/json
```

**请求体：**
```json
{
  "input": {
    "messages": [
      {
        "role": "user",
        "content": "Hello, can you help me?"
      }
    ]
  },
  "config": {
    "recursion_limit": 100,
    "configurable": {
      "model_name": "gpt-4",
      "thinking_enabled": false,
      "is_plan_mode": false
    }
  },
  "stream_mode": ["values", "messages-tuple", "custom"]
}
```

**流模式兼容性：**
- 可使用：`values`、`messages-tuple`、`custom`、`updates`、`events`、`debug`、`tasks`、`checkpoints`
- 不要使用：`tools`（在当前 `langgraph-api` 中已废弃/无效，并会触发 schema 校验错误）

**递归限制：**

`config.recursion_limit` 用于限制 LangGraph 在一次 run 中最多执行多少个 graph step。统一 Gateway 路径会在 `build_run_config` 中默认设置为 `100`（见 `backend/app/gateway/services.py`），这是对 plan mode 或大量 subagent run 更安全的起点。客户端仍可在请求体中显式设置 `recursion_limit`；如果你运行的是深层嵌套的 subagent graph，可适当提高该值。

**可配置选项：**
- `model_name`（string）：覆盖默认模型
- `thinking_enabled`（boolean）：为支持的模型启用扩展 thinking
- `is_plan_mode`（boolean）：启用 TodoList middleware 以跟踪任务

**响应：**Server-Sent Events (SSE) 流

```
event: values
data: {"messages": [...], "title": "..."}

event: messages
data: {"content": "Hello! I'd be happy to help.", "role": "assistant"}

event: end
data: {}
```

#### 获取 Run 历史

```http
GET /api/langgraph/threads/{thread_id}/runs
```

**响应：**
```json
{
  "runs": [
    {
      "run_id": "run123",
      "status": "success",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

#### 流式 Run

实时流式返回响应。

```http
POST /api/langgraph/threads/{thread_id}/runs/stream
Content-Type: application/json
```

请求体与“创建 Run”相同。返回 SSE 流。

---

## Gateway API 接口

基础 URL：`/api`

### Models

#### 列出 Models

获取配置中的所有可用 LLM 模型。

```http
GET /api/models
```

**响应：**
```json
{
  "models": [
    {
      "name": "gpt-4",
      "display_name": "GPT-4",
      "supports_thinking": false,
      "supports_vision": true
    },
    {
      "name": "claude-3-opus",
      "display_name": "Claude 3 Opus",
      "supports_thinking": false,
      "supports_vision": true
    },
    {
      "name": "deepseek-v3",
      "display_name": "DeepSeek V3",
      "supports_thinking": true,
      "supports_vision": false
    }
  ]
}
```

#### 获取 Model 详情

```http
GET /api/models/{model_name}
```

**响应：**
```json
{
  "name": "gpt-4",
  "display_name": "GPT-4",
  "model": "gpt-4",
  "max_tokens": 4096,
  "supports_thinking": false,
  "supports_vision": true
}
```

### MCP 配置

#### 获取 MCP 配置

获取当前 MCP server 配置。

```http
GET /api/mcp/config
```

**响应：**
```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "***"
      },
      "description": "GitHub operations"
    }
  }
}
```

#### 更新 MCP 配置

更新 MCP server 配置。

```http
PUT /api/mcp/config
Content-Type: application/json
```

**请求体：**
```json
{
  "mcpServers": {
    "github": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "$GITHUB_TOKEN"
      },
      "description": "GitHub operations"
    }
  }
}
```

**响应：**
```json
{
  "success": true,
  "message": "MCP configuration updated"
}
```

### Skills

#### 列出 Skills

获取所有可用 skills。

```http
GET /api/skills
```

**响应：**
```json
{
  "skills": [
    {
      "name": "pdf-processing",
      "display_name": "PDF Processing",
      "description": "Handle PDF documents efficiently",
      "enabled": true,
      "license": "MIT",
      "path": "public/pdf-processing"
    },
    {
      "name": "frontend-design",
      "display_name": "Frontend Design",
      "description": "Design and build frontend interfaces",
      "enabled": false,
      "license": "MIT",
      "path": "public/frontend-design"
    }
  ]
}
```

#### 获取 Skill 详情

```http
GET /api/skills/{skill_name}
```

**响应：**
```json
{
  "name": "pdf-processing",
  "display_name": "PDF Processing",
  "description": "Handle PDF documents efficiently",
  "enabled": true,
  "license": "MIT",
  "path": "public/pdf-processing",
  "allowed_tools": ["read_file", "write_file", "bash"],
  "content": "# PDF Processing\n\nInstructions for the agent..."
}
```

#### 启用 Skill

```http
POST /api/skills/{skill_name}/enable
```

**响应：**
```json
{
  "success": true,
  "message": "Skill 'pdf-processing' enabled"
}
```

#### 禁用 Skill

```http
POST /api/skills/{skill_name}/disable
```

**响应：**
```json
{
  "success": true,
  "message": "Skill 'pdf-processing' disabled"
}
```

#### 安装 Skill

从 `.skill` 文件安装 skill。

```http
POST /api/skills/install
Content-Type: multipart/form-data
```

**请求体：**
- `file`：要安装的 `.skill` 文件

**响应：**
```json
{
  "success": true,
  "message": "Skill 'my-skill' installed successfully",
  "skill": {
    "name": "my-skill",
    "display_name": "My Skill",
    "path": "custom/my-skill"
  }
}
```

### 文件上传

#### 上传文件

向某个 thread 上传一个或多个文件。

```http
POST /api/threads/{thread_id}/uploads
Content-Type: multipart/form-data
```

**请求体：**
- `files`：一个或多个待上传文件

**响应：**
```json
{
  "success": true,
  "files": [
    {
      "filename": "document.pdf",
      "size": 1234567,
      "path": ".deer-flow/threads/abc123/user-data/uploads/document.pdf",
      "virtual_path": "/mnt/user-data/uploads/document.pdf",
      "artifact_url": "/api/threads/abc123/artifacts/mnt/user-data/uploads/document.pdf",
      "markdown_file": "document.md",
      "markdown_path": ".deer-flow/threads/abc123/user-data/uploads/document.md",
      "markdown_virtual_path": "/mnt/user-data/uploads/document.md",
      "markdown_artifact_url": "/api/threads/abc123/artifacts/mnt/user-data/uploads/document.md"
    }
  ],
  "message": "Successfully uploaded 1 file(s)"
}
```

**支持的文档格式**（会自动转换为 Markdown）：
- PDF（`.pdf`）
- PowerPoint（`.ppt`、`.pptx`）
- Excel（`.xls`、`.xlsx`）
- Word（`.doc`、`.docx`）

#### 列出已上传文件

```http
GET /api/threads/{thread_id}/uploads/list
```

**响应：**
```json
{
  "files": [
    {
      "filename": "document.pdf",
      "size": 1234567,
      "path": ".deer-flow/threads/abc123/user-data/uploads/document.pdf",
      "virtual_path": "/mnt/user-data/uploads/document.pdf",
      "artifact_url": "/api/threads/abc123/artifacts/mnt/user-data/uploads/document.pdf",
      "extension": ".pdf",
      "modified": 1705997600.0
    }
  ],
  "count": 1
}
```

#### 删除文件

```http
DELETE /api/threads/{thread_id}/uploads/{filename}
```

**响应：**
```json
{
  "success": true,
  "message": "Deleted document.pdf"
}
```

### Thread 清理

在 LangGraph thread 本身已被删除后，移除 `.deer-flow/threads/{thread_id}` 下由 DeerFlow 管理的本地 thread 文件。

```http
DELETE /api/threads/{thread_id}
```

**响应：**
```json
{
  "success": true,
  "message": "Deleted local thread data for abc123"
}
```

**错误行为：**
- 无效 thread ID 返回 `422`
- `500` 返回通用响应 `{"detail": "Failed to delete local thread data."}`，完整异常细节仅保留在服务器日志中

### Artifacts 产物

#### 获取 Artifact

下载或查看 agent 生成的 artifact。

```http
GET /api/threads/{thread_id}/artifacts/{path}
```

**路径示例：**
- `/api/threads/abc123/artifacts/mnt/user-data/outputs/result.txt`
- `/api/threads/abc123/artifacts/mnt/user-data/uploads/document.pdf`

**查询参数：**
- `download`（boolean）：若为 `true`，则通过 Content-Disposition header 强制下载

**响应：**带有适当 Content-Type 的文件内容

---

## 错误响应

所有 API 都以统一格式返回错误：

```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP 状态码：**
- `400` - Bad Request：无效输入
- `404` - Not Found：资源不存在
- `422` - Validation Error：请求校验失败
- `500` - Internal Server Error：服务器端错误

---

## 身份验证

DeerFlow 会对所有非公开 HTTP 路由强制执行身份验证。公开路由仅限于 health/docs 元数据以及以下公开 auth 端点：

- `POST /api/v1/auth/initialize`：当还不存在 admin 时，创建第一个 admin 账户。
- `POST /api/v1/auth/login/local`：使用 email/password 登录，并设置 HttpOnly `access_token` cookie。
- `POST /api/v1/auth/register`：创建普通 `user` 账户，并设置 session cookie。
- `POST /api/v1/auth/logout`：清除 session cookie。
- `GET /api/v1/auth/setup-status`：报告是否仍需要创建第一个 admin。

需要已认证身份的 auth 端点包括：

- `GET /api/v1/auth/me`：返回当前用户。
- `POST /api/v1/auth/change-password`：修改密码，可在初始化期间同时修改 email，递增 `token_version`，并重新签发 cookie。

受保护且会更改状态的请求还需要 CSRF 双重提交 token：将 `csrf_token` cookie 的值作为 `X-CSRF-Token` header 发送。login/register/initialize/logout 属于引导型 auth 端点：它们不要求双重提交 token，但仍会拒绝恶意浏览器 `Origin` header。

用户隔离是根据已认证的用户上下文强制执行的：

- Thread 元数据通过 `threads_meta.user_id` 进行作用域隔离；search/read/write/delete API 只暴露当前用户的 threads。
- Thread 文件位于 `{base_dir}/users/{user_id}/threads/{thread_id}/user-data/`，并在 sandbox 内映射为 `/mnt/user-data/`。
- Memory 和自定义 agents 存储在 `{base_dir}/users/{user_id}/...` 下。

注意：MCP 的出站连接仍可对已配置的 HTTP/SSE MCP servers 使用 OAuth；这与 DeerFlow API 身份验证是彼此独立的。

---

## 速率限制

默认未实现速率限制。对于生产部署，请在 Nginx 中配置速率限制：

```nginx
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    proxy_pass http://backend;
}
```

---

## 流式支持

Gateway 的兼容 LangGraph API 通过 Server-Sent Events (SSE) 流式传输 run 事件：

```http
POST /api/langgraph/threads/{thread_id}/runs/stream
Accept: text/event-stream
```

---

## SDK 用法

### Python（LangGraph SDK）

```python
from langgraph_sdk import get_client

client = get_client(url="http://localhost:2026/api/langgraph")

# Create thread
thread = await client.threads.create()

# Run agent
async for event in client.runs.stream(
    thread["thread_id"],
    "lead_agent",
    input={"messages": [{"role": "user", "content": "Hello"}]},
    config={"configurable": {"model_name": "gpt-4"}},
    stream_mode=["values", "messages-tuple", "custom"],
):
    print(event)
```

### JavaScript/TypeScript

```typescript
// Using fetch for Gateway API
const response = await fetch('/api/models');
const data = await response.json();
console.log(data.models);

// Create a run and stream SSE events
const streamResponse = await fetch(`/api/langgraph/threads/${threadId}/runs/stream`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    Accept: "text/event-stream",
  },
  body: JSON.stringify({
    input: { messages: [{ role: "user", content: "Hello" }] },
    stream_mode: ["values", "messages-tuple", "custom"],
  }),
});

const reader = streamResponse.body?.getReader();
// Decode and parse SSE frames from reader in your client code.
```

### cURL 示例

```bash
# List models
curl http://localhost:2026/api/models

# Get MCP config
curl http://localhost:2026/api/mcp/config

# Upload file
curl -X POST http://localhost:2026/api/threads/abc123/uploads \
  -F "files=@document.pdf"

# Enable skill
curl -X POST http://localhost:2026/api/skills/pdf-processing/enable

# Create thread and run agent
curl -X POST http://localhost:2026/api/langgraph/threads \
  -H "Content-Type: application/json" \
  -d '{}'

curl -X POST http://localhost:2026/api/langgraph/threads/abc123/runs \
  -H "Content-Type: application/json" \
  -d '{
    "input": {"messages": [{"role": "user", "content": "Hello"}]},
    "config": {
      "recursion_limit": 100,
      "configurable": {"model_name": "gpt-4"}
    }
  }'
```

> 统一 Gateway 路径默认会将 `config.recursion_limit` 设为 100，适用于
> plan mode 和大量 subagent 的 run。客户端仍可显式设置
> `config.recursion_limit`——详见[创建 Run](#创建-run)部分。
