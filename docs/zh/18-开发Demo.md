# 18 — 开发 Demo 示例

> 本文档提供各核心模块的开发示例，帮助快速上手开发。  
> 参考来源：各模块文档 + 源码示例

---

## Demo 1：使用内嵌 Python 客户端

最简单的 Agent 调用方式，无需 HTTP，适合脚本和测试：

```python
#!/usr/bin/env python3
"""
Demo: 使用 DeerFlowClient 进行同步流式调用
文件: /tmp/demo_client.py
"""
import sys
sys.path.insert(0, 'backend/packages/harness')

from deerflow.client import DeerFlowClient

def main():
    client = DeerFlowClient()
    
    print("=== DeerFlow Agent Demo ===\n")
    
    for event in client.stream(
        "请帮我写一个 Python 函数，计算斐波那契数列的前 N 项",
        config={
            "configurable": {
                "model_name": "gpt-4o",
                "subagent_enabled": False,
            }
        }
    ):
        match event.type:
            case "message":
                print(event.data.content, end="", flush=True)
            case "tool_call":
                print(f"\n\n🔧 调用工具: {event.data.name}")
                print(f"   参数: {event.data.args}\n")
            case "tool_result":
                print(f"✅ 工具结果: {str(event.data.content)[:200]}\n")
            case "task_started":
                print(f"\n🚀 子代理任务开始: {event.data.get('description', '')}")
            case "task_completed":
                print(f"✅ 子代理任务完成")
    
    print("\n\n=== 完成 ===")

if __name__ == "__main__":
    main()
```

---

## Demo 2：通过 HTTP API 发送消息

```bash
#!/bin/bash
# Demo: 通过 REST API 与 Agent 交互
# 假设 DeerFlow 运行在 localhost:2026

# 1. 创建线程
THREAD_RESPONSE=$(curl -s -X POST http://localhost:2026/api/langgraph/threads \
  -H "Content-Type: application/json" \
  -d '{}')

THREAD_ID=$(echo $THREAD_RESPONSE | python3 -c "import sys,json; print(json.load(sys.stdin)['thread_id'])")
echo "线程 ID: $THREAD_ID"

# 2. 发送消息（SSE 流式响应）
curl -N -X POST "http://localhost:2026/api/threads/$THREAD_ID/runs/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "agent",
    "input": {
      "messages": [
        {"role": "user", "content": "请介绍一下 Python 的异步编程"}
      ]
    },
    "config": {
      "configurable": {
        "model_name": "gpt-4o"
      }
    }
  }'
```

---

## Demo 3：添加自定义工具

```python
"""
Demo: 实现并注册一个自定义工具（天气查询）
文件: backend/packages/harness/deerflow/community/weather/tool.py
"""
from langchain_core.tools import tool
import httpx

@tool
async def get_weather(city: str) -> str:
    """
    查询指定城市的天气信息。
    
    Args:
        city: 城市名称，例如 "北京"、"上海"
    
    Returns:
        天气信息字符串
    """
    # 示例：调用天气 API
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.example-weather.com/current",
                params={"city": city, "key": "YOUR_API_KEY"}
            )
            data = response.json()
            return f"{city}: {data['weather']}，{data['temperature']}°C，{data['humidity']}% 湿度"
    except Exception as e:
        return f"获取天气失败: {str(e)}"
```

在 `config.yaml` 中注册：
```yaml
tools:
  - name: weather
    use: deerflow.community.weather.tool:get_weather
    enabled: true
```

---

## Demo 4：实现自定义 Skill

```bash
# 创建技能目录
mkdir -p skills/custom/python-expert
```

```markdown
<!-- skills/custom/python-expert/SKILL.md -->
---
name: python-expert
description: Python 专家技能，提供深度的 Python 开发建议和最佳实践
version: 1.0.0
author: Your Name
allowed-tools:
  - bash
  - read_file
  - write_file
---

## Python 专家技能指南

当用户询问 Python 相关问题时，遵循以下规范：

### 代码质量标准
1. 始终使用类型注解（Python 3.12+ 语法）
2. 使用 `ruff` 格式化代码
3. 为每个函数编写 docstring
4. 优先使用标准库，减少第三方依赖

### 性能建议
1. 优先使用 `asyncio` 处理 I/O 密集型任务
2. 对 CPU 密集型任务使用 `multiprocessing`
3. 大数据集使用生成器而不是列表

### 代码示例风格
\`\`\`python
from typing import AsyncGenerator

async def process_items(
    items: list[str],
    batch_size: int = 10
) -> AsyncGenerator[list[str], None]:
    """
    批量处理 items，每次 yield 一个批次。
    
    Args:
        items: 待处理的 item 列表
        batch_size: 每批处理的数量
        
    Yields:
        每个批次的 items
    """
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]
\`\`\`
```

