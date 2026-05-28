# DeerFlow Sandbox（沙箱）与 Agent 关系分析沉淀

> 目标：沉淀 DeerFlow 仓库中 sandbox 的使用时机、能力边界、调用链，以及它与 tools/subagents/gateway/memory/MCP 的关系，便于后续快速查阅。

## 一、问题范围与结论速览

- **不是所有 agent 运行都会真正初始化 sandbox**。默认是 `lazy_init=True`，只有调用到 sandbox 相关工具（bash、文件操作等）才会 acquire。  
  参考：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/middleware.py:35-42, 63-66, 79-82`
- sandbox 是 DeerFlow 的“受控执行层”，核心通过 `Sandbox` 抽象 + `SandboxProvider` 实现切换（Local / AIO）。  
  参考：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/sandbox.py:6-113`、`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/sandbox_provider.py:9-75`
- lead agent 负责编排，subagent 负责隔离上下文执行；是否触发 sandbox 取决于工具调用，不取决于“是否创建了 agent”。

---

## 二、核心代码与配置位置（职责边界）

### 1) Sandbox 抽象与 Provider 入口

1. `Sandbox` 抽象接口：
   - 路径：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/sandbox.py`
   - 关键方法：`execute_command`、`read_file`、`download_file`、`list_dir`、`write_file`、`glob`、`grep`、`update_file`（`19-112` 行）
   - 职责：定义“执行与文件系统能力契约”，不关心底层是本地还是容器。

2. `SandboxProvider` 抽象与默认实例：
   - 路径：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/sandbox_provider.py`
   - 关键点：
     - acquire/get/release 抽象（`16-50` 行）
     - `get_sandbox_provider()` 根据 `config.sandbox.use` 反射创建 provider（`60-74` 行）
   - 职责：生命周期管理与实现切换。

### 2) Sandbox 中间件

- 路径：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/middleware.py`
- 关键点：
  - 默认 `lazy_init=True`（`35-42` 行）
  - lazy 模式下 `before_agent` 跳过 sandbox 获取（`63-66` 行）
  - 非 lazy 时可在 before_agent 获取（`68-75`, `85-92` 行）
- 职责：把 sandbox 生命周期挂到 agent 运行时状态（state/context）中，而不是直接执行命令。

### 3) Sandbox 工具包装层（真正触发入口）

- 路径：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/tools.py`
- 核心：
  - `ensure_sandbox_initialized` / async 版本负责 lazy acquire（`1094-1150`, `1153-1193` 行）
  - 对外工具：`bash`, `ls`, `glob`, `grep`, `read_file`, `write_file`, `str_replace`（`1328-1805` 行）
- 职责：工具参数校验、安全边界、防越权路径、输出截断、调用 sandbox API。

### 4) 两类具体实现

#### A. Local（本地）
- `LocalSandbox`: `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/local/local_sandbox.py`
  - 本地 shell 执行：`execute_command`（`311-357` 行）
  - 路径映射与反向映射（`111-183`, `220-283` 行）
  - 文件读写与权限（`370-477` 行）
- `LocalSandboxProvider`: `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`
  - 按 thread 生成/缓存 sandbox（`219-265` 行）
  - thread 映射 `/mnt/user-data/*` 与 `/mnt/acp-workspace`（`172-217` 行）
  - `uses_thread_data_mounts=True`（`65` 行）

#### B. AIO（容器/远程）
- `AioSandbox`: `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox.py`
  - 通过 agent_sandbox HTTP 客户端执行命令与文件操作（`39`, `61-92`, `93-286` 行）
- `AioSandboxProvider`: `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`
  - backend 选择：local container / remote provisioner（`174-195` 行）
  - acquire/release/warm pool/idle cleanup（`550-871` 行）
- backend 抽象：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/community/aio_sandbox/backend.py:68-145`
- local backend：`.../local_backend.py:172-260`
- remote backend：`.../remote_backend.py:32-99`

### 5) 配置位置

- 配置模型：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/config/sandbox_config.py:12-83`
- 示例配置：`/tmp/workspace/acongfly/deer-flow/config.example.yaml`
  - 工具绑定到 sandbox tools（`470-501` 行）
  - 默认 local provider（`600-606` 行）
  - AIO provider 示例（`621-669` 行）

