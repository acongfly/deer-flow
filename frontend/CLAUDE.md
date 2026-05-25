# CLAUDE.md

此文件为 Claude Code（claude.ai/code）在本仓库中工作时提供指导。

## 项目概览

DeerFlow Frontend 是一个基于 Next.js 16 的 AI agent 系统 Web 界面。它与基于 LangGraph 的 backend 通信，提供基于 thread 的 AI 对话、流式响应、artifacts，以及 skills/tools 系统。

**技术栈**：Next.js 16、React 19、TypeScript 5.8、Tailwind CSS 4、pnpm 10.26.2

## 命令

| 命令 | 用途 |
| ---------------- | ------------------------------------------------- |
| `pnpm dev`       | 使用 Turbopack 启动开发服务器（http://localhost:3000） |
| `pnpm build`     | 生产构建 |
| `pnpm check`     | Lint + 类型检查（提交前运行） |
| `pnpm lint`      | 仅运行 ESLint |
| `pnpm lint:fix`  | 运行 ESLint 并自动修复 |
| `pnpm test`      | 使用 Vitest 运行 unit tests |
| `pnpm test:e2e`  | 使用 Playwright（Chromium）运行 E2E tests |
| `pnpm typecheck` | TypeScript 类型检查（`tsc --noEmit`） |
| `pnpm start`     | 启动生产服务器 |

unit tests 位于 `tests/unit/` 下，并与 `src/` 目录结构对应（例如，`tests/unit/core/api/stream-mode.test.ts` 测试 `src/core/api/stream-mode.ts`）。测试基于 Vitest；通过 `@/` 路径别名导入源码模块。

E2E tests 位于 `tests/e2e/` 下，使用带 Chromium 的 Playwright。它们通过 `page.route()` 网络拦截来 mock 所有 backend API，并测试真实的页面交互（导航、聊天输入、流式响应）。配置文件：`playwright.config.ts`。

## 架构

```
Frontend (Next.js) ──▶ LangGraph SDK ──▶ LangGraph Backend (lead_agent)
                                              ├── Sub-Agents
                                              └── Tools & Skills
```

frontend 是一个有状态的聊天应用。用户会创建 **threads**（对话）、发送消息，并接收流式的 AI 响应。backend 负责编排 agents，这些 agents 可以生成 **artifacts**（文件/代码）和 **todos**。

### 源码布局（`src/`）

- **`app/`** — Next.js App Router。路由：`/`（landing）、`/workspace/chats/[thread_id]`（chat）。
- **`components/`** — React 组件，拆分为：
  - `ui/` — Shadcn UI primitives（自动生成，ESLint 忽略）
  - `ai-elements/` — Vercel AI SDK elements（自动生成，ESLint 忽略）
  - `workspace/` — chat 页面组件（messages、artifacts、settings）
  - `landing/` — landing 页面各区块
- **`core/`** — 业务逻辑，是整个应用的核心：
  - `threads/` — thread 创建、流式传输、state 管理（hooks + types）
  - `api/` — LangGraph client 单例
  - `artifacts/` — artifact 加载与缓存
  - `i18n/` — 国际化（en-US、zh-CN）
  - `settings/` — 存储在 localStorage 中的用户偏好
  - `memory/` — 持久化用户 memory 系统
  - `skills/` — skills 安装与管理
  - `messages/` — message 处理与转换
  - `mcp/` — Model Context Protocol 集成
  - `models/` — TypeScript 类型与数据模型
- **`hooks/`** — 共享的 React hooks
- **`lib/`** — 工具函数（来自 clsx + tailwind-merge 的 `cn()`）
- **`server/`** — server-side 代码（better-auth，尚未启用）
- **`styles/`** — 全局 CSS，使用 Tailwind v4 `@import` 语法和 CSS variables 进行主题化

### 数据流

1. 用户输入 → thread hooks（`core/threads/hooks.ts`）→ LangGraph SDK 流式传输
2. stream events 更新 thread state（messages、artifacts、todos）
3. TanStack Query 管理 server state；localStorage 存储用户设置
4. 组件订阅 thread state 并渲染更新

### 关键模式

- **默认使用 Server Components**，只有交互型组件才使用 `"use client"`
- **Thread hooks**（`useThreadStream`、`useSubmitThread`、`useThreads`）是主要的 API 接口
- **LangGraph client** 是通过 `core/api/` 中的 `getAPIClient()` 获取的单例
- **环境校验** 使用带 Zod schema 的 `@t3-oss/env-nextjs`（`src/env.js`）。可通过 `SKIP_ENV_VALIDATION=1` 跳过

## 代码风格

- **Imports**：强制排序（builtin → external → internal → parent → sibling），按字母排序，组之间空行分隔。类型导入使用内联形式：`import { type Foo }`。
- **未使用变量**：使用 `_` 前缀。
- **类名**：使用来自 `@/lib/utils` 的 `cn()` 处理条件式 Tailwind class。
- **路径别名**：`@/*` 映射到 `src/*`。
- **组件**：`ui/` 和 `ai-elements/` 来自 registries（Shadcn、MagicUI、React Bits、Vercel AI SDK）的自动生成内容——不要手动编辑这些文件。

## 环境

Backend API URL 是可选的；默认使用 nginx proxy：

```
NEXT_PUBLIC_BACKEND_BASE_URL=http://localhost:8001
NEXT_PUBLIC_LANGGRAPH_BASE_URL=http://localhost:2024
```

需要 Node.js 22+ 和 pnpm 10.26.2+。
