# 为 DeerFlow Backend 做贡献

感谢你对为 DeerFlow 做贡献感兴趣！本文档提供了为后端代码库做贡献的指南和说明。

## 目录

- [入门](#入门)
- [开发环境设置](#开发环境设置)
- [项目结构](#项目结构)
- [代码风格](#代码风格)
- [进行更改](#进行更改)
- [测试](#测试)
- [Pull Request 流程](#pull-request-流程)
- [架构指南](#架构指南)

## 入门

### 先决条件

- Python 3.12 或更高版本
- [uv](https://docs.astral.sh/uv/) 包管理器
- Git
- Docker（可选，用于 Docker sandbox 测试）

### Fork 与 Clone

1. 在 GitHub 上 fork 此仓库
2. 在本地 clone 你的 fork：
   ```bash
   git clone https://github.com/YOUR_USERNAME/deer-flow.git
   cd deer-flow
   ```

## 开发环境设置

### 安装依赖

```bash
# From project root
cp config.example.yaml config.yaml

# Install backend dependencies
cd backend
make install
```

### 配置环境

设置你的 API 密钥以进行测试：

```bash
export OPENAI_API_KEY="your-api-key"
# Add other keys as needed
```

### 运行开发服务器

```bash
# Gateway API + embedded agent runtime
make dev
```

## 项目结构

```
backend/src/
├── agents/                  # Agent system
│   ├── lead_agent/         # Main agent implementation
│   │   └── agent.py        # Agent factory and creation
│   ├── middlewares/        # Agent middlewares
│   │   ├── thread_data_middleware.py
│   │   ├── sandbox_middleware.py
│   │   ├── title_middleware.py
│   │   ├── uploads_middleware.py
│   │   ├── view_image_middleware.py
│   │   └── clarification_middleware.py
│   └── thread_state.py     # Thread state definition
│
├── gateway/                 # FastAPI Gateway
│   ├── app.py              # FastAPI application
│   └── routers/            # Route handlers
│       ├── models.py       # /api/models endpoints
│       ├── mcp.py          # /api/mcp endpoints
│       ├── skills.py       # /api/skills endpoints
│       ├── artifacts.py    # /api/threads/.../artifacts
│       └── uploads.py      # /api/threads/.../uploads
│
├── sandbox/                 # Sandbox execution
│   ├── __init__.py         # Sandbox interface
│   ├── local.py            # Local sandbox provider
│   └── tools.py            # Sandbox tools (bash, file ops)
│
├── tools/                   # Agent tools
│   └── builtins/           # Built-in tools
│       ├── present_file_tool.py
│       ├── ask_clarification_tool.py
│       └── view_image_tool.py
│
├── mcp/                     # MCP integration
│   └── manager.py          # MCP server management
│
├── models/                  # Model system
│   └── factory.py          # Model factory
│
├── skills/                  # Skills system
│   └── loader.py           # Skills loader
│
├── config/                  # Configuration
│   ├── app_config.py       # Main app config
│   ├── extensions_config.py # Extensions config
│   └── summarization_config.py
│
├── community/               # Community tools
│   ├── tavily/             # Tavily web search
│   ├── jina/               # Jina web fetch
│   ├── firecrawl/          # Firecrawl scraping
│   └── aio_sandbox/        # Docker sandbox
│
├── reflection/              # Dynamic loading
│   └── __init__.py         # Module resolution
│
└── utils/                   # Utilities
    └── __init__.py
```

## 代码风格

### Lint 与格式化

我们使用 `ruff` 同时进行 lint 和格式化：

```bash
# Check for issues
make lint

# Auto-fix and format
make format
```

### 风格指南

- **行长度**：最多 240 个字符
- **Python 版本**：允许使用 3.12+ 特性
- **类型提示**：为函数签名使用类型提示
- **引号**：字符串使用双引号
- **缩进**：4 个空格（不使用制表符）
- **导入**：按标准库、第三方、本地分组

### 文档字符串

为公共函数和类使用文档字符串：

```python
def create_chat_model(name: str, thinking_enabled: bool = False) -> BaseChatModel:
    """Create a chat model instance from configuration.

    Args:
        name: The model name as defined in config.yaml
        thinking_enabled: Whether to enable extended thinking

    Returns:
        A configured LangChain chat model instance

    Raises:
        ValueError: If the model name is not found in configuration
    """
    ...
```

## 进行更改

### 分支命名

使用描述性的分支名称：

- `feature/add-new-tool` - 新功能
- `fix/sandbox-timeout` - Bug 修复
- `docs/update-readme` - 文档
- `refactor/config-system` - 代码重构

### Commit 消息

编写清晰、简洁的 commit 消息：

```
feat: add support for Claude 3.5 model

- Add model configuration in config.yaml
- Update model factory to handle Claude-specific settings
- Add tests for new model
```

前缀类型：
- `feat:` - 新功能
- `fix:` - Bug 修复
- `docs:` - 文档
- `refactor:` - 代码重构
- `test:` - 测试
- `chore:` - 构建/配置变更

## 测试

### 运行测试

```bash
uv run pytest
```

### 编写测试

将测试放在 `tests/` 目录中，并与源代码结构保持对应：

```
tests/
├── test_models/
│   └── test_factory.py
├── test_sandbox/
│   └── test_local.py
└── test_gateway/
    └── test_models_router.py
```

测试示例：

```python
import pytest
from deerflow.models.factory import create_chat_model

def test_create_chat_model_with_valid_name():
    """Test that a valid model name creates a model instance."""
    model = create_chat_model("gpt-4")
    assert model is not None

def test_create_chat_model_with_invalid_name():
    """Test that an invalid model name raises ValueError."""
    with pytest.raises(ValueError):
        create_chat_model("nonexistent-model")
```

## Pull Request 流程

### 提交前

1. **确保测试通过**：`uv run pytest`
2. **运行 linter**：`make lint`
3. **格式化代码**：`make format`
4. 如有需要，**更新文档**

### PR 描述

在 PR 描述中包含：

- **内容**：变更的简要说明
- **原因**：进行此变更的动机
- **方式**：实现方法
- **测试**：你如何测试这些更改

### 评审流程

1. 提交带有清晰描述的 PR
2. 处理评审反馈
3. 确保 CI 通过
4. 获得批准后，维护者会进行合并

## 架构指南

### 添加新工具

1. 在 `packages/harness/deerflow/tools/builtins/` 或 `packages/harness/deerflow/community/` 中创建工具：

```python
# packages/harness/deerflow/tools/builtins/my_tool.py
from langchain_core.tools import tool

@tool
def my_tool(param: str) -> str:
    """Tool description for the agent.

    Args:
        param: Description of the parameter

    Returns:
        Description of return value
    """
    return f"Result: {param}"
```

2. 在 `config.yaml` 中注册：

```yaml
tools:
  - name: my_tool
    group: my_group
    use: deerflow.tools.builtins.my_tool:my_tool
```

### 添加新 Middleware

1. 在 `packages/harness/deerflow/agents/middlewares/` 中创建 middleware：

```python
# packages/harness/deerflow/agents/middlewares/my_middleware.py
from langchain.agents.middleware import BaseMiddleware
from langchain_core.runnables import RunnableConfig

class MyMiddleware(BaseMiddleware):
    """Middleware description."""

    def transform_state(self, state: dict, config: RunnableConfig) -> dict:
        """Transform the state before agent execution."""
        # Modify state as needed
        return state
```

2. 在 `packages/harness/deerflow/agents/lead_agent/agent.py` 中注册：

```python
middlewares = [
    ThreadDataMiddleware(),
    SandboxMiddleware(),
    MyMiddleware(),  # Add your middleware
    TitleMiddleware(),
    ClarificationMiddleware(),
]
```

### 添加新 API 端点

1. 在 `app/gateway/routers/` 中创建 router：

```python
# app/gateway/routers/my_router.py
from fastapi import APIRouter

router = APIRouter(prefix="/my-endpoint", tags=["my-endpoint"])

@router.get("/")
async def get_items():
    """Get all items."""
    return {"items": []}

@router.post("/")
async def create_item(data: dict):
    """Create a new item."""
    return {"created": data}
```

2. 在 `app/gateway/app.py` 中注册：

```python
from app.gateway.routers import my_router

app.include_router(my_router.router)
```

### 配置变更

添加新的配置选项时：

1. 在 `packages/harness/deerflow/config/app_config.py` 中更新新字段
2. 在 `config.example.yaml` 中添加默认值
3. 在 `docs/CONFIGURATION.md` 中编写文档

### MCP 服务器集成

要添加对新 MCP 服务器的支持：

1. 在 `extensions_config.json` 中添加配置：

```json
{
  "mcpServers": {
    "my-server": {
      "enabled": true,
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@my-org/mcp-server"],
      "description": "My MCP Server"
    }
  }
}
```

2. 在 `extensions_config.example.json` 中更新这个新服务器

### Skills 开发

要创建一个新的 skill：

1. 在 `skills/public/` 或 `skills/custom/` 中创建目录：

```
skills/public/my-skill/
└── SKILL.md
```

2. 编写带有 YAML front matter 的 `SKILL.md`：

```markdown
---
name: My Skill
description: What this skill does
license: MIT
allowed-tools:
  - read_file
  - write_file
  - bash
---

# My Skill

Instructions for the agent when this skill is enabled...
```

## 有问题？

如果你对贡献流程有疑问：

1. 查看 `docs/` 中已有的文档
2. 在 GitHub 上查找类似的 issue 或 PR
3. 在 GitHub 上发起 discussion 或 issue

感谢你为 DeerFlow 做出贡献！
