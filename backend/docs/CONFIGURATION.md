# 配置指南

本指南说明如何为你的环境配置 DeerFlow。

## 配置版本管理

`config.example.yaml` 包含一个用于跟踪 schema 变更的 `config_version` 字段。当示例文件中的版本高于本地 `config.yaml` 时，应用会在启动时发出警告：

```
WARNING - Your config.yaml (version 0) is outdated — the latest version is 1.
Run `make config-upgrade` to merge new fields into your config.
```

- 你的配置中**缺失 `config_version`** 会被视为版本 0。
- 运行 `make config-upgrade` 可自动合并缺失字段（会保留你现有的值，并创建一个 `.bak` 备份）。
- 当配置 schema 发生变化时，请同步提升 `config.example.yaml` 中的 `config_version`。

## 配置章节

### Models

配置 agent 可用的 LLM 模型：

```yaml
models:
  - name: gpt-4                    # Internal identifier
    display_name: GPT-4            # Human-readable name
    use: langchain_openai:ChatOpenAI  # LangChain class path
    model: gpt-4                   # Model identifier for API
    api_key: $OPENAI_API_KEY       # API key (use env var)
    max_tokens: 4096               # Max tokens per request
    temperature: 0.7               # Sampling temperature
```

**支持的 Provider：**
- OpenAI (`langchain_openai:ChatOpenAI`)
- Anthropic (`langchain_anthropic:ChatAnthropic`)
- DeepSeek (`langchain_deepseek:ChatDeepSeek`)
- Claude Code OAuth (`deerflow.models.claude_provider:ClaudeChatModel`)
- Codex CLI (`deerflow.models.openai_codex_provider:CodexChatModel`)
- 任意兼容 LangChain 的 provider

基于 CLI 的 provider 示例：

```yaml
models:
  - name: gpt-5.4
    display_name: GPT-5.4 (Codex CLI)
    use: deerflow.models.openai_codex_provider:CodexChatModel
    model: gpt-5.4
    supports_thinking: true
    supports_reasoning_effort: true

  - name: claude-sonnet-4.6
    display_name: Claude Sonnet 4.6 (Claude Code OAuth)
    use: deerflow.models.claude_provider:ClaudeChatModel
    model: claude-sonnet-4-6
    max_tokens: 4096
    supports_thinking: true
```

**基于 CLI 的 provider 认证行为：**
- `CodexChatModel` 会从 `~/.codex/auth.json` 加载 Codex CLI 认证信息
- Codex Responses 端点当前会拒绝 `max_tokens` 和 `max_output_tokens`，因此 `CodexChatModel` 不提供请求级 token 上限
- `ClaudeChatModel` 接受 `CLAUDE_CODE_OAUTH_TOKEN`、`ANTHROPIC_AUTH_TOKEN`、`CLAUDE_CODE_OAUTH_TOKEN_FILE_DESCRIPTOR`、`CLAUDE_CODE_CREDENTIALS_PATH`，或明文 `~/.claude/.credentials.json`
- 在 macOS 上，DeerFlow 不会自动探测 Keychain。需要时请使用 `scripts/export_claude_code_oauth.py` 显式导出 Claude Code 认证信息

如果要通过 LangChain 使用 OpenAI 的 `/v1/responses` 端点，请继续使用 `langchain_openai:ChatOpenAI`，并设置：

```yaml
models:
  - name: gpt-5-responses
    display_name: GPT-5 (Responses API)
    use: langchain_openai:ChatOpenAI
    model: gpt-5
    api_key: $OPENAI_API_KEY
    use_responses_api: true
    output_version: responses/v1
```

对于 OpenAI 兼容网关（例如 Novita 或 OpenRouter），同样继续使用 `langchain_openai:ChatOpenAI`，并设置 `base_url`：

