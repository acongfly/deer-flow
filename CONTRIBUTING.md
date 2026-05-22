# 为 DeerFlow 做贡献

感谢你有兴趣为 DeerFlow 做贡献！本指南将帮助你搭建开发环境并了解我们的开发工作流。

## 开发环境搭建

我们提供两种开发环境。为了获得最一致、最省心的体验，**推荐使用 Docker**。

### 方案 1：Docker 开发（推荐）

Docker 提供一致且隔离的环境，并且所有依赖都已预先配置。你无需在本地机器上安装 Node.js、Python 或 nginx。

#### 前置条件

- Docker Desktop 或 Docker Engine
- pnpm（用于缓存优化）

#### 搭建步骤

1. **配置应用**：
   ```bash
   # Copy example configuration
   cp config.example.yaml config.yaml

   # Set your API keys
   export OPENAI_API_KEY="your-key-here"
   # or edit config.yaml directly
   ```

2. **初始化 Docker 环境**（仅首次需要）：
   ```bash
   make docker-init
   ```
   这将会：
   - 构建 Docker 镜像
   - 安装前端依赖（pnpm）
   - 安装后端依赖（uv）
   - 与宿主机共享 pnpm 缓存以加快构建速度

3. **启动开发服务**：
   ```bash
   make docker-start
   ```
   `make docker-start` 会读取 `config.yaml`，并且仅在 provisioner/Kubernetes 沙箱模式下启动 `provisioner`。

   所有服务都会以启用热重载的方式启动：
   - 前端更改会自动重新加载
   - 后端更改会触发自动重启
   - 由 Gateway 托管的 LangGraph 兼容运行时支持热重载

4. **访问应用**：
   - Web 界面：http://localhost:2026
   - API Gateway：http://localhost:2026/api/*
   - LangGraph 兼容 API：http://localhost:2026/api/langgraph/*

#### Docker 命令

```bash
# Build the custom k3s image (with pre-cached sandbox image)
make docker-init
# Start Docker services (mode-aware, localhost:2026)
make docker-start
# Stop Docker development services
make docker-stop
# View Docker development logs
make docker-logs
# View Docker frontend logs
make docker-logs-frontend
# View Docker gateway logs
make docker-logs-gateway
```

如果你所在网络环境下 Docker 构建较慢，可以在运行 `make docker-init` 或 `make docker-start` 之前覆盖默认的软件包镜像源：

```bash
export UV_INDEX_URL=https://pypi.org/simple
export NPM_REGISTRY=https://registry.npmjs.org
```

#### 推荐的宿主机资源

可将下表作为开发与评审环境的实用起点：

| 场景 | 起始配置 | 推荐配置 | 说明 |
|---------|-----------|------------|-------|
| 单机运行 `make dev` | 4 vCPU，8 GB RAM | 8 vCPU，16 GB RAM | 当 DeerFlow 使用托管模型 API 时效果最佳。 |
| `make docker-start` 评审环境 | 4 vCPU，8 GB RAM | 8 vCPU，16 GB RAM | Docker 镜像构建和沙箱容器需要更多余量。 |
| 共享 Linux 测试服务器 | 8 vCPU，16 GB RAM | 16 vCPU，32 GB RAM | 更适合更重的多 Agent 运行或多个评审者同时使用。 |

`2 vCPU / 4 GB` 的环境通常无法可靠启动，或在 DeerFlow 的正常工作负载下变得无响应。

#### Linux：Docker 守护进程 permission denied

如果在 Linux 上运行 `make docker-init`、`make docker-start` 或 `make docker-stop` 失败，并出现如下错误，你当前用户很可能没有权限访问 Docker 守护进程套接字：

```text
unable to get image 'deer-flow-gateway': permission denied while trying to connect to the Docker daemon socket at unix:///var/run/docker.sock
```

推荐修复方式：将当前用户加入 `docker` 用户组，这样无需 `sudo` 即可使用 Docker 命令。

1. 确认 `docker` 用户组存在：
   ```bash
   getent group docker
   ```
2. 将当前用户加入 `docker` 用户组：
   ```bash
   sudo usermod -aG docker $USER
   ```
3. 让新的用户组成员关系生效。最可靠的方式是完全注销后重新登录。如果你想直接刷新当前 shell 会话，请运行：
   ```bash
   newgrp docker
   ```
4. 验证 Docker 访问权限：
   ```bash
   docker ps
   ```
5. 重新执行 DeerFlow 命令：
   ```bash
   make docker-stop
   make docker-start
   ```

如果在执行 `usermod` 之后 `docker ps` 仍然报权限错误，请先完全注销并重新登录，再重试。

#### Docker 架构

```
Host Machine
  ↓
Docker Compose (deer-flow-dev)
  ├→ nginx (port 2026) ← Reverse proxy
  ├→ web (port 3000) ← Frontend with hot-reload
  ├→ gateway (port 8001) ← Gateway API + LangGraph-compatible runtime with hot-reload
  └→ provisioner (optional, port 8002) ← Started only in provisioner/K8s sandbox mode
```

**Docker 开发的优势**：
- ✅ 不同机器间环境一致
- ✅ 无需在本地安装 Node.js、Python 或 nginx
- ✅ 依赖与服务相互隔离
- ✅ 易于清理与重置
- ✅ 所有服务都支持热重载
- ✅ 更接近生产环境

### 方案 2：本地开发

如果你更喜欢直接在本机运行服务：