启用技能：
```bash
curl -X PUT http://localhost:8001/api/skills/python-expert \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

---

## Demo 5：实现自定义中间件

```python
"""
Demo: 实现一个请求日志中间件
文件: backend/packages/harness/deerflow/agents/middlewares/request_logger_middleware.py
"""
import logging
import time
from typing import Any

from deerflow.agents.middlewares.base import BaseMiddleware
from deerflow.agents.thread_state import ThreadState

logger = logging.getLogger(__name__)


class RequestLoggerMiddleware(BaseMiddleware):
    """记录每次 LLM 调用的请求和响应信息。"""
    
    def __init__(self):
        self._start_times: dict[str, float] = {}
    
    async def before_model(
        self,
        state: ThreadState,
        config: dict[str, Any] | None = None
    ) -> ThreadState:
        """在 LLM 调用前记录请求信息。"""
        thread_id = state.get("thread_data", {}).get("thread_id", "unknown")
        self._start_times[thread_id] = time.monotonic()
        
        messages = state.get("messages", [])
        logger.info(
            "LLM 调用开始",
            extra={
                "thread_id": thread_id,
                "message_count": len(messages),
                "last_message_role": messages[-1].type if messages else "none",
            }
        )
        return state
    
    async def after_model(
        self,
        state: ThreadState,
        response: Any,
        config: dict[str, Any] | None = None
    ) -> Any:
        """在 LLM 响应后记录耗时信息。"""
        thread_id = state.get("thread_data", {}).get("thread_id", "unknown")
        start_time = self._start_times.pop(thread_id, time.monotonic())
        elapsed_ms = (time.monotonic() - start_time) * 1000
        
        tool_calls_count = len(getattr(response, "tool_calls", []))
        
        logger.info(
            "LLM 调用完成",
            extra={
                "thread_id": thread_id,
                "elapsed_ms": round(elapsed_ms, 2),
                "tool_calls_count": tool_calls_count,
                "has_content": bool(getattr(response, "content", "")),
            }
        )
        return response
```

在 `_build_middlewares()` 中注册（`backend/packages/harness/deerflow/agents/lead_agent/agent.py`）：
```python
from deerflow.agents.middlewares.request_logger_middleware import RequestLoggerMiddleware

def _build_middlewares(config):
    middlewares = build_lead_runtime_middlewares(config)
    # 在适当位置插入
    middlewares.insert(0, RequestLoggerMiddleware())
    return middlewares
```

---

## Demo 6：接入 MCP 工具服务器

```python
"""
Demo: 实现一个 MCP 工具服务器（数据库查询）
文件: /tmp/demo_mcp_server.py
运行: python /tmp/demo_mcp_server.py
"""
import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

server = Server("database-query")

