# task 工具改进

## 概述

task 工具已经过改进，以消除低效的 LLM 轮询。此前在使用后台任务时，LLM 必须反复调用 `task_status` 来轮询是否完成，从而产生不必要的 API 请求。

## 已做变更

### 1. 移除 `run_in_background` 参数

`task` 工具中的 `run_in_background` 参数已被移除。现在所有 subagent 任务默认都以异步方式运行，但工具会自动处理完成流程。

**之前：**
```python
# LLM had to manage polling
task_id = task(
    subagent_type="bash",
    prompt="Run tests",
    description="Run tests",
    run_in_background=True
)
# Then LLM had to poll repeatedly:
while True:
    status = task_status(task_id)
    if completed:
        break
```

**之后：**
```python
# Tool blocks until complete, polling happens in backend
result = task(
    subagent_type="bash",
    prompt="Run tests",
    description="Run tests"
)
# Result is available immediately after the call returns
```

### 2. 后端轮询

现在 `task_tool` 会：
- 以异步方式启动 subagent 任务
- 在后端轮询完成状态（每 2 秒一次）
- 在工具调用完成前持续阻塞
- 直接返回最终结果

这意味着：
- ✅ LLM 只需发起**一次**工具调用
- ✅ 不再有低效的 LLM 轮询请求
- ✅ 由后端统一处理所有状态检查
- ✅ 提供超时保护（最长 5 分钟）

### 3. 从 LLM 工具中移除 `task_status`

`task_status_tool` 不再暴露给 LLM。它仍然保留在代码库中，供未来内部/调试用途使用，但 LLM 无法再调用它。

### 4. 更新文档

- 更新了 `prompt.py` 中的 `SUBAGENT_SECTION`，移除了所有与后台任务和轮询相关的描述
- 简化了使用示例
- 明确说明该工具会自动等待任务完成

## 实现细节

### 轮询逻辑

位于 `packages/harness/deerflow/tools/builtins/task_tool.py`：

```python
# Start background execution
task_id = executor.execute_async(prompt)

# Poll for task completion in backend
while True:
    result = get_background_task_result(task_id)

    # Check if task completed or failed
    if result.status == SubagentStatus.COMPLETED:
        return f"[Subagent: {subagent_type}]\n\n{result.result}"
    elif result.status == SubagentStatus.FAILED:
        return f"[Subagent: {subagent_type}] Task failed: {result.error}"

    # Wait before next poll
    time.sleep(2)

    # Timeout protection (5 minutes)
    if poll_count > 150:
        return "Task timed out after 5 minutes"
```

### 执行超时

除轮询超时外，subagent 执行现在也具备内置超时机制：

**配置**（`packages/harness/deerflow/subagents/config.py`）：
```python
@dataclass
class SubagentConfig:
    # ...
    timeout_seconds: int = 300  # 5 minutes default
```

**线程池架构**：

为避免嵌套线程池和资源浪费，我们使用两个专用线程池：

1. **调度池**（`_scheduler_pool`）：
   - 最大 worker 数：4
   - 用途：编排后台任务执行
   - 运行负责管理任务生命周期的 `run_task()` 函数

2. **执行池**（`_execution_pool`）：
   - 最大 worker 数：8（更大，以避免阻塞）
   - 用途：真正执行 subagent，并支持超时
   - 运行调用 agent 的 `execute()` 方法

**工作方式**：
```python
# In execute_async():
_scheduler_pool.submit(run_task)  # Submit orchestration task

# In run_task():
future = _execution_pool.submit(self.execute, task)  # Submit execution
exec_result = future.result(timeout=timeout_seconds)  # Wait with timeout
```

**收益**：
- ✅ 关注点清晰分离（调度 vs 执行）
- ✅ 没有嵌套线程池
- ✅ 在正确层级强制执行超时
- ✅ 更高的资源利用率

**双层超时保护**：
1. **执行超时**：subagent 本身执行拥有 5 分钟超时（可在 SubagentConfig 中配置）
2. **轮询超时**：工具轮询拥有 5 分钟超时（30 次轮询 × 10 秒）

这样即使 subagent 执行卡住，系统也不会无限等待。

### 收益

1. **降低 API 成本**：不再需要反复发起 LLM 轮询请求
2. **更简单的 UX**：LLM 无需再管理轮询逻辑
3. **更好的可靠性**：由后端统一且一致地处理所有状态检查
4. **超时保护**：双层超时机制可防止无限等待（执行 + 轮询）

## 测试

要验证这些改动是否正常工作：

1. 启动一个耗时几秒的 subagent 任务
2. 验证工具调用会阻塞直到任务完成
3. 验证结果会被直接返回
4. 验证不会发生任何 `task_status` 调用

示例测试场景：
```python
# This should block for ~10 seconds then return result
result = task(
    subagent_type="bash",
    prompt="sleep 10 && echo 'Done'",
    description="Test task"
)
# result should contain "Done"
```

## 迁移说明

对于此前使用 `run_in_background=True` 的用户/代码：
- 只需移除该参数
- 删除所有轮询逻辑
- 工具会自动等待任务完成

无需进行其他修改——API 仍保持向后兼容（除了已删除的参数）。
