# 使用 TodoList Middleware 的 Plan Mode

本文档介绍如何在 DeerFlow 2.0 中启用并使用带有 TodoList middleware 的 Plan Mode 功能。

## 概述

Plan Mode 会为 agent 添加一个 TodoList middleware，它提供 `write_todos` 工具，帮助 agent：
- 将复杂任务拆解为更小、更易管理的步骤
- 在工作推进过程中跟踪进度
- 让用户清楚了解当前正在执行的内容

TodoList middleware 基于 LangChain 的 `TodoListMiddleware` 构建。

## 配置

### 启用 Plan Mode

Plan mode 通过 `RunnableConfig` 的 `configurable` 部分中的 `is_plan_mode` 参数进行**运行时配置**控制。这使你可以按请求动态启用或禁用 plan mode。

```python
from langchain_core.runnables import RunnableConfig
from deerflow.agents.lead_agent.agent import make_lead_agent

# Enable plan mode via runtime configuration
config = RunnableConfig(
    configurable={
        "thread_id": "example-thread",
        "thinking_enabled": True,
        "is_plan_mode": True,  # Enable plan mode
    }
)

# Create agent with plan mode enabled
agent = make_lead_agent(config)
```

### 配置选项

- **is_plan_mode** (bool)：是否启用带有 TodoList middleware 的 plan mode。默认值：`False`
  - 通过 `config.get("configurable", {}).get("is_plan_mode", False)` 传递
  - 可为每次 agent 调用动态设置
  - 无需全局配置

## 默认行为

当使用默认设置启用 plan mode 时，agent 将可以访问一个 `write_todos` 工具，其行为如下：

### 何时使用 TodoList

agent 会在以下情况下使用 todo list：
1. 复杂的多步骤任务（3 个及以上独立步骤）
2. 需要仔细规划的非简单任务
3. 用户明确要求提供 todo list
4. 用户一次提供了多个任务

### 何时**不**使用 TodoList

agent 会在以下情况下跳过 todo list：
1. 单一且直接的任务
2. 简单任务（少于 3 个步骤）
3. 纯对话型或信息查询型请求

### 任务状态

- **pending**：任务尚未开始
- **in_progress**：当前正在处理（可以有多个并行任务）
- **completed**：任务已成功完成

## 使用示例

### 基本用法

```python
from langchain_core.runnables import RunnableConfig
from deerflow.agents.lead_agent.agent import make_lead_agent

# Create agent with plan mode ENABLED
config_with_plan_mode = RunnableConfig(
    configurable={
        "thread_id": "example-thread",
        "thinking_enabled": True,
        "is_plan_mode": True,  # TodoList middleware will be added
    }
)
agent_with_todos = make_lead_agent(config_with_plan_mode)

# Create agent with plan mode DISABLED (default)
config_without_plan_mode = RunnableConfig(
    configurable={
        "thread_id": "another-thread",
        "thinking_enabled": True,
        "is_plan_mode": False,  # No TodoList middleware
    }
)
agent_without_todos = make_lead_agent(config_without_plan_mode)
```

### 按请求动态控制 Plan Mode

你可以为不同的对话或任务动态启用/禁用 plan mode：

```python
from langchain_core.runnables import RunnableConfig
from deerflow.agents.lead_agent.agent import make_lead_agent

def create_agent_for_task(task_complexity: str):
    """Create agent with plan mode based on task complexity."""
    is_complex = task_complexity in ["high", "very_high"]

    config = RunnableConfig(
        configurable={
            "thread_id": f"task-{task_complexity}",
            "thinking_enabled": True,
            "is_plan_mode": is_complex,  # Enable only for complex tasks
        }
    )

    return make_lead_agent(config)

# Simple task - no TodoList needed
simple_agent = create_agent_for_task("low")

# Complex task - TodoList enabled for better tracking
complex_agent = create_agent_for_task("high")
```

## 工作原理

1. 当调用 `make_lead_agent(config)` 时，它会从 `config.configurable` 中提取 `is_plan_mode`
2. 配置会被传递给 `_build_middlewares(config)`
3. `_build_middlewares()` 读取 `is_plan_mode` 并调用 `_create_todo_list_middleware(is_plan_mode)`
4. 如果 `is_plan_mode=True`，就会创建一个 `TodoListMiddleware` 实例并将其加入 middleware 链
5. 该 middleware 会自动向 agent 的工具集添加一个 `write_todos` 工具
6. agent 可以在执行过程中使用该工具管理任务
7. middleware 负责处理 todo list 状态并将其提供给 agent

## 架构

```
make_lead_agent(config)
  │
  ├─> Extracts: is_plan_mode = config.configurable.get("is_plan_mode", False)
  │
  └─> _build_middlewares(config)
        │
        ├─> ThreadDataMiddleware
        ├─> SandboxMiddleware
        ├─> SummarizationMiddleware (if enabled via global config)
        ├─> TodoListMiddleware (if is_plan_mode=True) ← NEW
        ├─> TitleMiddleware
        └─> ClarificationMiddleware
```

## 实现细节

### Agent 模块
- **位置**：`packages/harness/deerflow/agents/lead_agent/agent.py`
- **函数**：`_create_todo_list_middleware(is_plan_mode: bool)` - 在启用 plan mode 时创建 TodoListMiddleware
- **函数**：`_build_middlewares(config: RunnableConfig)` - 根据运行时配置构建 middleware 链
- **函数**：`make_lead_agent(config: RunnableConfig)` - 创建带有适当 middlewares 的 agent

### 运行时配置
Plan mode 通过 `RunnableConfig.configurable` 中的 `is_plan_mode` 参数进行控制：
```python
config = RunnableConfig(
    configurable={
        "is_plan_mode": True,  # Enable plan mode
        # ... other configurable options
    }
)
```

## 主要优势

1. **动态控制**：无需全局状态，即可按请求启用/禁用 plan mode
2. **灵活性**：不同对话可以拥有不同的 plan mode 设置
3. **简洁性**：无需全局配置管理
4. **上下文感知**：是否启用 plan mode 可以依据任务复杂度、用户偏好等因素决定

## 自定义提示词

DeerFlow 为 TodoListMiddleware 使用了自定义的 `system_prompt` 和 `tool_description`，以匹配 DeerFlow 整体的提示词风格：

### System Prompt 的特性
- 使用 XML 标签（`<todo_list_system>`）以保持与 DeerFlow 主提示词结构一致
- 强调 CRITICAL 规则和最佳实践
- 清晰区分“何时使用”与“何时不使用”指南
- 聚焦实时更新和即时任务完成

### Tool Description 的特性
- 提供包含示例的详细使用场景
- 强调不要将其用于简单任务
- 清晰定义任务状态（pending、in_progress、completed）
- 完整的最佳实践部分
- 任务完成要求可防止过早标记完成

这些自定义提示词定义在 `/Users/hetao/workspace/deer-flow/backend/packages/harness/deerflow/agents/lead_agent/agent.py:57` 中的 `_create_todo_list_middleware()`。

## 说明

- TodoList middleware 使用 LangChain 内置的 `TodoListMiddleware`，并配有**自定义的 DeerFlow 风格提示词**
- Plan mode **默认禁用**（`is_plan_mode=False`），以保持向后兼容
- 该 middleware 位于 `ClarificationMiddleware` 之前，以便在 clarification 流程中管理 todo
- 自定义提示词强调与 DeerFlow 主 system prompt 相同的原则（清晰、面向行动、关键规则）
