# Memory 系统改进

本文档用于跟踪 memory 注入行为及路线图状态。

## 当前状态（截至 2026-03-10）

已在 `main` 中实现：
- 在 `format_memory_for_injection` 中通过 `tiktoken` 进行精确 token 计数。
- 将事实注入到 prompt 的 memory 上下文中。
- 按置信度降序对事实排序。
- 注入过程遵守 `max_injection_tokens` 的预算限制。

计划中 / 尚未合并：
- 基于 TF-IDF 相似度的事实检索。
- 用于上下文感知评分的 `current_context` 输入。
- 可配置的相似度/置信度权重（`similarity_weight`、`confidence_weight`）。
- 在每次模型调用前，为上下文感知检索接入 middleware/runtime。

## 当前行为

当前函数签名：

```python
def format_memory_for_injection(memory_data: dict[str, Any], max_tokens: int = 2000) -> str:
```

当前注入格式：
- `User Context` 部分来自 `user.*.summary`
- `History` 部分来自 `history.*.summary`
- `Facts` 部分来自 `facts[]`，按置信度排序，并在达到 token 预算前持续追加

Token 计数：
- 可用时使用 `tiktoken`（`cl100k_base`）
- 若 tokenizer 导入失败，则回退为 `len(text) // 4`

## 已知缺口

此前版本的本文档将 TF-IDF/上下文感知检索描述成仿佛已经上线。
这与 `main` 分支的实际情况不符，并造成了困惑。

相关 issue：`#1059`

## 路线图（计划中）

计划中的评分策略：

```text
final_score = (similarity * 0.6) + (confidence * 0.4)
```

计划中的集成方式：
1. 从筛选后的 user/final-assistant 轮次中提取最近的对话上下文。
2. 计算每条事实与当前上下文之间的 TF-IDF 余弦相似度。
3. 按加权分数排序，并在 token 预算内注入。
4. 若上下文不可用，则回退为仅按置信度排序。

## 验证

当前回归覆盖包括：
- memory 注入输出中包含 facts
- 按置信度排序
- 在 token 预算限制下的 facts 注入

测试文件：
- `backend/tests/test_memory_prompt_injection.py`
