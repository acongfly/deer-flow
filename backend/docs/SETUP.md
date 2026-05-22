# 设置指南

DeerFlow 的快速设置说明。

## 配置设置

DeerFlow 使用 YAML 配置文件，该文件应放置在**项目根目录**中。

### 步骤

1. **进入项目根目录**：
   ```bash
   cd /path/to/deer-flow
   ```

2. **复制示例配置**：
   ```bash
   cp config.example.yaml config.yaml
   ```

3. **编辑配置**：
   ```bash
   # Option A: Set environment variables (recommended)
   export OPENAI_API_KEY="your-key-here"

   # Optional: pin the project root when running from another directory
   export DEER_FLOW_PROJECT_ROOT="/path/to/deer-flow"

   # Option B: Edit config.yaml directly
   vim config.yaml  # or your preferred editor
   ```

4. **验证配置**：
   ```bash
   cd backend
   python -c "from deerflow.config import get_app_config; print('✓ Config loaded:', get_app_config().models[0].name)"
   ```

## 重要说明

- **位置**：`config.yaml` 应放在 `deer-flow/`（项目根目录）
- **Git**：`config.yaml` 会被 git 自动忽略（因为其中包含 secrets）
- **运行时根目录**：如果 DeerFlow 可能从项目根目录之外启动，请设置 `DEER_FLOW_PROJECT_ROOT`
- **运行时数据**：状态默认保存在项目根目录下的 `.deer-flow`；如需迁移位置，请设置 `DEER_FLOW_HOME`
- **Skills**：skills 默认位于项目根目录下的 `skills/`；如需迁移位置，请设置 `DEER_FLOW_SKILLS_PATH` 或 `skills.path`

## 配置文件查找位置

backend 会按以下顺序查找 `config.yaml`：

1. 代码中显式传入的 `config_path` 参数
2. `DEER_FLOW_CONFIG_PATH` 环境变量（如果已设置）
3. `config.yaml` 位于 `DEER_FLOW_PROJECT_ROOT` 下；若未设置 `DEER_FLOW_PROJECT_ROOT`，则位于当前工作目录
4. 为兼容 monorepo 而保留的旧版 backend/仓库根目录位置

**推荐方式**：将 `config.yaml` 放在项目根目录（`deer-flow/config.yaml`）。

## Sandbox 设置（可选但推荐）

如果你计划使用基于 Docker/Container 的 sandbox（在 `config.yaml` 中配置为 `sandbox.use: deerflow.community.aio_sandbox:AioSandboxProvider`），强烈建议提前拉取容器镜像：

```bash
# From project root
make setup-sandbox
```

**为什么要提前拉取？**
- sandbox 镜像（约 500MB+）会在首次使用时拉取，可能导致长时间等待
- 提前拉取可以提供清晰的进度提示
- 避免首次使用 agent 时产生困惑

如果跳过这一步，镜像会在第一次执行 agent 时自动拉取，具体耗时取决于你的网络速度，可能需要数分钟。

## 故障排查

### 找不到配置文件

```bash
# Check where the backend is looking
cd deer-flow/backend
python -c "from deerflow.config.app_config import AppConfig; print(AppConfig.resolve_config_path())"
```

如果仍然找不到配置：
1. 确认你已经将 `config.example.yaml` 复制为 `config.yaml`
2. 确认你位于项目根目录，或已设置 `DEER_FLOW_PROJECT_ROOT`
3. 检查文件是否存在：`ls -la config.yaml`

### 权限被拒绝

```bash
chmod 600 ../config.yaml  # Protect sensitive configuration
```

## 另请参阅

- [Configuration Guide](CONFIGURATION.md) - 详细配置选项
- [Architecture Overview](../CLAUDE.md) - 系统架构
