# Guardrails：工具调用前授权

> **背景：** [Issue #1213](https://github.com/bytedance/deer-flow/issues/1213) —— DeerFlow 已具备 Docker sandbox 和通过 `ask_clarification` 实现的人类审批，但尚缺少一个针对工具调用的确定性、策略驱动授权层。运行自主多步骤任务的 agent 可以使用任意参数执行任何已加载工具。Guardrails 会添加一个 middleware，在执行**之前**依据策略评估每一次工具调用。

## 为什么需要 Guardrails

```
Without guardrails:                      With guardrails:

  Agent                                    Agent
    │                                        │
    ▼                                        ▼
  ┌──────────┐                             ┌──────────┐
  │ bash     │──▶ executes immediately     │ bash     │──▶ GuardrailMiddleware
  │ rm -rf / │                             │ rm -rf / │        │
  └──────────┘                             └──────────┘        ▼
                                                         ┌──────────────┐
                                                         │  Provider    │
                                                         │  evaluates   │
                                                         │  against     │
                                                         │  policy      │
                                                         └──────┬───────┘
                                                                │
                                                          ┌─────┴─────┐
                                                          │           │
                                                        ALLOW       DENY
                                                          │           │
                                                          ▼           ▼
                                                      Tool runs   Agent sees:
                                                      normally    "Guardrail denied:
                                                                   rm -rf blocked"
```

- **Sandboxing** 提供的是进程隔离，而不是语义层授权。被 sandbox 的 `bash` 仍然可以用 `curl` 把数据发出去。
- **人工审批**（`ask_clarification`）要求每个操作都有人在环。对于自治工作流并不可行。
- **Guardrails** 提供无需人工干预、确定性且由策略驱动的授权能力。

## 架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Middleware Chain                               │
│                                                                      │
│  1. ThreadDataMiddleware     ─── per-thread dirs                     │
│  2. UploadsMiddleware        ─── file upload tracking                │
│  3. SandboxMiddleware        ─── sandbox acquisition                 │
│  4. DanglingToolCallMiddleware ── fix incomplete tool calls           │
│  5. GuardrailMiddleware ◄──── EVALUATES EVERY TOOL CALL             │
│  6. ToolErrorHandlingMiddleware ── convert exceptions to messages     │
│  7-12. (Summarization, Title, Memory, Vision, Subagent, Clarify)    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
           ┌──────────────────────────┐
           │    GuardrailProvider     │  ◄── pluggable: any class
           │    (configured in YAML)  │      with evaluate/aevaluate
           └────────────┬─────────────┘
                        │
              ┌─────────┼──────────────┐
              │         │              │
              ▼         ▼              ▼
         Built-in   OAP Passport    Custom
         Allowlist  Provider        Provider
         (zero dep) (open standard) (your code)
                        │
                  Any implementation
                  (e.g. APort, or
                   your own evaluator)
```

`GuardrailMiddleware` 实现了 `wrap_tool_call` / `awrap_tool_call`（与 `ToolErrorHandlingMiddleware` 使用同一种 `AgentMiddleware` 模式）。它会：

1. 使用工具名、参数和 passport 引用构建 `GuardrailRequest`
2. 在已配置的 provider 上调用 `provider.evaluate(request)`
3. 如果**拒绝**：返回带有原因的 `ToolMessage(status="error")` —— agent 会看到拒绝并进行调整
4. 如果**允许**：继续传递给真实的工具处理器
5. 如果出现 **provider 错误** 且 `fail_closed=true`（默认）：阻止该调用
6. `GraphBubbleUp` 异常（LangGraph 控制信号）总是直接向上传播，绝不会被捕获

## 三种 Provider 选项

### 选项 1：内置 AllowlistProvider（零依赖）

这是最简单的选项，随 DeerFlow 一起提供。可按名称阻止或允许工具。无需外部包、无需 passport、无需网络。

**config.yaml：**
```yaml
guardrails:
  enabled: true
  provider:
    use: deerflow.guardrails.builtin:AllowlistProvider
    config:
      denied_tools: ["bash", "write_file"]
```

这会对所有请求阻止 `bash` 和 `write_file`。其余工具都会放行。

你也可以使用 allowlist（仅允许这些工具）：
```yaml
guardrails:
  enabled: true
  provider:
    use: deerflow.guardrails.builtin:AllowlistProvider
    config:
      allowed_tools: ["web_search", "read_file", "ls"]
```

**试一试：**
1. 将上述配置添加到你的 `config.yaml`
2. 启动 DeerFlow：`make dev`
3. 向 agent 提问：“Use bash to run echo hello”
4. agent 会看到：`Guardrail denied: tool 'bash' was blocked (oap.tool_not_allowed)`

### 选项 2：OAP Passport Provider（基于策略）

用于基于 [Open Agent Passport (OAP)](https://github.com/aporthq/aport-spec) 开放标准执行策略。OAP passport 是一个 JSON 文档，用于声明 agent 的身份、能力和运行限制。任何能够读取 OAP passport 并返回符合 OAP 的决策结果的 provider，都可以与 DeerFlow 配合使用。

```
┌─────────────────────────────────────────────────────────────┐
│                    OAP Passport (JSON)                        │
│                   (open standard, any provider)              │
│  {                                                           │
│    "spec_version": "oap/1.0",                                │
│    "status": "active",                                       │
│    "capabilities": [                                         │
│      {"id": "system.command.execute"},                       │
│      {"id": "data.file.read"},                               │
│      {"id": "data.file.write"},                              │
│      {"id": "web.fetch"},                                    │
│      {"id": "mcp.tool.execute"}                              │
│    ],                                                        │
│    "limits": {                                               │
│      "system.command.execute": {                             │
│        "allowed_commands": ["git", "npm", "node", "ls"],     │
│        "blocked_patterns": ["rm -rf", "sudo", "chmod 777"]   │
│      }                                                       │
│    }                                                         │
│  }                                                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
               Any OAP-compliant provider
          ┌────────────────┼────────────────┐
          │                │                │
     Your own         APort (ref.      Other future
     evaluator        implementation)  implementations
```

**手动创建 passport：**

OAP passport 本质上就是一个 JSON 文件。你可以按照 [OAP 规范](https://github.com/aporthq/aport-spec/blob/main/oap/oap-spec.md) 手动创建它，并用 [JSON schema](https://github.com/aporthq/aport-spec/blob/main/oap/passport-schema.json) 对其进行校验。模板可参考 [examples](https://github.com/aporthq/aport-spec/tree/main/oap/examples) 目录。

**使用 APort 作为参考实现：**

[APort Agent Guardrails](https://github.com/aporthq/aport-agent-guardrails) 是一个开源（Apache 2.0）的 OAP provider 实现。它负责 passport 创建、本地评估，以及可选的托管 API 评估。

```bash
pip install aport-agent-guardrails
aport setup --framework deerflow
```

这会创建：
- `~/.aport/deerflow/config.yaml` —— evaluator 配置（本地或 API 模式）
- `~/.aport/deerflow/aport/passport.json` —— 带有 capabilities 和 limits 的 OAP passport

**config.yaml（使用 APort 作为 provider）：**
```yaml
guardrails:
  enabled: true
  provider:
    use: aport_guardrails.providers.generic:OAPGuardrailProvider
```

**config.yaml（使用你自己的 OAP provider）：**
```yaml
guardrails:
  enabled: true
  provider:
    use: my_oap_provider:MyOAPProvider
    config:
      passport_path: ./my-passport.json
```

任何接受 `framework` 作为 kwarg 且实现了 `evaluate`/`aevaluate` 的 provider 都能工作。OAP 标准定义的是 passport 格式和决策代码；DeerFlow 不关心究竟由哪个 provider 来解析它们。

**passport 控制的内容：**

| Passport 字段 | 作用 | 示例 |
|---|---|---|
| `capabilities[].id` | agent 可以使用哪些工具类别 | `system.command.execute`, `data.file.write` |
| `limits.*.allowed_commands` | 哪些命令被允许 | `["git", "npm", "node"]`，或使用 `["*"]` 表示允许全部 |
| `limits.*.blocked_patterns` | 永远拒绝的模式 | `["rm -rf", "sudo", "chmod 777"]` |
| `status` | 总开关 | `active`, `suspended`, `revoked` |

**评估模式（取决于 provider）：**

OAP provider 可以支持不同的评估模式。例如，APort 参考实现支持：

| 模式 | 工作方式 | 网络 | 延迟 |
|---|---|---|---|
| **本地** | 在本地评估 passport（bash 脚本）。 | 无 | ~300ms |
| **API** | 将 passport + context 发送到托管 evaluator。返回已签名决策。 | 是 | ~65ms |

自定义 OAP provider 可以实现任意评估策略——DeerFlow middleware 并不关心 provider 如何做出决策。

**试一试：**
1. 按上文完成安装和设置
2. 启动 DeerFlow，并提问：“Create a file called test.txt with content hello”
3. 然后再问：“Now delete it using bash rm -rf”
4. Guardrail 会阻止它：`oap.blocked_pattern: Command contains blocked pattern: rm -rf`

### 选项 3：自定义 Provider（完全自定义）

任何实现了 `evaluate(request)` 和 `aevaluate(request)` 方法的 Python 类都可以使用。无需基类，也无需继承——它采用的是结构化协议。

```python
# my_guardrail.py

class MyGuardrailProvider:
    name = "my-company"

    def evaluate(self, request):
        from deerflow.guardrails.provider import GuardrailDecision, GuardrailReason

        # Example: block any bash command containing "delete"
        if request.tool_name == "bash" and "delete" in str(request.tool_input):
            return GuardrailDecision(
                allow=False,
                reasons=[GuardrailReason(code="custom.blocked", message="delete not allowed")],
                policy_id="custom.v1",
            )
        return GuardrailDecision(allow=True, reasons=[GuardrailReason(code="oap.allowed")])

    async def aevaluate(self, request):
        return self.evaluate(request)
```

**config.yaml：**
```yaml
guardrails:
  enabled: true
  provider:
    use: my_guardrail:MyGuardrailProvider
```

请确保 `my_guardrail.py` 位于 Python path 中（例如 backend 目录下，或已安装为一个 package）。

**试一试：**
1. 在 backend 目录中创建 `my_guardrail.py`
2. 添加配置
3. 启动 DeerFlow，并提问：“Use bash to delete test.txt”
4. 你的 provider 会阻止它

## 实现一个 Provider

### 必需接口

```
┌──────────────────────────────────────────────────┐
│              GuardrailProvider Protocol            │
│                                                   │
│  name: str                                        │
│                                                   │
│  evaluate(request: GuardrailRequest)              │
│      -> GuardrailDecision                         │
│                                                   │
│  aevaluate(request: GuardrailRequest)   (async)   │
│      -> GuardrailDecision                         │
└──────────────────────────────────────────────────┘

┌──────────────────────────┐    ┌──────────────────────────┐
│     GuardrailRequest      │    │    GuardrailDecision      │
│                           │    │                           │
│  tool_name: str           │    │  allow: bool              │
│  tool_input: dict         │    │  reasons: [GuardrailReason]│
│  agent_id: str | None     │    │  policy_id: str | None    │
│  thread_id: str | None    │    │  metadata: dict           │
│  is_subagent: bool        │    │                           │
│  timestamp: str           │    │  GuardrailReason:         │
│                           │    │    code: str              │
└──────────────────────────┘    │    message: str           │
                                └──────────────────────────┘
```

### DeerFlow 工具名称

这些是你的 provider 在 `request.tool_name` 中会看到的工具名称：

| 工具 | 作用 |
|---|---|
| `bash` | Shell 命令执行 |
| `write_file` | 创建/覆盖文件 |
| `str_replace` | 编辑文件（查找并替换） |
| `read_file` | 读取文件内容 |
| `ls` | 列出目录 |
| `web_search` | Web 搜索查询 |
| `web_fetch` | 获取 URL 内容 |
| `image_search` | 图片搜索 |
| `present_files` | 向用户展示文件 |
| `view_image` | 显示图片 |
| `ask_clarification` | 向用户提问 |
| `task` | 委派给 subagent |
| `mcp__*` | MCP 工具（动态） |

### OAP 原因代码

以下是 [OAP specification](https://github.com/aporthq/aport-spec) 使用的标准代码：

| Code | 含义 |
|---|---|
| `oap.allowed` | 工具调用已授权 |
| `oap.tool_not_allowed` | 工具不在 allowlist 中 |
| `oap.command_not_allowed` | 命令不在 `allowed_commands` 中 |
| `oap.blocked_pattern` | 命令命中了被阻止的模式 |
| `oap.limit_exceeded` | 操作超出限制 |
| `oap.passport_suspended` | Passport 状态为 suspended/revoked |
| `oap.evaluator_error` | Provider 崩溃（fail-closed） |

### Provider 加载

DeerFlow 通过 `resolve_variable()` 加载 provider——这与 models、tools 和 sandbox providers 使用的是同一套机制。`use:` 字段是 Python 类路径：`package.module:ClassName`。

如果设置了 `config:`，provider 会以 `**config` kwargs 实例化，并且始终会额外注入 `framework="deerflow"`。为保持前向兼容，请接受 `**kwargs`：

```python
class YourProvider:
    def __init__(self, framework: str = "generic", **kwargs):
        # framework="deerflow" tells you which config dir to use
        ...
```

## 配置参考

```yaml
guardrails:
  # Enable/disable guardrail middleware (default: false)
  enabled: true

  # Block tool calls if provider raises an exception (default: true)
  fail_closed: true

  # Passport reference -- passed as request.agent_id to the provider.
  # File path, hosted agent ID, or null (provider resolves from its config).
  passport: null

  # Provider: loaded by class path via resolve_variable
  provider:
    use: deerflow.guardrails.builtin:AllowlistProvider
    config:  # optional kwargs passed to provider.__init__
      denied_tools: ["bash"]
```

## 测试

```bash
cd backend
uv run python -m pytest tests/test_guardrail_middleware.py -v
```

共 25 个测试，覆盖：
- AllowlistProvider：允许、拒绝、同时使用 allowlist+denylist、异步路径
- GuardrailMiddleware：允许透传、使用 OAP 代码拒绝、fail-closed、fail-open、passport 转发、空 reasons 回退、空工具名、协议 isinstance 检查
- 异步路径：`awrap_tool_call` 的 allow、deny、fail-closed、fail-open
- GraphBubbleUp：LangGraph 控制信号会继续传播（不会被捕获）
- 配置：默认值、from_dict、singleton 的加载/重置

## 文件

```
packages/harness/deerflow/guardrails/
    __init__.py              # Public exports
    provider.py              # GuardrailProvider protocol, GuardrailRequest, GuardrailDecision
    middleware.py             # GuardrailMiddleware (AgentMiddleware subclass)
    builtin.py               # AllowlistProvider (zero deps)

packages/harness/deerflow/config/
    guardrails_config.py     # GuardrailsConfig Pydantic model + singleton

packages/harness/deerflow/agents/middlewares/
    tool_error_handling_middleware.py  # Registers GuardrailMiddleware in chain

config.example.yaml          # Three provider options documented
tests/test_guardrail_middleware.py  # 25 tests
docs/GUARDRAILS.md           # This file
```
