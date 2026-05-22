# 06 — 核心模块：Subagent 子代理系统

> 原始资料：[`backend/CLAUDE.md`](../../backend/CLAUDE.md) · [`backend/docs/ARCHITECTURE.md`](../../backend/docs/ARCHITECTURE.md)  
> 源码位置：`backend/packages/harness/deerflow/subagents/`

---

## 1. 总体结构

```
deerflow/subagents/
├── __init__.py
├── config.py        # 子代理配置（SubagentConfig）
├── executor.py      # SubagentExecutor：后台执行引擎
├── registry.py      # 子代理注册表
├── token_collector.py # Token 使用量收集
└── builtins/
    ├── __init__.py
    ├── general_purpose.py  # general-purpose 子代理（全工具，除 task）
    └── bash_agent.py       # bash 子代理（命令行专家）
```

---

## 2. 并发模型

```
Lead Agent
    │
    ▼ task() 工具调用
SubagentLimitMiddleware（最多 3 个并发，超出截断）
    │
    ▼
SubagentExecutor
    ├── _scheduler_pool（3 workers）← 调度层
    └── _execution_pool（3 workers）← 执行层

每个子代理：
  - 后台线程独立执行
  - 轮询间隔：5 秒
  - 超时：15 分钟
  - SSE 事件流回传到 Lead Agent
```

**并发上限**：`MAX_CONCURRENT_SUBAGENTS = 3`，由 `SubagentLimitMiddleware` 在 `after_model` 阶段截断超出的 `task` 工具调用。

---

## 3. 内置子代理

### general-purpose（通用子代理）

- 加载全部工具，**除了 `task` 工具**（防止无限递归委托）
- 适合复杂的多步骤任务，如代码生成、数据分析、文档撰写

### bash（命令行专家）

- 专注于 bash 命令执行
- 适合文件操作、脚本运行、系统管理任务

---

## 4. task 工具 — 委托入口

**注册**：当 `subagent_enabled=True` 时，`task` 工具加入 Lead Agent 的工具集。

**工具签名**：
```python
task(
    description: str,  # 任务的简短描述（用于显示）
    prompt: str,       # 详细的任务指令（会发给子代理）
    subagent_type: str # 子代理类型：general-purpose | bash
) -> str
```

**执行流程**：
```
1. Lead Agent 调用 task() 工具
2. SubagentLimitMiddleware 检查并发上限
3. SubagentExecutor 在后台线程中启动子代理
4. 每隔 5s 轮询子代理状态
5. 发出 SSE 事件：
   - task_started   → 子代理开始运行
   - task_running   → 中间状态更新（5s 间隔）
   - task_completed → 成功完成，携带结果
   - task_failed    → 执行失败，携带错误信息
   - task_timed_out → 超过 15 分钟
6. 结果作为 ToolMessage 返回给 Lead Agent
```

---

## 5. 子代理注册表

**文件**：`backend/packages/harness/deerflow/subagents/registry.py`

```python
# 查看所有注册的子代理
from deerflow.subagents.registry import get_subagent_registry

registry = get_subagent_registry()
available_agents = registry.list()  # ["general-purpose", "bash"]
```

---

## 6. Token 使用量追踪

**文件**：`backend/packages/harness/deerflow/subagents/token_collector.py`

- 子代理的 Token 使用量通过 `tool_call_id` 缓存
- 仅在 `TokenUsageMiddleware` 启用时激活
- 由消息位置（非消息 id）合并回 Lead Agent 的 AIMessage

---

## 7. 配置

在 `config.yaml` 中启用子代理：

```yaml
subagents:
  enabled: true
  max_concurrent: 3        # 最大并发子代理数
  timeout_minutes: 15      # 单个子代理超时时间
  
  agents:
    - name: general-purpose
      enabled: true
    - name: bash
      enabled: true
```

在运行时通过 `config.configurable` 传入：
```python
config = {"configurable": {"subagent_enabled": True}}
```

---

## 8. 开发步骤：注册自定义子代理

### 步骤 1：创建子代理工厂函数

```python
# backend/packages/harness/deerflow/subagents/builtins/my_agent.py
from langchain_core.runnables import RunnableConfig
from deerflow.agents.lead_agent.agent import make_lead_agent  # 复用 lead agent 构建器

def make_my_custom_agent(config: RunnableConfig):
    """
    创建我的自定义子代理。
    可以限制工具集、调整系统提示词等。
    """
    # 使用受限工具集
    custom_config = {
        **config,
        "configurable": {
            **config.get("configurable", {}),
            "subagent_enabled": False,  # 子代理不能再委托子代理
            "tool_groups": ["sandbox", "my_custom_tools"],
        }
    }
    return make_lead_agent(custom_config)
```

### 步骤 2：注册到子代理注册表

```python
# backend/packages/harness/deerflow/subagents/registry.py
from deerflow.subagents.builtins.my_agent import make_my_custom_agent

_BUILTIN_SUBAGENTS = {
    "general-purpose": make_general_purpose_agent,
    "bash": make_bash_agent,
    "my-custom-agent": make_my_custom_agent,  # 添加这行
}
```

### 步骤 3：在 config.yaml 中启用

```yaml
subagents:
  enabled: true
  agents:
    - name: my-custom-agent
      enabled: true
      description: "我的自定义子代理，专门用于..."
```

---

## 9. 开发 Demo：使用 task 工具委托任务

以下是 Lead Agent 在对话中委托子代理的示例（Agent 自动调用，无需手动触发）：

```
用户：帮我分析仓库里的 Python 代码质量，然后生成一份报告

Agent 内部流程：
  1. 决定拆分任务
  2. 调用 task(
       description="分析 Python 代码质量",
       prompt="请运行 ruff check . 和 pytest，收集所有警告和错误，统计每类问题的数量",
       subagent_type="bash"
     )
  3. 后台 bash 子代理执行命令
  4. task_completed 事件带回执行结果
  5. Lead Agent 基于结果生成报告
```

---

## 10. 注意事项

- **防递归**：`general-purpose` 子代理**不包含** `task` 工具，无法再委托子代理
- **隔离**：每个子代理有独立的消息历史和工具执行上下文
- **状态共享**：子代理通过沙箱文件系统与 Lead Agent 共享文件（同一线程目录）
- **并发限制**：超出 `MAX_CONCURRENT_SUBAGENTS` 的 task 调用会被 `SubagentLimitMiddleware` 截断，Agent 会收到提示重试
