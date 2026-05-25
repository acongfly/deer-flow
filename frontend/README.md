# DeerFlow Frontend（前端）

像最初的 DeerFlow 1.0 一样，我们希望为社区提供一个极简、易用，并且拥有更现代、更灵活架构的 Web 界面。

## 技术栈

- **框架**：[Next.js 16](https://nextjs.org/) 与 [App Router](https://nextjs.org/docs/app)
- **UI**：[React 19](https://react.dev/)、[Tailwind CSS 4](https://tailwindcss.com/)、[Shadcn UI](https://ui.shadcn.com/)、[MagicUI](https://magicui.design/) 和 [React Bits](https://reactbits.dev/)
- **AI 集成**：[LangGraph SDK](https://www.npmjs.com/package/@langchain/langgraph-sdk) 与 [Vercel AI Elements](https://vercel.com/ai-sdk/ai-elements)

## 快速开始

### 前置条件

- Node.js 22+
- pnpm 10.26.2+

### 安装

```bash
# Install dependencies
pnpm install

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration
```

### 开发

```bash
# Start development server
pnpm dev

# The app will be available at http://localhost:3000
```

### 构建与测试

```bash
# Type check
pnpm typecheck

# Check formatting
pnpm format

# Apply formatting
pnpm format:write

# Lint
pnpm lint

# Run unit tests
pnpm test

# One-time setup: install Playwright Chromium browser
pnpm exec playwright install chromium

# Run E2E tests (builds and starts production server automatically)
pnpm test:e2e

# Build for production
pnpm build

# Start production server
pnpm start
```

## 站点地图

```
├── /                    # Landing page
├── /chats               # Chat list
├── /chats/new           # New chat page
└── /chats/[thread_id]   # A specific chat page
```

## 配置

### 环境变量

关键环境变量（完整列表见 `.env.example`）：

```bash
# Backend API URL (optional, uses local Next.js/nginx proxy by default)
NEXT_PUBLIC_BACKEND_BASE_URL="http://localhost:8001"
# LangGraph-compatible API URL (optional, uses local Next.js/nginx proxy by default)
NEXT_PUBLIC_LANGGRAPH_BASE_URL="http://localhost:8001/api"
```

## 项目结构

```
tests/
├── e2e/                    # E2E tests (Playwright, Chromium, mocked backend)
└── unit/                   # Unit tests (mirrors src/ layout)
src/
├── app/                    # Next.js App Router pages
│   ├── api/                # API routes
│   ├── workspace/          # Main workspace pages
│   └── mock/               # Mock/demo pages
├── components/             # React components
│   ├── ui/                 # Reusable UI components
│   ├── workspace/          # Workspace-specific components
│   ├── landing/            # Landing page components
│   └── ai-elements/        # AI-related UI elements
├── core/                   # Core business logic
│   ├── api/                # API client & data fetching
│   ├── artifacts/          # Artifact management
│   ├── config/              # App configuration
│   ├── i18n/               # Internationalization
│   ├── mcp/                # MCP integration
│   ├── messages/           # Message handling
│   ├── models/             # Data models & types
│   ├── settings/           # User settings
│   ├── skills/             # Skills system
│   ├── threads/            # Thread management
│   ├── todos/              # Todo system
│   └── utils/              # Utility functions
├── hooks/                  # Custom React hooks
├── lib/                    # Shared libraries & utilities
├── server/                 # Server-side code
│   └── better-auth/        # Authentication setup and session helpers
└── styles/                 # Global styles
```

## 脚本

| 命令 | 说明 |
| ------------------- | --------------------------------------- |
| `pnpm dev`          | 使用 Turbopack 启动开发服务器 |
| `pnpm build`        | 生产构建 |
| `pnpm start`        | 启动生产服务器 |
| `pnpm test`         | 使用 Vitest 运行 unit tests |
| `pnpm test:e2e`     | 使用 Playwright 运行 E2E tests |
| `pnpm format`       | 使用 Prettier 检查格式 |
| `pnpm format:write` | 使用 Prettier 应用格式化 |
| `pnpm lint`         | 运行 ESLint |
| `pnpm lint:fix`     | 修复 ESLint 问题 |
| `pnpm typecheck`    | 运行 TypeScript 类型检查 |
| `pnpm check`        | 同时运行 lint 和 typecheck |

## 开发说明

- 使用 pnpm workspaces（见 package.json 中的 `packageManager`）
- 开发环境默认启用 Turbopack，以加快构建速度
- 可以通过 `SKIP_ENV_VALIDATION=1` 跳过环境校验（对 Docker 很有用）
- Backend API URL 是可选的；开发环境默认使用 nginx proxy

## 许可证

MIT License。详情见 [LICENSE](../LICENSE)。