```yaml
models:
  - name: novita-deepseek-v3.2
    display_name: Novita DeepSeek V3.2
    use: langchain_openai:ChatOpenAI
    model: deepseek/deepseek-v3.2
    api_key: $NOVITA_API_KEY
    base_url: https://api.novita.ai/openai
    supports_thinking: true
    when_thinking_enabled:
      extra_body:
        thinking:
          type: enabled

  - name: minimax-m2.5
    display_name: MiniMax M2.5
    use: langchain_openai:ChatOpenAI
    model: MiniMax-M2.5
    api_key: $MINIMAX_API_KEY
    base_url: https://api.minimax.io/v1
    max_tokens: 4096
    temperature: 1.0  # MiniMax requires temperature in (0.0, 1.0]
    supports_vision: true

  - name: minimax-m2.5-highspeed
    display_name: MiniMax M2.5 Highspeed
    use: langchain_openai:ChatOpenAI
    model: MiniMax-M2.5-highspeed
    api_key: $MINIMAX_API_KEY
    base_url: https://api.minimax.io/v1
    max_tokens: 4096
    temperature: 1.0  # MiniMax requires temperature in (0.0, 1.0]
    supports_vision: true
  - name: openrouter-gemini-2.5-flash
    display_name: Gemini 2.5 Flash (OpenRouter)
    use: langchain_openai:ChatOpenAI
    model: google/gemini-2.5-flash-preview
    api_key: $OPENAI_API_KEY
    base_url: https://openrouter.ai/api/v1
```

如果你的 OpenRouter key 存在于其他环境变量名中，请将 `api_key` 明确指向该变量（例如 `api_key: $OPENROUTER_API_KEY`）。

**Thinking 模型：**
某些模型支持用于复杂推理的 “thinking” 模式：

```yaml
models:
  - name: deepseek-v3
    supports_thinking: true
    when_thinking_enabled:
      extra_body:
        thinking:
          type: enabled
```

**通过 OpenAI 兼容网关使用带 thinking 的 Gemini：**

当你通过启用了 thinking 的 OpenAI 兼容代理（Vertex AI OpenAI compat endpoint、AI Studio 或第三方网关）路由 Gemini 时，API 会在响应中返回的每个 tool-call 对象上附加一个 `thought_signature`。之后所有重放这些 assistant 消息的请求，**都必须**在 tool-call 条目上回传这些 signature，否则 API 会返回：

```
HTTP 400 INVALID_ARGUMENT: function call `<tool>` in the N. content block is
missing a `thought_signature`.
```

标准的 `langchain_openai:ChatOpenAI` 在序列化消息时会静默丢弃 `thought_signature`。请改用 `deerflow.models.patched_openai:PatchedChatOpenAI`——它会把工具调用签名（来源于 `AIMessage.additional_kwargs["tool_calls"]`）重新注入到所有出站 payload 中：

```yaml
models:
  - name: gemini-2.5-pro-thinking
    display_name: Gemini 2.5 Pro (Thinking)
    use: deerflow.models.patched_openai:PatchedChatOpenAI
    model: google/gemini-2.5-pro-preview   # model name as expected by your gateway
    api_key: $GEMINI_API_KEY
    base_url: https://<your-openai-compat-gateway>/v1
    max_tokens: 16384
    supports_thinking: true
    supports_vision: true
    when_thinking_enabled:
      extra_body:
        thinking:
          type: enabled
```

如果访问 Gemini 时**未启用** thinking（例如通过未开启 thinking 的 OpenRouter），使用普通的 `langchain_openai:ChatOpenAI` 并设置 `supports_thinking: false` 即可，无需补丁。

### 工具分组

将工具组织到逻辑分组中：

```yaml
tool_groups:
  - name: web          # Web browsing and search
  - name: file:read    # Read-only file operations
  - name: file:write   # Write file operations
  - name: bash         # Shell command execution
```

### Tools

配置 agent 可用的具体工具：

```yaml
tools:
  - name: web_search
    group: web
    use: deerflow.community.tavily.tools:web_search_tool
    max_results: 5
    # api_key: $TAVILY_API_KEY  # Optional
```

**内置工具：**
- `web_search` - 搜索 Web（DuckDuckGo、Tavily、Exa、InfoQuest、Firecrawl）
- `web_fetch` - 抓取网页（Jina AI、Exa、InfoQuest、Firecrawl）
- `ls` - 列出目录内容
- `read_file` - 读取文件内容
- `write_file` - 写入文件内容
- `str_replace` - 在文件中进行字符串替换
- `bash` - 执行 bash 命令

### Sandbox

