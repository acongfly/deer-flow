# Langfuse Tracing 实施计划

**目标：** 为 DeerFlow 增加可选的 Langfuse observability 支持，同时保留现有的 LangSmith tracing，并允许两个 provider 同时启用。

**架构：** 将 tracing 配置从仅支持 LangSmith 的单一结构扩展为多 provider 配置；添加一个 tracing callback factory，根据环境变量构建 0 个、1 个或 2 个 callback；并更新 model 创建逻辑以附加这些 callback。如果某个 provider 被显式启用但配置错误或初始化失败，那么在 model 创建期间初始化 tracing 时应以清晰错误失败，并明确指出是哪个 provider。

**技术栈：** Python 3.12、Pydantic、LangChain callbacks、LangSmith、Langfuse、pytest

---

### 任务 1：添加失败中的 tracing config 测试

**文件：**
- 修改：`backend/tests/test_tracing_config.py`

**步骤 1：编写失败中的测试**

添加以下覆盖场景的测试：
- 仅 Langfuse 的配置解析
- 双 provider 解析
- 显式启用但缺少必需的 Langfuse 字段
- 不依赖仅限 LangSmith helper 的 provider 启用检测

**步骤 2：运行测试并确认其失败**

运行：`cd backend && uv run pytest tests/test_tracing_config.py -q`
预期：FAIL，因为当前 tracing config 只支持 LangSmith。

**步骤 3：编写最小实现**

更新 tracing config 代码，以表示多个 provider，并暴露测试所需的 helper functions。

**步骤 4：再次运行测试并确认通过**

运行：`cd backend && uv run pytest tests/test_tracing_config.py -q`
预期：PASS

### 任务 2：添加失败中的 callback factory 和 model attachment 测试

**文件：**
- 修改：`backend/tests/test_model_factory.py`
- 新建：`backend/tests/test_tracing_factory.py`

**步骤 1：编写失败中的测试**

添加以下覆盖场景的测试：
- LangSmith callback 创建
- Langfuse callback 创建
- 双 callback 创建
- 当显式启用的 provider 无法初始化时，启动失败
- model factory 会将所有 tracing callbacks 附加到 model callbacks

**步骤 2：运行测试并确认其失败**

运行：`cd backend && uv run pytest tests/test_model_factory.py tests/test_tracing_factory.py -q`
预期：FAIL，因为目前没有 provider factory，而且 model 创建只会附加 LangSmith。

**步骤 3：编写最小实现**

创建 tracing callback factory 模块，并更新 model factory 以使用它。

**步骤 4：再次运行测试并确认通过**

运行：`cd backend && uv run pytest tests/test_model_factory.py tests/test_tracing_factory.py -q`
预期：PASS

### 任务 3：接入依赖与文档

**文件：**
- 修改：`backend/packages/harness/pyproject.toml`
- 修改：`README.md`
- 修改：`backend/README.md`

**步骤 1：更新依赖**

将 `langfuse` 添加到 harness dependencies 中。

**步骤 2：更新文档**

记录以下内容：
- Langfuse 环境变量
- 双 provider 行为
- 显式启用 provider 时的失败行为

**步骤 3：运行定向验证**

运行：`cd backend && uv run pytest tests/test_tracing_config.py tests/test_model_factory.py tests/test_tracing_factory.py -q`
预期：PASS

### 任务 4：运行更广泛的回归检查

**文件：**
- 不需要代码改动

**步骤 1：运行相关测试套件**

运行：`cd backend && uv run pytest tests/test_tracing_config.py tests/test_model_factory.py tests/test_tracing_factory.py -q`

**步骤 2：如有需要运行 lint**

运行：`cd backend && uv run ruff check packages/harness/deerflow/config/tracing_config.py packages/harness/deerflow/models/factory.py packages/harness/deerflow/tracing`

**步骤 3：审阅 diff**

运行：`git diff -- backend/packages/harness backend/tests README.md backend/README.md`
