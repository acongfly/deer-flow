# 03 — 核心模块：Agent 系统

> 原始资料：[`backend/CLAUDE.md`](../../backend/CLAUDE.md) · [`backend/docs/ARCHITECTURE.md`](../../backend/docs/ARCHITECTURE.md)  
> 源码位置：`backend/packages/harness/deerflow/agents/`

---

## 1. 总体结构

```
deerflow/agents/
├── __init__.py          # 导出 make_lead_agent
├── factory.py           # 辅助工厂函数
├── features.py          # 特性开关
├── thread_state.py      # ThreadState 状态模式定义
├── lead_agent/
│   ├── agent.py         # ← 核心入口：make_lead_agent()
│   └── prompt.py        # 系统提示词模板生成
├── memory/
│   ├── extractor.py     # 记忆提取逻辑
│   ├── queue.py         # 异步记忆更新队列
│   └── prompts.py       # 记忆相关提示词
└── middlewares/
    ├── __init__.py
    ├── tool_error_handling_middleware.py  # 组装 build_lead_runtime_middlewares
    └── （其他中间件模块）
```

---

## 2. 入口：`make_lead_agent()`

**文件**：`backend/packages/harness/deerflow/agents/lead_agent/agent.py`

```python
def make_lead_agent(config: RunnableConfig) -> CompiledGraph:
    """
    注册在 langgraph.json，是 LangGraph 图的唯一入口。
    根据 config.configurable 动态选择模型、工具集和中间件。
    """
```

**主要执行流程**：

1. 从 `config.configurable` 读取运行时参数（见下方表格）
2. 调用 `create_chat_model()` 实例化 LLM
3. 调用 `get_available_tools()` 组装工具集
4. 调用 `apply_prompt_template()` 生成系统提示词（含 Skills、Memory、Subagent 指令）
5. 调用 `_build_middlewares()` 构建中间件链
6. 返回已编译的 LangGraph `CompiledGraph`

**运行时配置参数**（通过 `config.configurable` 传入）：

| 参数 | 类型 | 说明 |
|------|------|------|
| `thinking_enabled` | bool | 开启模型的扩展思维（Extended Thinking）|
| `model_name` | str | 指定使用哪个 LLM |
| `is_plan_mode` | bool | 开启 TodoList 中间件（任务追踪）|
| `subagent_enabled` | bool | 开启子代理任务委托工具 |

---

## 3. ThreadState — 状态模式

**文件**：`backend/packages/harness/deerflow/agents/thread_state.py`

ThreadState 继承 LangGraph 的 `AgentState`，增加了 DeerFlow 特有的字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `sandbox` | Sandbox \| None | 当前线程的沙箱实例 |
| `thread_data` | ThreadData | 线程目录、workspace 路径等 |
| `title` | str | 对话标题（由 TitleMiddleware 自动生成）|
| `artifacts` | list[Artifact] | 输出文件元数据，使用 `merge_artifacts` 去重 |
| `todos` | list[Todo] | 待办事项（plan_mode 下使用）|
| `uploaded_files` | list[UploadedFile] | 已上传的文件列表 |
| `viewed_images` | set[str] | 已被模型查看的图片路径，使用 `merge_viewed_images` 合并/清除 |

---

## 4. 中间件链（18 层，严格顺序执行）

中间件在 `build_lead_runtime_middlewares()` 和 `_build_middlewares()` 中按固定顺序组装，**顺序不可随意变更**。

