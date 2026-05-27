# MCP（Model Context Protocol）配置

DeerFlow 支持可配置的 MCP servers 和 skills 来扩展其能力；这些配置从项目根目录下专用的 `extensions_config.json` 文件加载。

## 设置

1. 将 `extensions_config.example.json` 复制为项目根目录下的 `extensions_config.json`。
   ```bash
   # Copy example configuration
   cp extensions_config.example.json extensions_config.json
   ```

2. 将所需 MCP server 或 skill 的 `"enabled": true` 打开。
3. 根据需要配置每个 server 的命令、参数和环境变量。
4. 重启应用，以加载并注册 MCP 工具。

## Filesystem MCP Servers

DeerFlow 已经内置了面向 thread 作用域 workspace 访问的文件工具。
不要为同一个 DeerFlow workspace 再添加 MCP filesystem server。
这些重叠的文件工具使用不同的路径语义，可能导致 LLM 的工具选择与文件访问行为变得不稳定。

DeerFlow 当前也不会为 filesystem servers 适配 MCP Roots 模式。
具体来说，它不会发布按 thread 划分的 MCP roots，也不会将 DeerFlow sandbox 路径（例如 `/mnt/user-data/...`）映射为 `@modelcontextprotocol/server-filesystem` 可接受的路径。
对于 DeerFlow workspace 文件，请使用 DeerFlow 内置的文件工具。

## OAuth 支持（HTTP/SSE MCP Servers）

对于 `http` 和 `sse` 类型的 MCP servers，DeerFlow 支持 OAuth token 获取与自动 token 刷新。

- 支持的 grant：`client_credentials`、`refresh_token`
- 在 `extensions_config.json` 中为每个 server 配置 `oauth` 块
- secrets 应通过环境变量提供（例如：`$MCP_OAUTH_CLIENT_SECRET`）

示例：

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

## 自定义工具拦截器

你可以注册自定义拦截器，在每次 MCP 工具调用之前执行。这对于注入按请求生成的 headers（例如来自 LangGraph 执行上下文的用户认证 token）、记录日志或采集指标非常有用。

在 `extensions_config.json` 中通过 `mcpInterceptors` 字段声明拦截器：

```json
{
  "mcpInterceptors": [
    "my_package.mcp.auth:build_auth_interceptor"
  ],
  "mcpServers": { ... }
}
```

每个条目都是 `module:variable` 格式的 Python 导入路径（通过 `resolve_variable` 解析）。该变量必须是一个**无参 builder 函数**，它需要返回一个与 `MultiServerMCPClient` 的 `tool_interceptors` 接口兼容的异步拦截器，或者返回 `None` 表示跳过。

下面是一个从 LangGraph metadata 注入认证 headers 的拦截器示例：

```python
def build_auth_interceptor():
    async def interceptor(request, handler):
        from langgraph.config import get_config
        metadata = get_config().get("metadata", {})
        headers = dict(request.headers or {})
        if token := metadata.get("auth_token"):
            headers["X-Auth-Token"] = token
        return await handler(request.override(headers=headers))
    return interceptor
```

- 单个字符串值也会被接受，并规范化为只有一个元素的列表。
- 无效路径或 builder 构建失败只会记录 warning，不会阻塞其他拦截器。
- builder 的返回值必须是 `callable`；否则会记录 warning 并跳过。

## 工作原理

MCP servers 会暴露一组工具，这些工具会在运行时被自动发现并集成到 DeerFlow 的 agent 系统中。启用后，无需额外代码改动，这些工具就会对 agents 可用。

## 示例能力

MCP servers 可以提供以下访问能力：

- **数据库**（例如 PostgreSQL）
- **外部 API**（例如 GitHub、Brave Search）
- **浏览器自动化**（例如 Puppeteer）
- **自定义 MCP server 实现**

## 了解更多

有关 Model Context Protocol 的详细文档，请访问：  
https://modelcontextprotocol.io