#### 前置条件

检查你是否已安装所有必需工具：

```bash
make check
```

所需工具：
- Node.js 22+
- pnpm
- uv（Python 包管理器）
- nginx

#### 搭建步骤

1. **配置应用**（与上面的 Docker 搭建相同）

2. **安装依赖**（这也会设置 pre-commit hooks）：
   ```bash
   make install
   ```

3. **运行开发服务器**（通过 nginx 启动所有服务）：
   ```bash
   make dev
   ```

4. **访问应用**：
   - Web 界面：http://localhost:2026
   - 所有 API 请求都会通过 nginx 自动代理

#### 手动控制服务

如果你需要分别启动各个服务：

1. **启动后端服务**：
   ```bash
   # Terminal 1: Start Gateway API + embedded agent runtime (port 8001)
   cd backend
   make dev

   # Terminal 2: Start Frontend (port 3000)
   cd frontend
   pnpm dev
   ```

2. **启动 nginx**：
   ```bash
   make nginx
   # or directly: nginx -c $(pwd)/docker/nginx/nginx.local.conf -g 'daemon off;'
   ```

3. **访问应用**：
   - Web 界面：http://localhost:2026

#### Nginx 配置

nginx 配置提供：
- 端口 2026 上的统一入口
- 将 `/api/langgraph/*` 重写到 Gateway 的 LangGraph 兼容 API（8001）
- 将其他 `/api/*` 端点路由到 Gateway API（8001）
- 将非 API 请求路由到 Frontend（3000）
- 同源 API 路由；分离源或端口转发的浏览器客户端应使用 Gateway 的 `GATEWAY_CORS_ORIGINS` 允许列表
- 为实时 Agent 响应提供 SSE/流式支持
- 针对长时间运行操作优化的超时设置

## 项目结构

```
deer-flow/
├── config.example.yaml      # Configuration template
├── extensions_config.example.json  # MCP and Skills configuration template
├── Makefile                 # Build and development commands
├── scripts/
│   └── docker.sh           # Docker management script
├── docker/
│   ├── docker-compose-dev.yaml  # Docker Compose configuration
│   └── nginx/
│       ├── nginx.conf      # Nginx config for Docker
│       └── nginx.local.conf # Nginx config for local dev
├── backend/                 # Backend application
│   ├── src/
│   │   ├── gateway/        # Gateway API and LangGraph-compatible runtime (port 8001)
│   │   ├── agents/         # LangGraph agent runtime used by Gateway
│   │   ├── mcp/            # Model Context Protocol integration
│   │   ├── skills/         # Skills system
│   │   └── sandbox/        # Sandbox execution
│   ├── docs/               # Backend documentation
│   └── Makefile            # Backend commands
├── frontend/               # Frontend application
│   └── Makefile            # Frontend commands
└── skills/                 # Agent skills
    ├── public/             # Public skills
    └── custom/             # Custom skills
```

## 架构

```
Browser
  ↓
Nginx (port 2026) ← Unified entry point
  ├→ Frontend (port 3000) ← / (non-API requests)
  └→ Gateway API (port 8001) ← /api/* and /api/langgraph/* (LangGraph-compatible agent interactions)
```

## 开发工作流

1. **创建功能分支**：
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **进行更改**，热重载会自动生效

3. **格式化并检查代码**（CI 会拒绝未格式化的代码）：
   ```bash
   # Backend
   cd backend
   make format   # ruff check --fix + ruff format

   # Frontend
   cd frontend
   pnpm format:write   # Prettier
   ```

4. **充分测试你的更改**

5. **提交你的更改**：
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   ```

6. **推送并创建 Pull Request**：
   ```bash
   git push origin feature/your-feature-name
   ```

## 测试

```bash
# Backend tests
cd backend
make test

# Frontend unit tests
cd frontend
make test

# Frontend E2E tests (requires Chromium; builds and auto-starts the Next.js production server)
cd frontend
make test-e2e
```

### PR 回归检查

每个 Pull Request 都会触发以下 CI 工作流：

- **后端单元测试** — [.github/workflows/backend-unit-tests.yml](.github/workflows/backend-unit-tests.yml)
- **前端单元测试** — [.github/workflows/frontend-unit-tests.yml](.github/workflows/frontend-unit-tests.yml)
- **前端 E2E 测试** — [.github/workflows/e2e-tests.yml](.github/workflows/e2e-tests.yml)（仅当 `frontend/` 文件发生更改时触发）

## 代码风格

- **后端（Python）**：我们使用 `ruff` 进行 lint 和格式化。提交前请运行 `make format`。
- **前端（TypeScript）**：我们使用 ESLint 和 Prettier。提交前请运行 `pnpm format:write`。
- CI 会强制检查格式——未格式化代码的 PR 将无法通过 lint 检查。

## 文档

- [配置指南](backend/docs/CONFIGURATION.md) - 安装与配置
- [架构概览](backend/CLAUDE.md) - 技术架构
- [MCP 搭建指南](backend/docs/MCP_SERVER.md) - Model Context Protocol 配置

## 需要帮助？

- 查看现有的 [Issues](https://github.com/bytedance/deer-flow/issues)
- 阅读[文档](backend/docs/)
- 在 [Discussions](https://github.com/bytedance/deer-flow/discussions) 中提问

## 许可证

通过向 DeerFlow 贡献代码，你同意你的贡献将依据 [MIT 许可证](./LICENSE) 进行许可。