---

## 三、从 agent 创建/运行到 sandbox 初始化的典型调用链

### 1) run 入口到 agent 工厂

1. Gateway `start_run` 触发后台执行：
   - `/tmp/workspace/acongfly/deer-flow/backend/app/gateway/services.py:265-363`
2. `run_agent` 组装 runtime/context 并调用 agent_factory：
   - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/runtime/runs/worker.py:124-137, 212-257`
3. `agent_factory` 指向 `make_lead_agent`：
   - `langgraph.json` 映射：`/tmp/workspace/acongfly/deer-flow/backend/langgraph.json:8-10`
   - 工厂实现：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/agents/lead_agent/agent.py:378-494`

### 2) middleware 装配

- 子系统公共链中包含：`ThreadDataMiddleware -> (Uploads) -> SandboxMiddleware`  
  参考：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py:82-91`

### 3) 两条路径分歧（关键）

#### 路径 A：仅聊天/推理（不触发工具）
- `SandboxMiddleware` 因 lazy 模式不 acquire。  
  参考：`/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/middleware.py:63-66`
- 结果：run 中可能存在 sandbox middleware，但没有真实 sandbox 实例创建。

#### 路径 B：需要执行命令/文件操作（触发工具）
- 工具内调用 `ensure_sandbox_initialized(runtime)`：  
  `.../sandbox/tools.py:1094-1150`
- 若 state 中无 sandbox_id：
  - 取 thread_id（context/configurable）
  - provider.acquire(thread_id)
  - 回填 `runtime.state["sandbox"] = {"sandbox_id": ...}`  
  参考：`.../sandbox/tools.py:1130-1142`
- 之后工具调用 `sandbox.execute_command/read_file/write_file...`。

---

## 四、sandbox 提供的能力（以及安全边界）

## 1) 能力列表

- 命令执行：`execute_command`
- 文件读/写/更新/下载：`read_file/write_file/update_file/download_file`
- 目录列举：`list_dir`
- 搜索：`glob/grep`
- 并发文件写保护：`str_replace` 通过 file lock 串行（按 `(sandbox.id, path)`）
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/file_operation_lock.py:13-27`

## 2) 路径与隔离

- 虚拟路径前缀：`/mnt/user-data`  
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/config/paths.py:8-10`
- ThreadDataMiddleware 提供每线程 workspace/uploads/outputs 物理目录：
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/agents/middlewares/thread_data_middleware.py:24-35, 62-66, 113-117`

## 3) 安全边界（工具层）

- 本地路径访问校验：`validate_local_tool_path`（限制到 user-data/skills/acp-workspace/custom mounts）  
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/tools.py:624-676`
- user-data 路径防穿越：
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/tools.py:706-715`
- 本地 bash 命令路径审计：
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/tools.py:930-969`
- bash 高风险审计中间件：
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/agents/middlewares/sandbox_audit_middleware.py:197-212, 335-363`
- host bash 默认禁用（Local provider 下）：
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/sandbox/security.py:10-20, 35-45`

---

## 五、sandbox 与 tools / subagents / gateway / memory / MCP 的关系

### 1) sandbox 与 tools

- tool 是触发者：只有工具调用才会触发 sandbox acquire。  
  - `.../sandbox/tools.py:1094-1150`
- sandbox 是执行底座：工具把模型意图映射为受控执行操作。

### 2) sandbox 与 subagents

- `task_tool` 从父 runtime 取 `sandbox_state/thread_data/thread_id`，传入 `SubagentExecutor`：
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/tools/builtins/task_tool.py:251-263, 301-312`
- Subagent 初始 state 继承 sandbox/thread_data：
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/subagents/executor.py:441-447`
- 结论：subagent 可以复用父线程上下文与沙箱状态，但是否“实际用到 sandbox”仍取决于它调用了哪些工具。

### 3) sandbox 与 gateway

- gateway 不直接执行 sandbox 命令；它负责 run 生命周期与流式事件。  
  - `/tmp/workspace/acongfly/deer-flow/backend/app/gateway/services.py:265-370`
- 真实执行发生在 runtime worker 里的 agent graph。  
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/runtime/runs/worker.py:307-335`

