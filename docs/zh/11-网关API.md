# 11 — 网关 API

> 原始资料：[`backend/CLAUDE.md`](../../backend/CLAUDE.md) · [`backend/docs/ARCHITECTURE.md`](../../backend/docs/ARCHITECTURE.md) · [`backend/docs/API.md`](../../backend/docs/API.md)  
> 源码位置：`backend/app/gateway/`

---

## 1. 总体结构

```
app/gateway/
├── app.py               # FastAPI 应用实例 + lifespan（启动/关闭）
├── config.py            # Gateway 配置（CORS、端口等）
├── auth/                # 认证模块（见认证文档）
├── auth_middleware.py   # 认证中间件
├── authz.py             # 授权逻辑
├── csrf_middleware.py   # CSRF 保护
├── deps.py              # FastAPI 依赖注入
├── internal_auth.py     # 内部服务认证（IM 渠道使用）
├── langgraph_auth.py    # LangGraph 兼容认证
├── path_utils.py        # 路径工具
├── utils.py             # 通用工具
└── services.py          # 应用服务（RunManager、RunStore 等）
├── routers/             # FastAPI 路由模块
│   ├── models.py        # /api/models
│   ├── mcp.py           # /api/mcp
│   ├── skills.py        # /api/skills
│   ├── memory.py        # /api/memory
│   ├── uploads.py       # /api/threads/{id}/uploads
│   ├── threads.py       # /api/threads/{id}（线程目录清理）
│   ├── artifacts.py     # /api/threads/{id}/artifacts
│   ├── suggestions.py   # /api/threads/{id}/suggestions
│   ├── thread_runs.py   # /api/threads/{id}/runs（LangGraph-compatible）
│   ├── runs.py          # /api/runs（无状态运行）
│   ├── feedback.py      # /api/threads/{id}/runs/{rid}/feedback
│   ├── agents.py        # /api/agents（自定义 Agent）
│   └── channels.py      # /api/channels
```

---

## 2. FastAPI 应用启动

**文件**：`backend/app/gateway/app.py`

```python
# 健康检查（无需认证）
GET /health → {"status": "ok"}

# API 文档（生产环境可关闭）
GET /docs
GET /redoc
GET /openapi.json
```

关闭文档：设置环境变量 `GATEWAY_ENABLE_DOCS=false`

---

## 3. 完整路由表

### 模型管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/models/` | 列出所有可用模型 |
| GET | `/api/models/{name}` | 获取模型详情 |

### MCP 配置

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/mcp/config` | 获取 MCP 配置 |
| PUT | `/api/mcp/config` | 更新 MCP 配置（保存到 extensions_config.json）|

### Skills 管理

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/skills/` | 列出所有技能 |
| GET | `/api/skills/{name}` | 获取技能详情 |
| PUT | `/api/skills/{name}` | 更新技能启用状态 |
| POST | `/api/skills/install` | 安装 .skill 包 |

### 记忆

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/memory/` | 获取记忆数据 |
| POST | `/api/memory/reload` | 强制重新加载记忆 |
| GET | `/api/memory/config` | 获取记忆配置 |
| GET | `/api/memory/status` | 记忆配置 + 数据综合状态 |

### 文件上传

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/threads/{id}/uploads/` | 上传文件（自动转换 PDF/PPT/Excel/Word）|
| GET | `/api/threads/{id}/uploads/list` | 列出上传文件 |
| DELETE | `/api/threads/{id}/uploads/{filename}` | 删除上传文件 |

### 线程管理

| 方法 | 路径 | 说明 |
|------|------|------|
| DELETE | `/api/threads/{id}` | 删除线程（清理 DeerFlow 管理的文件数据）|

### Artifacts（输出文件）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/threads/{id}/artifacts/{path}` | 提供输出文件下载（活跃内容类型强制为下载附件，降低 XSS 风险）|

