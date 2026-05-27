# Event Store 历史记录——Backend 兼容层

> **针对 agentic workers：** 必需的子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans，按任务逐项实现该计划。步骤使用 checkbox（`- [ ]`）语法进行跟踪。

**目标：** 在 thread state/history endpoints 中，用 append-only 的 event store 替代 checkpoint state 作为消息来源，这样 summarization 就不会导致消息丢失。

**架构：** Gateway 的 `get_thread_state` 和 `get_thread_history` endpoints 当前从 `checkpoint.channel_values["messages"]` 读取消息。summarization 之后，这些消息会被替换成一个 synthetic 的 summary-as-human message，所有 summarization 之前的消息都会消失。我们要修改这些 endpoints，使其改为从 RunEventStore 读取消息（append-only，不受 summarization 影响）。每条消息的响应结构保持完全一致，因此 chat 渲染路径无需改动，但 frontend 的 feedback hook 必须对齐为使用同一份完整历史视图（见任务 4）。

**技术栈：** Python（FastAPI、SQLAlchemy）、pytest、TypeScript（React Query）

**范围：** 仅限 Gateway mode（`make dev-pro`）。Standard mode 直接使用 LangGraph Server，不会经过这些 endpoints；因此 summarize bug 在那里依然存在，必须作为单独的后续项跟踪（见本文末尾“Follow-ups”）。

**已落地的前置项：** `backend/packages/harness/deerflow/runtime/journal.py` 现在会在 `on_tool_end` 中解包 `Command(update={'messages':[ToolMessage(...)]})`，因此新运行中使用 state-updating tools（例如 `present_files`）时，会将内部 `ToolMessage` 内容写入 event store，而不是写入 `str(Command(...))`。在该修复之前产生的 legacy 数据，会由新的 helper 做防御性清理（见任务 1 步骤 3 中的 `_sanitize_legacy_command_repr`）。

---

## 真实数据对齐分析

已将真实的 `POST /history` 响应（基于 checkpoint）与 thread `6d30913e-dcd4-41c8-8941-f66c716cf359` 的 `run_events` 表（`docs/resp.json` + `backend/.deer-flow/data/deerflow.db`）进行了对比。完整证据链见 `docs/superpowers/specs/2026-04-11-runjournal-history-evaluation.md`。

| 消息类型 | 对比字段 | 差异 |
|-------------|----------------|------------|
| human_message | 全部字段 | event store 中 `id` 为 `None`，checkpoint 中为 UUID |
| ai_message (tool_call) | 全部字段，6 个重叠字段 | **完全一致**（0 个差异） |
| ai_message (final) | 全部字段 | **完全一致** |
| tool_result (normal) | 全部字段 | 只有 `id` 不同（`None` vs UUID） |
| tool_result（来自 `Command`-returning tool） | content | **legacy 数据存储的是 `str(Command(...))` repr，而不是内部 ToolMessage** —— 新运行已在 `journal.py` 中修复；legacy 行由 helper 清理 |

**`id` 差异的根本原因：** LangGraph 的 checkpoint 会在 graph 执行期间为 HumanMessage 和 ToolMessage 分配 `id`。而 event store 写入发生得更早，此时这些 `id` 仍然是 None。AI message 的 `id` 来自 LLM 响应（`lc_run--*`），因此不受影响。

**`id` 的修复方案：** 对 `id=None` 的消息，在读取时使用 `uuid5(NAMESPACE_URL, f"{thread_id}:{seq}")` 生成确定性的 UUID。要修改的是内容 dict 的**副本**，绝不能改动 live store object。

**在复现 thread 上量化 summarize 的影响：** event_store 中有 16 条消息（7 条 AI + 9 条其他消息）；summarize 后 checkpoint 中只有 12 条（5 条 AI + 7 条其他消息）。AI id 重叠数：7 条中的 5 条——缺失的 2 条 AI 消息都发生在 summarize 之前。

---

## 文件结构

| 文件 | 操作 | 职责 |
|------|--------|----------------|
| `backend/app/gateway/routers/threads.py` | 修改 | 在 `get_thread_state` 和 `get_thread_history` 中，用 event store 消息替换 checkpoint 消息 |
| `backend/tests/test_thread_state_event_store.py` | 新建 | 为修改后的 endpoints 编写测试 |

---

### 任务 1：在 `threads.py` 中添加 `_get_event_store_messages` helper

