---
name: claude-to-deerflow
description: "通过 DeerFlow 的 HTTP API 与 DeerFlow AI agent 平台交互。当用户想要向 DeerFlow 发送消息或问题以进行研究/分析、启动 DeerFlow 对话线程、检查 DeerFlow 状态或健康情况、列出 DeerFlow 中可用的 models/skills/agents、管理 DeerFlow memory、向 DeerFlow 线程上传文件，或将复杂研究任务委托给 DeerFlow 时使用此 skill。当用户提到 deerflow、deer flow，或希望运行 DeerFlow 可处理的深度研究任务时，也应使用。"
---

# DeerFlow Skill

通过其 HTTP API 与正在运行的 DeerFlow 实例通信。DeerFlow 是一个基于 LangGraph 的 AI agent 平台，可编排 sub-agents 来执行研究、代码执行、网页浏览等任务。

## 架构

DeerFlow 在 Nginx 反向代理之后暴露两个 API 面：

| 服务 | 直连端口 | 通过代理 | 用途 |
|----------------|-------------|----------------------------------|----------------------------------|
| Gateway API | 8001 | `$DEERFLOW_GATEWAY_URL` | REST 端点与嵌入式 agent runtime |
| LangGraph-compatible API | 8001 | `$DEERFLOW_LANGGRAPH_URL` | Agent threads、runs、流式输出 |

## 环境变量

所有 URL 都可通过环境变量配置。**发起任何请求之前，先读取这些环境变量。**

| 变量 | 默认值 | 说明 |
|-------------------------|------------------------------------------|------------------------------------|
| `DEERFLOW_URL` | `http://localhost:2026` | 统一代理基础 URL |
| `DEERFLOW_GATEWAY_URL` | `${DEERFLOW_URL}` | Gateway API 基础地址（models、skills、memory、uploads） |
| `DEERFLOW_LANGGRAPH_URL`| `${DEERFLOW_URL}/api/langgraph` | LangGraph API 基础地址（threads、runs） |

在进行 curl 调用时，始终按如下方式解析 URL：

```bash
# Resolve base URLs from env (do this FIRST before any API call)
DEERFLOW_URL="${DEERFLOW_URL:-http://localhost:2026}"
DEERFLOW_GATEWAY_URL="${DEERFLOW_GATEWAY_URL:-$DEERFLOW_URL}"
DEERFLOW_LANGGRAPH_URL="${DEERFLOW_LANGGRAPH_URL:-$DEERFLOW_URL/api/langgraph}"
```

## 可用操作

### 1. 健康检查

验证 DeerFlow 是否正在运行：

```bash
curl -s "$DEERFLOW_GATEWAY_URL/health"
```

### 2. 发送消息（流式）

这是主要操作。它会创建一个 thread 并流式返回 agent 的响应。

**步骤 1：创建 thread**

```bash
curl -s -X POST "$DEERFLOW_LANGGRAPH_URL/threads" \
  -H "Content-Type: application/json" \
  -d '{}'
```

响应：`{"thread_id": "<uuid>", ...}`

**步骤 2：流式运行**

```bash
curl -s -N -X POST "$DEERFLOW_LANGGRAPH_URL/threads/<thread_id>/runs/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "lead_agent",
    "input": {
      "messages": [
        {
          "type": "human",
          "content": [{"type": "text", "text": "YOUR MESSAGE HERE"}]
        }
      ]
    },
    "stream_mode": ["values", "messages-tuple"],
    "stream_subgraphs": true,
    "config": {
      "recursion_limit": 1000
    },
    "context": {
      "thinking_enabled": true,
      "is_plan_mode": true,
      "subagent_enabled": true,
      "thread_id": "<thread_id>"
    }
  }'
```

响应为 SSE 流。每个事件的格式如下：
```
event: <event_type>
data: <json_data>
```

关键事件类型：
- `metadata` —— 运行元数据，包括 `run_id`
- `values` —— 包含 `messages` 数组的完整状态快照
- `messages-tuple` —— 增量消息更新（AI 文本片段、tool 调用、tool 结果）
- `end` —— 流结束

**上下文模式**（通过 `context` 设置）：
- Flash mode：`thinking_enabled: false, is_plan_mode: false, subagent_enabled: false`
- Standard mode：`thinking_enabled: true, is_plan_mode: false, subagent_enabled: false`
- Pro mode：`thinking_enabled: true, is_plan_mode: true, subagent_enabled: false`
- Ultra mode：`thinking_enabled: true, is_plan_mode: true, subagent_enabled: true`

### 3. 继续对话

要发送后续消息，复用步骤 2 中相同的 `thread_id`，并使用新消息再次 POST 一个 run。

### 4. 列出 Models

```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/models"
```

返回：`{"models": [{"name": "...", "provider": "...", ...}, ...]}`

### 5. 列出 Skills

```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/skills"
```

返回：`{"skills": [{"name": "...", "enabled": true, ...}, ...]}`

### 6. 启用/禁用 Skill

```bash
curl -s -X PUT "$DEERFLOW_GATEWAY_URL/api/skills/<skill_name>" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### 7. 列出 Agents

```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/agents"
```

返回：`{"agents": [{"name": "...", ...}, ...]}`

### 8. 获取 Memory

```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/memory"
```

返回用户上下文、事实以及对话历史摘要。

### 9. 向 Thread 上传文件

```bash
curl -s -X POST "$DEERFLOW_GATEWAY_URL/api/threads/<thread_id>/uploads" \
  -F "files=@/path/to/file.pdf"
```

支持 PDF、PPTX、XLSX、DOCX —— 会自动转换为 Markdown。

### 10. 列出已上传文件

```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/threads/<thread_id>/uploads/list"
```

### 11. 获取 Thread 历史

```bash
curl -s "$DEERFLOW_LANGGRAPH_URL/threads/<thread_id>/history"
```

### 12. 列出 Threads

```bash
curl -s -X POST "$DEERFLOW_LANGGRAPH_URL/threads/search" \
  -H "Content-Type: application/json" \
  -d '{"limit": 20, "sort_by": "updated_at", "sort_order": "desc"}'
```

## 使用脚本

如需发送消息并收集完整响应，请使用辅助脚本：

```bash
bash /path/to/skills/claude-to-deerflow/scripts/chat.sh "Your question here"
```

具体实现见 `scripts/chat.sh`。该脚本会：
1. 检查健康状态
2. 创建 thread
3. 流式运行并收集最终 AI 响应
4. 打印结果

## 解析 SSE 输出

流返回的是 SSE 事件。要从 `values` 事件中提取最终 AI 响应：
- 找到最后一个 `event: values` 代码块
- 解析其 `data` JSON
- `messages` 数组包含全部消息；最后一个 `type: "ai"` 的消息就是响应
- 该消息的 `content` 字段即 AI 的文本回复

## 错误处理

- 如果健康检查失败，说明 DeerFlow 未运行。应告知用户需要先启动它。
- 如果流返回 error 事件，提取并展示错误信息。
- 常见问题：端口未开放、服务仍在启动中、配置错误。

## 提示

- 对于快速问题，使用 flash mode（最快，无规划）。
- 对于研究任务，使用 pro 或 ultra mode（启用规划和 sub-agents）。
- 你可以先上传文件，再在消息中引用它们。
- Thread IDs 会持久存在——你以后可以回到同一段对话。
