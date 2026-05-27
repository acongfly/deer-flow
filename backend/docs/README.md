# 文档

本目录包含 DeerFlow backend 的详细文档。

## 快速链接

| 文档 | 说明 |
|----------|-------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统架构概览 |
| [API.md](API.md) | 完整 API 参考 |
| [AUTH_DESIGN.md](AUTH_DESIGN.md) | 用户认证、CSRF 与按用户隔离的设计 |
| [CONFIGURATION.md](CONFIGURATION.md) | 配置选项 |
| [SETUP.md](SETUP.md) | 快速设置指南 |

## 功能文档

| 文档 | 说明 |
|----------|-------------|
| [STREAMING.md](STREAMING.md) | Token 级流式输出设计：Gateway 与 DeerFlowClient 路径、`stream_mode` 语义、按 id 去重 |
| [FILE_UPLOAD.md](FILE_UPLOAD.md) | 文件上传功能 |
| [PATH_EXAMPLES.md](PATH_EXAMPLES.md) | 路径类型与使用示例 |
| [summarization.md](summarization.md) | 上下文摘要功能 |
| [plan_mode_usage.md](plan_mode_usage.md) | 带 TodoList 的 Plan mode |
| [AUTO_TITLE_GENERATION.md](AUTO_TITLE_GENERATION.md) | 自动标题生成 |

## 开发

| 文档 | 说明 |
|----------|-------------|
| [TODO.md](TODO.md) | 规划中的功能与已知问题 |

## 入门

1. **第一次接触 DeerFlow？** 先阅读 [SETUP.md](SETUP.md) 进行快速安装
2. **正在配置系统？** 参见 [CONFIGURATION.md](CONFIGURATION.md)
3. **想了解架构？** 阅读 [ARCHITECTURE.md](ARCHITECTURE.md)
4. **要构建集成？** 查看 [API.md](API.md) 获取 API 参考

## 文档组织

```
docs/
├── README.md                  # This file
├── ARCHITECTURE.md            # System architecture
├── API.md                     # API reference
├── AUTH_DESIGN.md             # User authentication and isolation design
├── CONFIGURATION.md           # Configuration guide
├── SETUP.md                   # Setup instructions
├── FILE_UPLOAD.md             # File upload feature
├── PATH_EXAMPLES.md           # Path usage examples
├── summarization.md           # Summarization feature
├── plan_mode_usage.md         # Plan mode feature
├── STREAMING.md               # Token-level streaming design
├── AUTO_TITLE_GENERATION.md   # Title generation
├── TITLE_GENERATION_IMPLEMENTATION.md  # Title implementation details
└── TODO.md                    # Roadmap and issues
```
