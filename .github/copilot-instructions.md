# DeerFlow Copilot 使用指南

本文件是此仓库的默认操作指南。优先遵循本文件，仅在本文件不完整或不正确时才搜索代码库。

## 1）仓库概要

DeerFlow 是一个全栈"超级 Agent 框架"。

- 后端：Python 3.12，LangGraph + FastAPI 网关，沙箱/工具系统，记忆，MCP 集成。
- 前端：Next.js 16 + React 19 + TypeScript + pnpm。
- 本地开发入口：根目录 `Makefile` 在 `http://localhost:2026` 启动后端 + 前端 + nginx。
- Docker 开发入口：`make docker-*`（从 `config.yaml` 进行模式感知的 provisioner 启动）。

当前仓库规模为中大型（后端服务、前端应用、docker 栈、skills 库、文档）。

## 2）运行时和工具链要求

在此仓库中 macOS 上已验证：

- Node.js `>=22`（已验证 Node `23.11.0`）
- pnpm（仓库期望 pnpm 10 生成的锁文件；已验证 pnpm `10.26.2` 和 `10.15.0`）
- Python `>=3.12`（CI 使用 `3.12`）
- `uv`（已验证 `0.7.20`）
- `nginx`（`make dev` 统一本地端点所必需）

除非命令明确说明，否则始终从仓库根目录运行。

## 3）构建/测试/Lint/运行 - 已验证命令序列

以下命令已在此仓库中执行和验证。

### A. 引导和安装

1. 检查先决条件：

```bash
make check
```

观察结果：安装了所需工具时通过。

2. 安装依赖（推荐顺序：先后端后前端，如 `make install` 所实现）：

```bash
make install
```

### B. 后端 CI 等效验证

从 `backend/` 运行：

```bash
make lint
make test
```

已验证结果：

- `make lint`：通过（`ruff check .`）
- `make test`：通过（`277 passed, 15 warnings in ~76.6s`）

CI 对应：

- `.github/workflows/backend-unit-tests.yml` 在拉取请求时运行。
- CI 在 `backend/` 中执行 `uv sync --group dev`，然后 `make lint`，然后 `make test`。

### C. 前端验证

从 `frontend/` 运行。

推荐的可靠序列：

```bash
pnpm lint
pnpm typecheck
BETTER_AUTH_SECRET=local-dev-secret pnpm build
```

观察到的失败模式和解决方案：

- `pnpm build` 在生产模式环境验证中没有 `BETTER_AUTH_SECRET` 会失败。
- 解决方案：设置 `BETTER_AUTH_SECRET`（最佳）或设置 `SKIP_ENV_VALIDATION=1`。
- 即使使用 `SKIP_ENV_VALIDATION=1`，Better Auth 仍可能在日志中警告/报错默认密钥；推荐设置真实的非默认密钥。
- `pnpm check` 目前失败（`next lint` 调用不兼容，解析到无效目录）。不要依赖 `pnpm check`；显式运行 `pnpm lint` 和 `pnpm typecheck`。

### D. 本地运行（所有服务）

从根目录：

```bash
make dev
```

行为：

- 首先停止现有本地服务。
- 启动 LangGraph（`2024`）、Gateway（`8001`）、Frontend（`3000`）、nginx（`2026`）。
- 统一应用端点：`http://localhost:2026`。
- 日志：`logs/langgraph.log`、`logs/gateway.log`、`logs/frontend.log`、`logs/nginx.log`。

停止服务：

```bash
make stop
```

如果工具会话/超时中断了 `make dev`，再次运行 `make stop` 以确保清理。

### E. 配置引导

从根目录：

```bash
make config
```

重要行为：

- 如果 `config.yaml`（或 `config.yml`/`configure.yml`）已存在，此命令会故意中止。
- 仅在全新克隆的首次设置时使用 `make config`。

## 4）最小化失败的命令顺序

对于本地代码更改，使用以下精确顺序：

1. `make check`
2. `make install`（如果前端因代理错误失败，在未设置代理变量的情况下重新运行前端安装）
3. 后端检查：`cd backend && make lint && make test`
4. 前端检查：`cd frontend && pnpm lint && pnpm typecheck`
5. 前端构建（如果有 UI 更改或对发布敏感的更改）：`BETTER_AUTH_SECRET=... pnpm build`

始终在打开 PR 前运行后端 lint/tests，因为这是 CI 强制执行的。

## 5）项目布局和架构（高价值路径）

根级编排和配置：

- `Makefile` - 主要本地/开发/docker 命令入口
- `config.example.yaml` - 主应用配置模板
- `config.yaml` - 本地活动配置（gitignored）
- `docker/docker-compose-dev.yaml` - Docker 开发拓扑
- `.github/workflows/backend-unit-tests.yml` - PR 验证工作流

后端核心：

- `backend/packages/harness/deerflow/agents/` - lead agent、中间件链、记忆
- `backend/app/gateway/` - FastAPI 网关 API
- `backend/packages/harness/deerflow/sandbox/` - 沙箱提供者 + 工具包装器
- `backend/packages/harness/deerflow/subagents/` - 子代理注册/执行
- `backend/packages/harness/deerflow/mcp/` - MCP 集成
- `backend/langgraph.json` - 图入口（`deerflow.agents:make_lead_agent`）
- `backend/pyproject.toml` - Python 依赖和 `requires-python`
- `backend/ruff.toml` - lint/format 策略
- `backend/tests/` - 后端单元测试和集成测试

前端核心：

- `frontend/src/app/` - Next.js 路由/页面
- `frontend/src/components/` - UI 组件
- `frontend/src/core/` - 应用逻辑（threads、tools、API、models）
- `frontend/src/env.js` - 环境模式/验证（对构建行为至关重要）
- `frontend/package.json` - 脚本/依赖
- `frontend/eslint.config.js` - lint 规则
- `frontend/tsconfig.json` - TypeScript 配置

技能和资源：

- `skills/public/` - 由 Agent 运行时加载的内置技能包

## 6）预提交/验证期望

在提交更改前，至少运行：

- 后端：`cd backend && make lint && make test`
- 前端（如有更改）：`cd frontend && pnpm lint && pnpm typecheck`
- 更改环境/认证/路由/构建敏感文件时的前端构建：`BETTER_AUTH_SECRET=... pnpm build`

如果更改了编排/配置（`Makefile`、`docker/*`、`config*.yaml`），还要运行 `make dev` 并验证四个服务启动。

## 7）非显而易见的依赖和注意事项

- 代理环境变量可能悄悄破坏前端网络操作（`pnpm install`/注册表访问）。
- `BETTER_AUTH_SECRET` 对于可靠的前端生产构建验证实际上是必需的。
- Next.js 可能警告多个锁文件和工作区根推断；这目前是警告，不是构建阻碍。
- `make config` 在配置已存在时设计为非幂等的。
- `make dev` 包括进程清理，如果被中断可能会发出关闭日志/噪音；这是预期行为。

## 8）根目录清单（快速参考）

重要的根目录条目：

- `.github/`
- `backend/`
- `frontend/`
- `docker/`
- `skills/`
- `scripts/`
- `docs/`
- `README.md`
- `CONTRIBUTING.md`
- `Makefile`
- `config.example.yaml`
- `extensions_config.example.json`

## 9）指令优先级

首先信任此入门指南。

仅在以下情况下进行广泛的仓库搜索（`grep/find/代码搜索`）：

- 你需要此处未列出的文件级实现细节，
- 此处的命令失败，你需要更新的替代行为，
- 或自本文件编写以来 CI/工作流定义已发生变化。
