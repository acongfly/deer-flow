# Agents 架构

## 概览

DeerFlow 基于复杂的 agent 架构构建，使用 [LangGraph SDK](https://github.com/langchain-ai/langgraph) 来实现智能、有状态的 AI 交互。本文档概述了 frontend 应用中 agent 系统的架构、模式以及最佳实践。

## 架构概览

### 核心组件

```
┌────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                  │
├────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │ UI Components│───▶│ Thread Hooks │───▶│ LangGraph│  │
│  │              │    │              │    │   SDK    │  │
│  └──────────────┘    └──────────────┘    └──────────┘  │
│         │                    │                  │      │
│         │                    ▼                  │      │
│         │            ┌──────────────┐           │      │
│         └───────────▶│ Thread State │◀──────────┘      │
│                      │  Management  │                  │
│                      └──────────────┘                  │
└────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────┐
│              LangGraph Backend (lead_agent)            │
│  ┌────────────┐  ┌──────────┐  ┌───────────────────┐   │
│  │Main Agent  │─▶│Sub-Agents│─▶│  Tools & Skills   │   │
│  └────────────┘  └──────────┘  └───────────────────┘   │
└────────────────────────────────────────────────────────┘
```

## 项目结构

```
tests/
├── e2e/                    # E2E tests (Playwright, Chromium, mocked backend)
└── unit/                   # Unit tests (mirrors src/ layout, powered by Vitest)
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
├── server/                 # Server-side code (Not available yet)
│   └── better-auth/        # Authentication setup (Not available yet)
└── styles/                 # Global styles
```

### 技术栈

- **LangGraph SDK** (`@langchain/langgraph-sdk@1.5.3`) - agent 编排与流式传输
- **LangChain Core** (`@langchain/core@1.1.15`) - 基础 AI 构建模块
- **TanStack Query** (`@tanstack/react-query@5.90.17`) - server state 管理
- **React Hooks** - thread 生命周期与 state 管理
- **Shadcn UI** - UI 组件
- **MagicUI** - Magic UI 组件
- **React Bits** - React bits 组件

### 交互所有权

- `src/app/workspace/chats/[thread_id]/page.tsx` 负责 composer busy-state 的接线。
- `src/core/threads/hooks.ts` 负责提交前上传状态和 thread 提交。
- `src/hooks/usePoseStream.ts` 是一个被动的 store selector；全局 WebSocket 生命周期仍保留在 `App.tsx` 中。

## 资源

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Core Concepts](https://js.langchain.com/docs/concepts)
- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [Next.js App Router](https://nextjs.org/docs/app)

## 贡献

添加新的 agent 功能时：

1. 遵循既有的项目结构
2. 添加完整的 TypeScript 类型
3. 实现恰当的错误处理
4. 在 `tests/unit/` 下编写 unit tests（使用 `pnpm test` 运行），并在 `tests/e2e/` 下编写 E2E tests（使用 `pnpm test:e2e` 运行）
5. 更新本文档
6. 遵循代码风格指南（ESLint + Prettier）

## 许可证

此 agent 架构是 DeerFlow 项目的一部分。