DeerFlow 支持多种 sandbox 执行模式。在 `config.yaml` 中配置你偏好的模式：

**本地执行**（直接在宿主机上运行 sandbox 代码）：
```yaml
sandbox:
   use: deerflow.sandbox.local:LocalSandboxProvider # Local execution
   allow_host_bash: false # default; host bash is disabled unless explicitly re-enabled
```

**Docker 执行**（在隔离的 Docker 容器中运行 sandbox 代码）：
```yaml
sandbox:
   use: deerflow.community.aio_sandbox:AioSandboxProvider # Docker-based sandbox
```

**结合 Kubernetes 的 Docker 执行**（通过 provisioner service 在 Kubernetes Pod 中运行 sandbox 代码）：

本模式会在你**宿主机集群**中的隔离 Kubernetes Pod 中运行每个 sandbox。需要 Docker Desktop K8s、OrbStack 或类似的本地 K8s 环境。

```yaml
sandbox:
   use: deerflow.community.aio_sandbox:AioSandboxProvider
   provisioner_url: http://provisioner:8002
```

使用 Docker 开发模式（`make docker-start`）时，只有在配置了此 provisioner 模式的情况下，DeerFlow 才会启动 `provisioner` 服务。在本地模式或普通 Docker sandbox 模式下，会跳过 `provisioner`。

有关详细配置、前置条件和故障排查，请参见 [Provisioner Setup Guide](../../docker/provisioner/README.md)。

可在本地执行与基于 Docker 的隔离之间进行选择：

**选项 1：Local Sandbox**（默认，配置更简单）：
```yaml
sandbox:
  use: deerflow.sandbox.local:LocalSandboxProvider
  allow_host_bash: false
```

`allow_host_bash` 默认有意设为 `false`。DeerFlow 的本地 sandbox 只是宿主机侧的便捷模式，并不是安全的 shell 隔离边界。如果你需要 `bash`，优先使用 `AioSandboxProvider`。只有在完全可信、单用户的本地工作流中，才建议设置 `allow_host_bash: true`。

**选项 2：Docker Sandbox**（隔离更强，更安全）：
```yaml
sandbox:
  use: deerflow.community.aio_sandbox:AioSandboxProvider
  port: 8080
  auto_start: true
  container_prefix: deer-flow-sandbox

  # Optional: Additional mounts
  mounts:
    - host_path: /path/on/host
      container_path: /path/in/container
      read_only: false
```

当你配置 `sandbox.mounts` 时，DeerFlow 会把这些 `container_path` 值暴露在 agent prompt 中，使 agent 能直接发现并操作挂载目录，而不是假设所有内容都必须位于 `/mnt/user-data` 下。

对于使用 localhost 的裸机 Docker sandbox 运行，DeerFlow 默认会将 sandbox HTTP 端口绑定到 `127.0.0.1`，以避免暴露到宿主机的所有网络接口。通过 `host.docker.internal` 连接的 Docker-outside-of-Docker 部署则会保留较宽松的旧绑定方式以保持兼容。如果你的部署需要不同的绑定地址，请显式设置 `DEER_FLOW_SANDBOX_BIND_HOST`。

### Skills

为专门化工作流配置 skills 目录：

```yaml
skills:
  # Host path (optional, default: ../skills)
  path: /custom/path/to/skills

  # Container mount path (default: /mnt/skills)
  container_path: /mnt/skills
```

**Skills 的工作方式：**
- Skills 存储在 `deer-flow/skills/{public,custom}/`
- 每个 skill 都有一个包含元数据的 `SKILL.md` 文件
- Skills 会被自动发现并加载
- 通过路径映射，可在本地和 Docker sandbox 中使用

**按 Agent 过滤 Skills：**
自定义 agent 可以在其 `config.yaml`（位于 `workspace/agents/<agent_name>/config.yaml`）中定义 `skills` 字段，以限制加载哪些 skill：
- **省略或设为 `null`**：加载所有全局启用的 skills（默认回退行为）。
- **`[]`（空列表）**：为该特定 agent 禁用所有 skills。
- **`["skill-name"]`**：仅加载明确指定的 skills。

### 标题生成

自动生成对话标题：