| 序号 | 中间件 | 阶段 | 说明 |
|------|--------|------|------|
| 1 | **ThreadDataMiddleware** | before_model | 为每个线程创建隔离目录（`users/{user_id}/threads/{thread_id}/user-data/{workspace,uploads,outputs}`），通过 `get_effective_user_id()` 解析用户身份（无 auth 模式回退到 `"default"`） |
| 2 | **UploadsMiddleware** | before_model | 追踪并注入新上传文件到对话上下文 |
| 3 | **SandboxMiddleware** | before_model | 获取沙箱实例，将 `sandbox_id` 写入 state |
| 4 | **DanglingToolCallMiddleware** | before_model | 为缺少响应的 tool_call 注入占位 ToolMessage（处理用户中断的情况）|
| 5 | **LLMErrorHandlingMiddleware** | after_model | 将模型/提供商调用失败规范化为可恢复的 assistant 错误 |
| 6 | **GuardrailMiddleware** | before_tool | 工具调用前授权检查（可选，需 `guardrails.enabled`）|
| 7 | **SandboxAuditMiddleware** | before_tool | 记录沙箱 shell/文件操作的安全审计日志 |
| 8 | **ToolErrorHandlingMiddleware** | after_tool | 将工具异常转换为 error ToolMessage，让运行继续而不是崩溃 |
| 9 | **SummarizationMiddleware** | before_model | 接近 Token 上限时压缩上下文（可选，需配置开启）|
| 10 | **TodoListMiddleware** | before/after | 任务追踪，注入 `write_todos` 工具（可选，plan_mode 下）|
| 11 | **TokenUsageMiddleware** | after_model | 记录 Token 使用量指标（可选）|
| 12 | **TitleMiddleware** | after_model | 首次完整对话后自动生成线程标题 |
| 13 | **MemoryMiddleware** | after_model | 将对话加入异步记忆更新队列（过滤为用户+最终 AI 响应）|
| 14 | **ViewImageMiddleware** | before_model | 条件性注入 base64 图片数据（需模型支持视觉）|
| 15 | **DeferredToolFilterMiddleware** | before_model | 对模型隐藏 deferred 工具 schema，直到工具搜索启用 |
| 16 | **SubagentLimitMiddleware** | after_model | 截断超出 `MAX_CONCURRENT_SUBAGENTS`（默认 3）的 task 工具调用 |
| 17 | **LoopDetectionMiddleware** | after_model | 检测重复工具调用循环，硬停止并强制输出文本答案 |
| 18 | **ClarificationMiddleware** | after_tool | 拦截 `ask_clarification` 工具调用，通过 `Command(goto=END)` 中断（必须最后）|

### 中间件执行钩子

每个中间件可以选择性地实现以下钩子：

```python
class BaseMiddleware:
    async def before_model(self, state: ThreadState) -> ThreadState: ...
    async def after_model(self, state: ThreadState, response: AIMessage) -> AIMessage: ...
    async def before_tool(self, state: ThreadState, tool_calls: list) -> list: ...
    async def after_tool(self, state: ThreadState, results: list) -> list: ...
```

---

## 5. 系统提示词生成

**文件**：`backend/packages/harness/deerflow/agents/lead_agent/prompt.py`

`apply_prompt_template()` 会动态生成系统提示词，包含：

1. **基础指令**：Agent 的角色定义和行为规范
2. **Skills 注入**：将已启用的技能说明注入提示词
3. **Memory 注入**：从 `memory.json` 读取并注入用户记忆（受 Token 预算限制）
4. **Subagent 指令**：如果 `subagent_enabled=True`，注入子代理使用指南

---

## 6. 开发步骤：添加新中间件

1. 在 `backend/packages/harness/deerflow/agents/middlewares/` 下新建文件，例如 `my_middleware.py`
2. 继承 `BaseMiddleware`，实现需要的钩子
3. 在 `build_lead_runtime_middlewares()` 或 `_build_middlewares()` 中按正确位置插入
4. 在 `config.yaml` 中（如需要）添加开关
5. 在 `backend/tests/` 中添加对应测试

**示例**：
```python
# backend/packages/harness/deerflow/agents/middlewares/my_middleware.py
from deerflow.agents.middlewares.base import BaseMiddleware
from deerflow.agents.thread_state import ThreadState

class MyMiddleware(BaseMiddleware):
    async def before_model(self, state: ThreadState) -> ThreadState:
        # 在每次 LLM 调用前执行自定义逻辑
        return state

    async def after_tool(self, state: ThreadState, results: list) -> list:
        # 在工具执行后执行自定义逻辑
        return results
```

---

## 7. 开发 Demo：调用内嵌 Python 客户端

**文件**：`backend/packages/harness/deerflow/client.py`

```python
from deerflow.client import DeerFlowClient

client = DeerFlowClient()

# 同步流式调用
for event in client.stream("帮我分析一下最近的 AI 趋势"):
    if event.type == "message":
        print(event.data.content, end="", flush=True)
    elif event.type == "tool_call":
        print(f"\n[工具调用] {event.data.name}: {event.data.args}")
```

> **注意**：`DeerFlowClient` 是同步 API，内部直接调用 `agent.stream()`，无需 HTTP，适合 Jupyter notebook、脚本和集成测试。