一个共享 helper，用于从 event store 加载**完整**消息流，为 `id=None` 的消息补上确定性 UUID，并对 `journal.py` 修复前遗留的 `Command(update=...)` repr 做防御性清理。它会对每条 content dict 的副本进行修补，以确保不会修改 live store。

**设计约束（来自评估 §3、§4、§5）：**
- **完整分页**，而不是 `limit=1000`。`RunEventStore.list_messages` 返回的是“最新 N 条记录”——固定 limit 会静默截断更旧的消息。使用 `count_messages()` 来确定请求规模，或通过 `after_seq` cursor 循环分页。
- **修改前先复制。** `MemoryRunEventStore` 返回的是 live dict 引用；JSONL/DB store 可能返回脱离的数据行，但我们不能依赖这一点。补 `id` 之前始终执行 `content = dict(evt["content"])`。
- **Legacy Command 清理。** legacy 数据中会出现 `content["content"] == "Command(update={'artifacts': [...], 'messages': [ToolMessage(content='X', ...)]})"`。用 regex 提取内部 ToolMessage 的内容字符串并替换；如果提取失败，则保持原样不动（即便如此也依然优于现有基于 checkpoint 的回退，因为 summarized thread 上那个回退同样是错误的）。
- **用户上下文。** `DbRunEventStore.list_messages` 通过 `resolve_user_id(AUTO)` 按用户作用域工作，并依赖 `@require_permission` 设置的 auth contextvar。这两个 endpoint 已经都带有该 decorator——请在 helper 的 docstring 中注明这一依赖。

**文件：**
- 修改：`backend/app/gateway/routers/threads.py`
- 测试：`backend/tests/test_thread_state_event_store.py`

- [ ] **步骤 1：编写测试**

创建 `backend/tests/test_thread_state_event_store.py`：

```python
"""Tests for event-store-backed message loading in thread state/history endpoints."""

from __future__ import annotations

import uuid

import pytest

from deerflow.runtime.events.store.memory import MemoryRunEventStore


@pytest.fixture()
def event_store():
    return MemoryRunEventStore()


async def _seed_conversation(event_store: MemoryRunEventStore, thread_id: str = "t1"):
    """Seed a realistic multi-turn conversation matching real checkpoint format."""
    # human_message: id is None (same as real data)
    await event_store.put(
        thread_id=thread_id, run_id="r1",
        event_type="human_message", category="message",
        content={
            "type": "human", "id": None,
            "content": [{"type": "text", "text": "Hello"}],
            "additional_kwargs": {}, "response_metadata": {}, "name": None,
        },
    )
    # ai_tool_call: id is set by LLM
    await event_store.put(
        thread_id=thread_id, run_id="r1",
        event_type="ai_tool_call", category="message",
        content={
            "type": "ai", "id": "lc_run--abc123",
            "content": "",
            "tool_calls": [{"name": "search", "args": {"q": "cats"}, "id": "call_1", "type": "tool_call"}],
            "invalid_tool_calls": [],
            "additional_kwargs": {}, "response_metadata": {}, "name": None,
            "usage_metadata": {"input_tokens": 100, "output_tokens": 50, "total_tokens": 150},
        },
    )
    # tool_result: id is None (same as real data)
    await event_store.put(
        thread_id=thread_id, run_id="r1",
        event_type="tool_result", category="message",
        content={
            "type": "tool", "id": None,
            "content": "Found 10 results",
            "tool_call_id": "call_1", "name": "search",
            "artifact": None, "status": "success",
            "additional_kwargs": {}, "response_metadata": {},
        },
    )
    # ai_message: id is set by LLM
    await event_store.put(
        thread_id=thread_id, run_id="r1",
        event_type="ai_message", category="message",
        content={
            "type": "ai", "id": "lc_run--def456",
            "content": "I found 10 results about cats.",
            "tool_calls": [], "invalid_tool_calls": [],
            "additional_kwargs": {}, "response_metadata": {"finish_reason": "stop"}, "name": None,
            "usage_metadata": {"input_tokens": 200, "output_tokens": 100, "total_tokens": 300},
        },
    )
    # Also add a trace event — should NOT appear
    await event_store.put(
        thread_id=thread_id, run_id="r1",
        event_type="llm_request", category="trace",
        content={"model": "gpt-4"},
    )


class TestGetEventStoreMessages:
    """Verify event store message extraction with id patching."""

    @pytest.mark.asyncio
    async def test_extracts_all_message_types(self, event_store):
        await _seed_conversation(event_store)
        events = await event_store.list_messages("t1", limit=500)
        messages = [evt["content"] for evt in events if isinstance(evt.get("content"), dict) and "type" in evt["content"]]
        assert len(messages) == 4
        assert [m["type"] for m in messages] == ["human", "ai", "tool", "ai"]

    @pytest.mark.asyncio
    async def test_null_ids_get_patched(self, event_store):
        """Messages with id=None should get deterministic UUIDs."""
        await _seed_conversation(event_store)
        events = await event_store.list_messages("t1", limit=500)
        messages = []
        for evt in events:
            content = evt.get("content")
            if isinstance(content, dict) and "type" in content:
                if content.get("id") is None:
                    content["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"t1:{evt['seq']}"))
                messages.append(content)

        # All messages now have an id
        for m in messages:
            assert m["id"] is not None
            assert isinstance(m["id"], str)
            assert len(m["id"]) > 0

        # AI messages keep their original id
        assert messages[1]["id"] == "lc_run--abc123"
        assert messages[3]["id"] == "lc_run--def456"

        # Human and tool messages get deterministic ids (same input = same output)
        human_id_1 = str(uuid.uuid5(uuid.NAMESPACE_URL, "t1:1"))
        assert messages[0]["id"] == human_id_1

    @pytest.mark.asyncio
    async def test_empty_thread(self, event_store):
        events = await event_store.list_messages("nonexistent", limit=500)
        messages = [evt["content"] for evt in events if isinstance(evt.get("content"), dict)]
        assert messages == []

    @pytest.mark.asyncio
    async def test_tool_call_fields_preserved(self, event_store):
        await _seed_conversation(event_store)
        events = await event_store.list_messages("t1", limit=500)
        messages = [evt["content"] for evt in events if isinstance(evt.get("content"), dict) and "type" in evt["content"]]

        # AI tool_call message
        ai_tc = messages[1]
        assert ai_tc["tool_calls"][0]["name"] == "search"
        assert ai_tc["tool_calls"][0]["id"] == "call_1"

        # Tool result
        tool = messages[2]
        assert tool["tool_call_id"] == "call_1"
        assert tool["status"] == "success"
```