```yaml
title:
  enabled: true
  max_words: 6
  max_chars: 60
  model_name: null  # Use first model in list
```

### GitHub API Token（可选，用于 GitHub Deep Research Skill）

GitHub API 的默认速率限制相当严格。对于频繁的项目研究，我们建议配置一个具有只读权限的个人访问令牌（PAT）。

**配置步骤：**
1. 取消注释 `.env` 文件中的 `GITHUB_TOKEN` 行，并填入你的个人访问令牌
2. 重启 DeerFlow 服务以应用更改

## 环境变量

DeerFlow 支持使用 `$` 前缀进行环境变量替换：

```yaml
models:
  - api_key: $OPENAI_API_KEY  # Reads from environment
```

**常用环境变量：**
- `OPENAI_API_KEY` - OpenAI API key
- `ANTHROPIC_API_KEY` - Anthropic API key
- `DEEPSEEK_API_KEY` - DeepSeek API key
- `NOVITA_API_KEY` - Novita API key（OpenAI 兼容端点）
- `TAVILY_API_KEY` - Tavily 搜索 API key
- `DEER_FLOW_PROJECT_ROOT` - 相对运行时路径所基于的项目根目录
- `DEER_FLOW_CONFIG_PATH` - 自定义配置文件路径
- `DEER_FLOW_EXTENSIONS_CONFIG_PATH` - 自定义 extensions 配置文件路径
- `DEER_FLOW_HOME` - 运行时状态目录（默认为项目根目录下的 `.deer-flow`）
- `DEER_FLOW_SKILLS_PATH` - 当 `skills.path` 省略时使用的 skills 目录
- `GATEWAY_ENABLE_DOCS` - 设为 `false` 可禁用 Swagger UI（`/docs`）、ReDoc（`/redoc`）和 OpenAPI schema（`/openapi.json`）端点（默认：`true`）

## 配置文件位置

配置文件应放置在**项目根目录**（`deer-flow/config.yaml`）。如果进程可能从其他工作目录启动，请设置 `DEER_FLOW_PROJECT_ROOT`；或者设置 `DEER_FLOW_CONFIG_PATH` 指向某个特定文件。

## 配置优先级

DeerFlow 按以下顺序查找配置：

1. 代码中通过 `config_path` 参数指定的路径
2. `DEER_FLOW_CONFIG_PATH` 环境变量提供的路径
3. `DEER_FLOW_PROJECT_ROOT` 下的 `config.yaml`，若未设置 `DEER_FLOW_PROJECT_ROOT`，则使用当前工作目录下的 `config.yaml`
4. 为保持 monorepo 兼容性而保留的旧 backend/仓库根目录位置

## 最佳实践

1. **将 `config.yaml` 放在项目根目录** - 如果运行时从其他位置启动，请设置 `DEER_FLOW_PROJECT_ROOT`
2. **不要提交 `config.yaml`** - 它已经被加入 `.gitignore`
3. **对敏感信息使用环境变量** - 不要硬编码 API key
4. **保持 `config.example.yaml` 为最新** - 记录所有新增选项
5. **在本地测试配置变更** - 再进行部署
6. **在生产环境使用 Docker sandbox** - 提供更好的隔离性和安全性

## 故障排查

### “找不到配置文件”
- 确保 `config.yaml` 位于**项目根目录**（`deer-flow/config.yaml`）
- 如果运行时从项目根目录之外启动，请设置 `DEER_FLOW_PROJECT_ROOT`
- 或者设置 `DEER_FLOW_CONFIG_PATH` 环境变量指向自定义位置

### “API key 无效”
- 验证环境变量是否已正确设置
- 检查是否为环境变量引用使用了 `$` 前缀

### “Skills 未加载”
- 检查 `deer-flow/skills/` 目录是否存在
- 验证 skills 是否包含有效的 `SKILL.md` 文件
- 如果使用自定义路径，请检查 `skills.path` 或 `DEER_FLOW_SKILLS_PATH`

### “Docker sandbox 启动失败”
- 确保 Docker 正在运行
- 检查端口 8080（或所配置端口）是否可用
- 验证 Docker 镜像可被访问

## 示例

完整配置选项示例请参见 `config.example.yaml`。