# 模拟数据库
FAKE_DB = {
    "users": [
        {"id": 1, "name": "张三", "email": "zhang@example.com"},
        {"id": 2, "name": "李四", "email": "li@example.com"},
    ],
    "products": [
        {"id": 1, "name": "Product A", "price": 99.9},
        {"id": 2, "name": "Product B", "price": 199.9},
    ]
}

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="query_table",
            description="查询数据库表",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "表名",
                        "enum": ["users", "products"]
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回行数限制",
                        "default": 10
                    }
                },
                "required": ["table"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "query_table":
        table = arguments["table"]
        limit = arguments.get("limit", 10)
        
        if table not in FAKE_DB:
            return [types.TextContent(type="text", text=f"错误：表 {table} 不存在")]
        
        rows = FAKE_DB[table][:limit]
        result = f"表 {table} 的查询结果（共 {len(rows)} 行）：\n"
        for row in rows:
            result += f"  {row}\n"
        
        return [types.TextContent(type="text", text=result)]
    
    raise ValueError(f"未知工具: {name}")

if __name__ == "__main__":
    asyncio.run(stdio_server(server))
```

在 `extensions_config.json` 中注册：
```json
{
  "mcpServers": {
    "database": {
      "enabled": true,
      "command": "python",
      "args": ["/tmp/demo_mcp_server.py"]
    }
  }
}
```

---

## Demo 7：使用 Plan Mode（任务规划模式）

```python
"""
Demo: 开启 Plan Mode，Agent 会生成待办列表追踪任务进度
"""
from deerflow.client import DeerFlowClient

client = DeerFlowClient()

print("=== Plan Mode Demo ===\n")
print("Agent 将使用待办列表追踪任务进度\n")

for event in client.stream(
    "帮我完成以下任务：\n1. 创建一个 Python 项目目录结构\n2. 编写 README.md\n3. 创建 main.py 入口文件",
    config={
        "configurable": {
            "model_name": "gpt-4o",
            "is_plan_mode": True,      # 开启 Plan Mode
            "subagent_enabled": True,   # 可以委托子代理
        }
    }
):
    match event.type:
        case "message":
            print(event.data.content, end="", flush=True)
        case "tool_call":
            if event.data.name == "write_todos":
                print(f"\n📋 更新待办列表")
            else:
                print(f"\n🔧 {event.data.name}")
```

---

## Demo 8：前端新增自定义设置项

```typescript
// frontend/src/core/settings/my-setting.ts
// 添加自定义设置项

export interface MyCustomSettings {
  enableFeatureX: boolean;
  maxRetries: number;
}

export const defaultMyCustomSettings: MyCustomSettings = {
  enableFeatureX: false,
  maxRetries: 3,
};

// frontend/src/core/settings/store.ts
// 在全局设置 store 中使用 Zustand 存储
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface SettingsStore {
  myCustomSettings: MyCustomSettings;
  updateMyCustomSettings: (settings: Partial<MyCustomSettings>) => void;
}

export const useSettingsStore = create<SettingsStore>()(
  persist(
    (set) => ({
      myCustomSettings: defaultMyCustomSettings,
      updateMyCustomSettings: (settings) =>
        set((state) => ({
          myCustomSettings: { ...state.myCustomSettings, ...settings },
        })),
    }),
    { name: 'deerflow-settings' }
  )
);
```

---

## Demo 9：完整的 Agent 调用示例（带错误处理）

```python
"""
Demo: 生产级别的 Agent 调用示例，包含错误处理和重试
"""
import time
import httpx
from typing import Generator

def stream_agent_response(
    thread_id: str,
    message: str,
    model_name: str = "gpt-4o",
    base_url: str = "http://localhost:2026",
    max_retries: int = 3,
) -> Generator[dict, None, None]:
    """
    向 DeerFlow Agent 发送消息并流式接收响应。
    
    Args:
        thread_id: 线程 ID
        message: 用户消息
        model_name: 使用的模型
        base_url: DeerFlow 服务地址
        max_retries: 最大重试次数
        
    Yields:
        SSE 事件数据字典
    """
    url = f"{base_url}/api/threads/{thread_id}/runs/stream"
    payload = {
        "assistant_id": "agent",
        "input": {"messages": [{"role": "user", "content": message}]},
        "config": {"configurable": {"model_name": model_name}}
    }
    
    for attempt in range(max_retries):
        try:
            with httpx.stream("POST", url, json=payload, timeout=300) as response:
                response.raise_for_status()
                
                buffer = ""
                for chunk in response.iter_text():
                    buffer += chunk
                    
                    while "\n\n" in buffer:
                        event_block, buffer = buffer.split("\n\n", 1)
                        
                        event_data = {}
                        for line in event_block.split("\n"):
                            if line.startswith("event: "):
                                event_data["event"] = line[7:]
                            elif line.startswith("data: "):
                                import json
                                try:
                                    event_data["data"] = json.loads(line[6:])
                                except json.JSONDecodeError:
                                    event_data["data"] = line[6:]
                        
                        if event_data:
                            yield event_data
            break
            
        except (httpx.HTTPError, httpx.TimeoutException) as e:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt
            print(f"请求失败（第 {attempt + 1} 次）：{e}，{wait_time}s 后重试...")
            time.sleep(wait_time)


# 使用示例
if __name__ == "__main__":
    # 1. 先创建线程
    with httpx.Client() as client:
        thread_resp = client.post(
            "http://localhost:2026/api/langgraph/threads",
            json={}
        )
        thread_id = thread_resp.json()["thread_id"]
    
    print(f"线程 ID: {thread_id}\n")
    
    # 2. 发送消息并接收流式响应
    for event in stream_agent_response(
        thread_id=thread_id,
        message="用 Python 实现快速排序，并给出时间复杂度分析",
        model_name="gpt-4o"
    ):
        if event.get("event") == "messages/partial":
            data = event.get("data", {})
            for content_item in data.get("content", []):
                if isinstance(content_item, dict) and content_item.get("type") == "text":
                    print(content_item["text"], end="", flush=True)
```