- [ ] **步骤 2：运行测试并确认通过**

运行：`cd backend && PYTHONPATH=. uv run pytest tests/test_thread_state_event_store.py -v`

- [ ] **步骤 3：添加 helper function 并修改 `get_thread_history`**

在 `backend/app/gateway/routers/threads.py` 中：

1. 在文件顶部添加 import：
```python
import uuid  # ADD (may already exist, check first)
from app.gateway.deps import get_run_event_store  # ADD
```

2. 添加 helper function（放在 endpoint functions 之前、model 定义之后）：

```python
_LEGACY_CMD_INNER_CONTENT_RE = re.compile(
    r"ToolMessage\(content=(?P<q>['\"])(?P<inner>.*?)(?P=q)",
    re.DOTALL,
)

def _sanitize_legacy_command_repr(content_field: Any) -> Any:
    """Recover the inner ToolMessage text from a legacy ``str(Command(...))`` repr.

    Runs that pre-date the ``on_tool_end`` fix in ``journal.py`` stored
    ``str(Command(update={'messages':[ToolMessage(content='X', ...)]}))`` as the
    tool_result content. New runs store ``'X'`` directly. For old threads, try
    to extract ``'X'`` defensively; return the original string if extraction
    fails (still no worse than the current checkpoint-based fallback, which is
    broken for summarized threads anyway).
    """
    if not isinstance(content_field, str) or not content_field.startswith("Command(update="):
        return content_field
    match = _LEGACY_CMD_INNER_CONTENT_RE.search(content_field)
    return match.group("inner") if match else content_field


async def _get_event_store_messages(request: Request, thread_id: str) -> list[dict] | None:
    """Load messages from the event store, returning None if unavailable.

    The event store is append-only and immune to summarization. Each
    message event's ``content`` field contains a ``model_dump()``'d
    LangChain Message dict that is already JSON-serialisable.

    **Full pagination, not a fixed limit.** ``RunEventStore.list_messages``
    returns the newest ``limit`` records when no cursor is given, which
    silently drops older messages. We call ``count_messages()`` first and
    request that many records. For stores that may return fewer (e.g. filtered
    by user), we also fall back to ``after_seq``-cursor pagination.

    **Copy-on-read.** Each content dict is copied before ``id`` is patched so
    the live store object is never mutated; ``MemoryRunEventStore`` returns
    live references.

    **Legacy Command repr sanitization.** See ``_sanitize_legacy_command_repr``.

    **User context.** ``DbRunEventStore`` is user-scoped by default via
    ``resolve_user_id(AUTO)`` (see ``runtime/user_context.py``). Callers of
    this helper must be inside a request where ``@require_permission`` has
    populated the user contextvar. Both ``get_thread_history`` and
    ``get_thread_state`` satisfy that. Do not call this helper from CLI or
    migration scripts without passing ``user_id=None`` explicitly.

    Returns ``None`` when the event store is not configured or contains no
    messages for this thread, so callers can fall back to checkpoint messages.
    """
    try:
        event_store = get_run_event_store(request)
    except Exception:
        return None

    try:
        total = await event_store.count_messages(thread_id)
    except Exception:
        logger.exception("count_messages failed for thread %s", sanitize_log_param(thread_id))
        return None
    if not total:
        return None

    # Batch by page_size to keep memory bounded for very long threads.
    page_size = 500
    collected: list[dict] = []
    after_seq: int | None = None
    while True:
        page = await event_store.list_messages(thread_id, limit=page_size, after_seq=after_seq)
        if not page:
            break
        collected.extend(page)
        if len(page) < page_size:
            break
        after_seq = page[-1].get("seq")
        if after_seq is None:
            break

    messages: list[dict] = []
    for evt in collected:
        raw = evt.get("content")
        if not isinstance(raw, dict) or "type" not in raw:
            continue
        # Copy to avoid mutating the store-owned dict.
        content = dict(raw)
        if content.get("id") is None:
            content["id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{thread_id}:{evt['seq']}"))
        # Sanitize legacy Command reprs on tool_result messages only.
        if content.get("type") == "tool":
            content["content"] = _sanitize_legacy_command_repr(content.get("content"))
        messages.append(content)
    return messages if messages else None
```

