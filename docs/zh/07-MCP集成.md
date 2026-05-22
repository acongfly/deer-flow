# 07 — 核心模块：MCP 集成

> 原始资料：[`backend/docs/MCP_SERVER.md`](../../backend/docs/MCP_SERVER.md) · [`backend/CLAUDE.md`](../../backend/CLAUDE.md)  
> 源码位置：`backend/packages/harness/deerflow/mcp/`

---

## 1. 什么是 MCP

MCP（Model Context Protocol）是一个开放协议，让 AI Agent 可以调用外部服务的工具。DeerFlow 使用 `langchain-mcp-adapters` 库的 `MultiServerMCPClient` 管理多服务器连接。

---

## 2. 总体结构

```
deerflow/mcp/
├── __init__.py
├── cache.py        # 工具缓存（懒加载 + mtime 失效）
├── client.py       # MCP 客户端封装（MultiServerMCPClient）
├── oauth.py        # OAuth Token 获取和刷新
├── session_pool.py # 会话池管理
└── tools.py        # get_cached_mcp_tools()
```

---

## 3. 配置文件：extensions_config.json

**路径**：项目根目录 `extensions_config.json`（从 `extensions_config.example.json` 复制）

配置优先级：
1. 显式传入的 `config_path` 参数
2. `DEER_FLOW_EXTENSIONS_CONFIG_PATH` 环境变量
3. 当前目录（backend/）的 `extensions_config.json`
4. 父目录（项目根）的 `extensions_config.json`（**推荐位置**）

### stdio 传输（命令行进程）

```json
{
  "mcpServers": {
    "filesystem": {
      "enabled": true,
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
      "env": {}
    },
    "github": {
      "enabled": true,
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "$GITHUB_TOKEN"
      }
    }
  }
}
```

### HTTP 传输

```json
{
  "mcpServers": {
    "my-http-server": {
      "enabled": true,
      "type": "http",
      "url": "https://api.example.com/mcp"
    }
  }
}
```

### SSE 传输

```json
{
  "mcpServers": {
    "my-sse-server": {
      "enabled": true,
      "type": "sse",
      "url": "https://api.example.com/mcp/sse"
    }
  }
}
```

---

## 4. OAuth 支持（HTTP / SSE 服务器）

对于 HTTP 和 SSE 类型的 MCP 服务器，DeerFlow 支持 OAuth Token 自动获取和刷新：

```json
{
  "mcpServers": {
    "secure-http-server": {
      "enabled": true,
      "type": "http",
      "url": "https://api.example.com/mcp",
      "oauth": {
        "enabled": true,
        "token_url": "https://auth.example.com/oauth/token",
        "grant_type": "client_credentials",
        "client_id": "$MCP_OAUTH_CLIENT_ID",
        "client_secret": "$MCP_OAUTH_CLIENT_SECRET",
        "scope": "mcp.read",
        "refresh_skew_seconds": 60
      }
    }
  }
}
```

**支持的 grant type**：
- `client_credentials`
- `refresh_token`

Token 会自动注入 Authorization 请求头，过期前 `refresh_skew_seconds` 秒自动刷新。

---

## 5. 工具缓存机制

**文件**：`backend/packages/harness/deerflow/mcp/tools.py`

`get_cached_mcp_tools()` 的缓存策略：
- **懒加载**：首次使用时初始化 MCP 客户端
- **mtime 失效**：检测 `extensions_config.json` 文件修改时间，文件变化时自动重新加载
- **Gateway API 更新**：`PUT /api/mcp/config` 保存到 `extensions_config.json`，LangGraph 通过 mtime 检测自动感知

---

## 6. 通过 Gateway API 管理 MCP 配置

无需重启，通过 API 动态更新：

```bash
# 查看当前 MCP 配置
GET /api/mcp/config

# 更新 MCP 配置（会保存到 extensions_config.json）
PUT /api/mcp/config
Content-Type: application/json

{
  "mcpServers": {
    "new-server": {
      "enabled": true,
      "command": "npx",
      "args": ["-y", "my-mcp-server"]
    }
  }
}
```

前端的 MCP 设置页面也可以直接管理这些配置。

---

## 7. 文件系统 MCP 服务器注意事项

> ⚠️ **不要为 DeerFlow 工作区添加 MCP 文件系统服务器**

DeerFlow 已内置文件工具用于线程作用域的工作区访问（`bash`、`read_file`、`write_file` 等）。如果再添加 MCP 文件系统服务器用于同一 DeerFlow 工作区，会产生路径语义冲突，导致 LLM 工具选择行为不稳定。

DeerFlow 目前不适配 MCP Roots 模式，无法将 DeerFlow 沙箱路径（如 `/mnt/user-data/...`）映射到 `@modelcontextprotocol/server-filesystem` 所接受的路径。

---

## 8. 开发步骤：开发自定义 MCP 服务器

### 步骤 1：实现 MCP 服务器

```python
# my_mcp_server.py
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

server = Server("my-server")

@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="my_tool",
            description="我的自定义工具",
            inputSchema={
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "输入内容"}
                },
                "required": ["input"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "my_tool":
        result = f"处理结果: {arguments['input']}"
        return [types.TextContent(type="text", text=result)]
    raise ValueError(f"未知工具: {name}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(stdio_server(server))
```

### 步骤 2：注册到 extensions_config.json

```json
{
  "mcpServers": {
    "my-server": {
      "enabled": true,
      "command": "python",
      "args": ["/path/to/my_mcp_server.py"]
    }
  }
}
```

### 步骤 3：验证

重启 Gateway 或等待 mtime 检测，然后在对话中测试新工具是否可用。

---

## 9. 调试 MCP 连接

```bash
# 查看 Gateway 日志，搜索 MCP 初始化信息
tail -f logs/gateway.log | grep -i mcp

# 通过 API 检查已加载的 MCP 工具
curl http://localhost:8001/api/mcp/config
```
