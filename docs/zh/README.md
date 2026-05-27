# DeerFlow 中文开发者文档

> 文档来源：本目录所有文档均基于以下原始资料整理翻译：
> - 仓库根目录：[`README_zh.md`](../../README_zh.md)、[`CONTRIBUTING.md`](../../CONTRIBUTING.md)、[`Install.md`](../../Install.md)
> - 后端主文档：[`backend/CLAUDE.md`](../../backend/CLAUDE.md)
> - 后端架构文档：[`backend/docs/ARCHITECTURE.md`](../../backend/docs/ARCHITECTURE.md)
> - 后端配置文档：[`backend/docs/CONFIGURATION.md`](../../backend/docs/CONFIGURATION.md)
> - 后端认证设计：[`backend/docs/AUTH_DESIGN.md`](../../backend/docs/AUTH_DESIGN.md)
> - MCP 文档：[`backend/docs/MCP_SERVER.md`](../../backend/docs/MCP_SERVER.md)
> - 安全护栏：[`backend/docs/GUARDRAILS.md`](../../backend/docs/GUARDRAILS.md)
> - 流式输出设计：[`backend/docs/STREAMING.md`](../../backend/docs/STREAMING.md)
> - 记忆系统：[`backend/docs/MEMORY_IMPROVEMENTS.md`](../../backend/docs/MEMORY_IMPROVEMENTS.md)
> - 其他 RFC / 计划文档：[`backend/docs/`](../../backend/docs/)

---

## 文档目录（按架构优先级排列）

| 序号 | 文档 | 说明 |
|------|------|------|
| 01 | [架构总览](./01-架构总览.md) | 系统整体架构、层次关系、核心组件 |
| 02 | [快速开始与开发环境](./02-快速开始.md) | 环境搭建、本地运行、Docker 运行 |
| 03 | [核心模块 — Agent 系统](./03-Agent系统.md) | Lead Agent、中间件链、ThreadState |
| 04 | [核心模块 — Sandbox 沙箱](./04-Sandbox沙箱.md) | 沙箱抽象、本地/AIO 实现、虚拟路径 |
| 05 | [核心模块 — 工具系统](./05-工具系统.md) | 内置工具、社区工具、工具组装 |
| 06 | [核心模块 — Subagent 子代理](./06-Subagent子代理.md) | 子代理注册、调度、并发控制 |
| 07 | [核心模块 — MCP 集成](./07-MCP集成.md) | 协议概念、配置、OAuth、缓存 |
| 08 | [核心模块 — Skills 技能系统](./08-Skills技能系统.md) | 技能格式、加载、注入、安装 |
| 09 | [核心模块 — 记忆系统](./09-记忆系统.md) | 记忆提取、注入、Token 预算、路线图 |
| 10 | [核心模块 — 模型工厂](./10-模型工厂.md) | 模型配置、思维模式、视觉支持 |
| 11 | [网关 API](./11-网关API.md) | FastAPI 路由、RunManager、SSE |
| 12 | [配置系统](./12-配置系统.md) | config.yaml、extensions_config.json、热重载 |
| 13 | [认证与安全](./13-认证与安全.md) | 认证流程、用户隔离、CSRF、Guardrails |
| 14 | [前端架构](./14-前端架构.md) | Next.js 目录、核心模块、状态管理 |
| 15 | [IM 渠道集成](./15-IM渠道集成.md) | 飞书/Slack/Telegram/钉钉接入 |
| 16 | [流式输出设计](./16-流式输出设计.md) | Gateway 路径、Client 路径、SSE 协议 |
| 17 | [开发-测试-上线全链路](./17-全链路指南.md) | CI/CD、测试策略、上线 checklist |
| 18 | [开发 Demo 示例](./18-开发Demo.md) | 各模块示例代码、集成演示 |
| 19 | [沙箱与智能体作用说明](./19-沙箱与智能体作用说明.md) | 面向问题解答的沙箱使用时机与智能体价值说明 |

---

## 项目一句话介绍

**DeerFlow**（Deep Exploration and Efficient Research Flow）是字节跳动开源的 **Super Agent Harness**。它以 LangGraph 为编排核心，把 **Lead Agent + Sub-Agent + Memory + Sandbox + Skills + MCP** 集于一体，配合可插拔的扩展机制，让 AI Agent 几乎可以完成任何任务。

官网：<https://deerflow.tech>  
GitHub：<https://github.com/bytedance/deer-flow>