另外，如果文件顶部还没有 `import re`，也请添加。

3. 在 `get_thread_history` 中（大约第 585-590 行），替换 messages 处理部分：

**修改前：**
```python
            # Attach messages from checkpointer only for the latest checkpoint
            if is_latest_checkpoint:
                messages = channel_values.get("messages")
                if messages:
                    values["messages"] = serialize_channel_values({"messages": messages}).get("messages", [])
            is_latest_checkpoint = False
```

**修改后：**
```python
            # Attach messages: prefer event store (immune to summarization),
            # fall back to checkpoint messages when event store is unavailable.
            if is_latest_checkpoint:
                es_messages = await _get_event_store_messages(request, thread_id)
                if es_messages is not None:
                    values["messages"] = es_messages
                else:
                    messages = channel_values.get("messages")
                    if messages:
                        values["messages"] = serialize_channel_values({"messages": messages}).get("messages", [])
            is_latest_checkpoint = False
```

- [ ] **步骤 4：以相同方式修改 `get_thread_state`**

在 `get_thread_state` 中（大约第 443-444 行），替换：

**修改前：**
```python
    return ThreadStateResponse(
        values=serialize_channel_values(channel_values),
```

**修改后：**
```python
    values = serialize_channel_values(channel_values)

    # Override messages with event store data (immune to summarization)
    es_messages = await _get_event_store_messages(request, thread_id)
    if es_messages is not None:
        values["messages"] = es_messages

    return ThreadStateResponse(
        values=values,
```

- [ ] **步骤 5：运行所有 backend 测试**

运行：`cd backend && PYTHONPATH=. uv run pytest tests/ -v --timeout=30 -x`

- [ ] **步骤 6：提交**

```bash
git add backend/app/gateway/routers/threads.py backend/tests/test_thread_state_event_store.py
git commit -m "feat(threads): load messages from event store instead of checkpoint state

Event store is append-only and immune to summarization. Messages with
null ids (human, tool) get deterministic UUIDs based on thread_id:seq
for stable frontend rendering."
```

---

### 任务 2（可选，延期）：降低 flush_threshold，以缩短中途间隔

**状态：** 这不是正确性修复。重新评估（见 spec）发现，`RunJournal` 已经会在 `run_end`、`run_error`、取消以及 worker `finally` 路径上 flush。此次调优唯一缩小的窗口，是硬进程崩溃或运行中 reload 的情况。应延期并单独决策；不要与任务 1 的合并绑定。

如果继续推进：将 `journal.py:42` 中 `flush_threshold` 的默认值从 20 改为 5，重新运行 `tests/test_run_journal.py`，并作为单独的 `perf(journal): …` commit 提交。

---

### 任务 3：修复 frontend 中的 `useThreadFeedback` 分页