### 4) sandbox 与 memory

- `MemoryMiddleware` 在 `after_agent` 做消息过滤并入队，不依赖 sandbox API：  
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/agents/middlewares/memory_middleware.py:29-36, 53-110`
- 结论：memory 是“会话知识沉淀层”，不是执行环境层。

### 5) sandbox 与 MCP

- MCP 工具通过 `get_available_tools` 并入工具集，不等于 sandbox。  
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/tools/tools.py:119-130`
- MCP 有自己的缓存/会话池机制：
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/mcp/cache.py:56-80, 82-130`
- 结论：MCP 与 sandbox 是并行的“工具来源/执行路径”；某些 MCP server 可能内部再做远程执行，但这与 DeerFlow sandbox 生命周期是两层概念。

---

## 六、“创建智能体的作用是什么”

## 1) 为什么不是写死流程

- `make_lead_agent` 会根据运行时配置动态装配：模型、middleware、tool groups、skills、subagent 开关。  
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/agents/lead_agent/agent.py:390-494`
- `get_available_tools` 动态加载内置工具、MCP 工具、ACP 工具，并做去重与安全门控。  
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/tools/tools.py:44-221`

## 2) lead agent 与 subagent 分工

- lead agent：任务编排、拆解、选择工具、综合输出。
- subagent：针对子任务在独立上下文中执行（可并行），结果回传 lead 汇总。  
  - `task_tool`：`.../tools/builtins/task_tool.py:186-229, 314-374`  
  - `SubagentExecutor`：`.../subagents/executor.py:269-343, 449-540`
- prompt 层也明确了“复杂任务优先分解并并行委托”的策略：
  - `/tmp/workspace/acongfly/deer-flow/backend/packages/harness/deerflow/agents/lead_agent/prompt.py:235-306`

---

## 七、面向初学者的通俗解释

## 1) 什么时候会进入沙箱？

当模型要“动手做事”（跑命令、读写文件、grep/glob）时，就会进入沙箱；如果只是聊天回答，通常不会初始化沙箱。

## 2) 为什么需要沙箱？

因为模型是自动执行的，必须把它限制在安全边界里（可访问目录、可执行命令、路径防穿越、风险审计），防止误操作主机环境。

## 3) 没有沙箱会怎样？

模型能力越强，误伤风险越高：可能读写不该访问的路径、执行危险命令。DeerFlow 通过默认禁用 Local host bash、路径白名单、审计中间件来降低风险。

---

## 八、简化流程图（文本版）

```text
HTTP /runs -> start_run -> run_agent
  -> agent_factory(make_lead_agent) -> create_agent(tools + middlewares)
      middlewares: ThreadData -> (Uploads) -> Sandbox(lazy) -> ...
      |
      +-- 如果仅聊天/推理（无工具调用）
      |      -> SandboxMiddleware lazy skip（通常不 acquire）
      |
      +-- 如果调用 sandbox 工具（bash/read_file/write_file/ls/glob/grep/str_replace）
             -> ensure_sandbox_initialized(runtime)
             -> get_sandbox_provider() (from config.sandbox.use)
             -> provider.acquire(thread_id) & state 写入 sandbox_id
             -> LocalSandbox 或 AioSandbox 执行
             -> after_agent 阶段 release（AIO 可进 warm pool；Local 常复用缓存）
```

---

## 九、补充：与本次沉淀相关的运行校验记录

在当前执行环境中，尝试执行仓库 lint/test 的结果如下（命令可用性受环境限制）：

- backend `make lint`：失败（`uvx` 不存在）
- backend `make test`：失败（`uv` 不存在）
- frontend `pnpm lint`：失败（`pnpm` 不存在）
- frontend `pnpm test`：失败（`pnpm` 不存在）

说明：本次仅新增文档沉淀，不涉及代码逻辑修改。

---

## 十、可快速复用的检索关键词

- `SandboxMiddleware lazy_init ensure_sandbox_initialized`
- `LocalSandboxProvider / AioSandboxProvider`
- `task_tool SubagentExecutor sandbox_state`
- `get_available_tools mcp_tools`
- `validate_local_tool_path validate_local_bash_command_paths`