### 建议问题

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/threads/{id}/suggestions/` | 生成对话后续建议问题 |

### 线程运行（LangGraph-compatible）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/threads/{id}/runs/` | 创建后台运行 |
| POST | `/api/threads/{id}/runs/stream` | 创建运行 + SSE 流式输出 |
| POST | `/api/threads/{id}/runs/wait` | 创建运行 + 阻塞等待 |
| GET | `/api/threads/{id}/runs/` | 列出运行历史 |
| GET | `/api/threads/{id}/runs/{rid}` | 获取运行详情 |
| POST | `/api/threads/{id}/runs/{rid}/cancel` | 取消运行 |
| GET | `/api/threads/{id}/runs/{rid}/join` | 加入 SSE 流 |
| GET | `/api/threads/{id}/runs/{rid}/messages` | 分页获取消息 `{data, has_more}` |
| GET | `/api/threads/{id}/runs/{rid}/events` | 完整事件流 |
| GET | `/api/threads/{id}/messages` | 线程消息（含反馈）|
| GET | `/api/threads/{id}/token-usage` | 汇总 Token 使用量 |

### 反馈

| 方法 | 路径 | 说明 |
|------|------|------|
| PUT | `/api/threads/{id}/runs/{rid}/feedback/` | 更新/插入反馈 |
| DELETE | `/api/threads/{id}/runs/{rid}/feedback/` | 删除用户反馈 |
| POST | `/api/threads/{id}/runs/{rid}/feedback/` | 创建反馈 |
| GET | `/api/threads/{id}/runs/{rid}/feedback/` | 列出反馈 |
| GET | `/api/threads/{id}/runs/{rid}/feedback/stats` | 汇总反馈统计 |
| DELETE | `/api/threads/{id}/runs/{rid}/feedback/{fid}` | 删除特定反馈 |

### 无状态运行

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/runs/stream` | 无状态运行 + SSE 流 |
| POST | `/api/runs/wait` | 无状态运行 + 阻塞 |
| GET | `/api/runs/{rid}/messages` | 按 run_id 分页获取消息（cursor: `after_seq`/`before_seq`）|
| GET | `/api/runs/{rid}/feedback` | 按 run_id 列出反馈 |

---

## 4. RunManager / RunStore 合约

- `RunManager.get()` 是异步方法，调用方必须 `await`
- 配置持久化 `RunStore` 后，`get()` 和 `list_by_thread()` 会从存储中加载历史运行
- 内存中的记录优先于存储记录（同一 `run_id`），保持任务、中止和流控制状态
- `cancel()` 和 `create_or_reject(..., multitask_strategy="interrupt"|"rollback")` 通过 `RunStore.update_status()` 持久化中断状态
- 仅存储中的历史运行：可读，但当前 worker 没有对应的任务/控制状态，取消 API 会返回 409

---

## 5. CORS 配置

默认情况下，通过 nginx 在 2026 端口进入时是同源请求，无需额外 CORS 配置。

如果需要跨域访问（Split-origin 或端口转发）：

```bash
export GATEWAY_CORS_ORIGINS="https://my-frontend.example.com,http://localhost:3001"
```

`CORSMiddleware` 和 `CSRFMiddleware` 都读取这个变量，保持对齐。

---

## 6. SSE 流式输出接入示例

```javascript
// 前端 JavaScript
const response = await fetch('/api/threads/{threadId}/runs/stream', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    assistant_id: 'agent',
    input: {messages: [{role: 'user', content: '你好'}]},
    config: {configurable: {model_name: 'gpt-4o'}}
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const {done, value} = await reader.read();
  if (done) break;
  
  const lines = decoder.decode(value).split('\n');
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));
      console.log(data);
    }
  }
}
```

---

## 7. 开发时的调试技巧

```bash
# 查看 API 文档（开发时默认开启）
open http://localhost:8001/docs

# 健康检查
curl http://localhost:8001/health

# 查看 Gateway 日志
tail -f logs/gateway.log
```