一旦 `/history` 返回完整的、由 event-store 提供支持的消息流，frontend 中的 `runIdByAiIndex` 映射也必须覆盖完整流，否则它基于位置的 AI 索引映射会漂移，导致 feedback 点击指向错误的 `run_id`。当前 hook 把 `limit=200` 写死了。

**文件：**
- 修改：`frontend/src/core/threads/hooks.ts`（大约第 679 行）

- [ ] **步骤 1：用完整分页替换固定的 `?limit=200`**

将：

```ts
const res = await fetchWithAuth(
  `${getBackendBaseURL()}/api/threads/${encodeURIComponent(threadId)}/messages?limit=200`,
);
```

改为通过 `after_seq`（或 `/messages` endpoint 实际暴露的等价查询参数——在编写 TS 代码之前，请先检查 `backend/app/gateway/routers/thread_runs.py:285-323` 中的真实参数名）循环分页。持续累积 `messages`，直到某一页返回的数据量少于 page size。

- [ ] **步骤 2：防御性索引保护**

当 frontend 还在渲染 optimistic state、而 messages 查询尚未刷新时，`runIdByAiIndex[aiMessageIndex]` 仍然可能是 `undefined`。当前 `message-list.tsx:71` 中的 `?? undefined` 已经处理了这一点；不要删除它。

- [ ] **步骤 3：新 run 完成后使 `['thread-feedback', threadId]` 失效**

在 `useThreadStream`（或处理 stream-end 的位置）中，当 stream 关闭时调用 `queryClient.invalidateQueries({ queryKey: ["thread-feedback", threadId] })`，以便 `runIdByAiIndex` 能立即拿到新 run 的 AI message。

- [ ] **步骤 4：运行 `pnpm check`**

```bash
cd frontend && pnpm check
```

- [ ] **步骤 5：提交**

```bash
git add frontend/src/core/threads/hooks.ts
git commit -m "fix(feedback): paginate useThreadFeedback and invalidate after stream"
```

---

### 任务 4：端到端测试——summarize + 多 run feedback

添加一个回归测试，覆盖我们正在修复的精确 bug 类型：一个已 summarized 的 thread，至少包含两次 run，点击 feedback 时必须命中正确的 `run_id`。

**文件：**
- 修改：`backend/tests/test_thread_state_event_store.py`

- [ ] **步骤 1：编写测试**

为 `MemoryRunEventStore` 注入两次 run 的消息（`r1`：human + ai + human + ai，`r2`：human + ai），然后模拟一个 summarized 的 checkpoint state，使其丢弃 `r1` 的消息。调用 `_get_event_store_messages` 并断言：
- 长度与 event store 一致，而不是 checkpoint
- 第一条消息是原始 `r1` 的 human，而不是 summary
- AI 消息按顺序保留它们的 `lc_run--*` ids
- 所有 `id=None` 的消息都会获得稳定的 `uuid5(...)` id
- tool_result 中 legacy 的 `str(Command(update=...))` content 字段会被清洗为内部文本

- [ ] **步骤 2：运行新测试**

```bash
cd backend && PYTHONPATH=. uv run pytest tests/test_thread_state_event_store.py -v
```

- [ ] **步骤 3：与任务 1、3 的改动一起提交**

与任务 1 的 commit 打包在一起，这样测试总能与实现同步落地。

---

### 任务 5：Standard mode 后续项（仅文档）

Standard mode（`make dev`）会直接命中 LangGraph Server 的 `/threads/{id}/history`，不会经过我们刚刚修补过的 Gateway router。因此 summarize bug 在那里依然存在。

**文件：**
- 修改：本计划（在底部添加 follow-up 小节，见下文）或创建一个单独的跟踪 issue

- [ ] **步骤 1：记录该缺口**

将以下内容追加到本计划底部（或者新开一个 GitHub issue 并链接到这里）：

> **Follow-up — Standard mode summarize bug**
> `get_thread_history` in `backend/app/gateway/routers/threads.py` is only hit in Gateway mode. Standard mode proxies `/api/langgraph/*` directly to the LangGraph Server (see `backend/CLAUDE.md` nginx routing and `frontend/CLAUDE.md` `NEXT_PUBLIC_LANGGRAPH_BASE_URL`). The summarize-message-loss symptom is still reproducible there. Options: (a) teach the LangGraph Server checkpointer to branch on an override, (b) move `/history` behind Gateway in Standard mode as well, (c) accept as known limitation for Standard mode. Decide before GA.
