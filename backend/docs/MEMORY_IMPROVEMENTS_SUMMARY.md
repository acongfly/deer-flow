# Memory 系统改进 - 摘要

## 同步说明（2026-03-10）

本摘要已与 `main` 分支实现保持同步。
TF-IDF/上下文感知检索**仍处于计划中**，尚未合并。

## 已实现

- 在 memory 注入中使用 `tiktoken` 进行精确 token 计数。
- 将事实注入到 `<memory>` prompt 内容中。
- 按置信度排序事实，并受 `max_injection_tokens` 限制。

## 计划中（尚未合并）

- 基于最近对话上下文的 TF-IDF 余弦相似度召回。
- 为 `format_memory_for_injection` 增加 `current_context` 参数。
- 加权排序（`similarity` + `confidence`）。
- 在运行时接入提取/注入流程，以实现上下文感知的事实选择。

## 为什么需要这次同步

早期文档将 TF-IDF 行为描述为已经实现，这与 `main` 中的代码不一致。
这个不匹配问题记录在 issue `#1059` 中。

## 当前 API 形态

```python
def format_memory_for_injection(memory_data: dict[str, Any], max_tokens: int = 2000) -> str:
```

当前 `main` 中还没有 `current_context` 参数。

## 验证指引

- 实现位置：`packages/harness/deerflow/agents/memory/prompt.py`
- Prompt 组装：`packages/harness/deerflow/agents/lead_agent/prompt.py`
- 回归测试：`backend/tests/test_memory_prompt_injection.py`
