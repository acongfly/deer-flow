# TODO 列表

## 已完成功能

- [x] 仅在首次调用文件系统或 bash 工具后才启动 sandbox
- [x] 为整个流程添加 Clarification Process
- [x] 实现上下文摘要机制，避免上下文膨胀
- [x] 集成 MCP（Model Context Protocol），实现可扩展工具能力
- [x] 添加文件上传支持，并自动进行文档转换
- [x] 实现对话线程标题自动生成
- [x] 添加带 TodoList middleware 的 Plan Mode
- [x] 添加视觉模型支持，并提供 ViewImageMiddleware
- [x] 使用 SKILL.md 格式的 skills 系统
- [x] 将 `packages/harness/deerflow/tools/builtins/task_tool.py`（subagent 轮询）中的 `time.sleep(5)` 替换为 `asyncio.sleep()`

## 计划中的功能

- [ ] 池化 sandbox 资源，减少 sandbox 容器数量
- [ ] 添加认证/授权层
- [ ] 实现限流
- [ ] 添加指标与监控
- [ ] 支持更多上传文档格式
- [ ] Skill 市场 / 远程安装 skill
- [ ] 优化 agent 热路径中的异步并发（IM 渠道多任务场景）
- [ ] 将 `packages/harness/deerflow/sandbox/local/local_sandbox.py` 中的 `subprocess.run()` 替换为 `asyncio.create_subprocess_shell()`
  - 将 community tools（tavily、jina_ai、firecrawl、infoquest、image_search）中的同步 `requests` 替换为 `httpx.AsyncClient`
  - [x] 将 title_middleware 和 memory updater 中同步的 `model.invoke()` 替换为异步 `model.ainvoke()`
  - 考虑为剩余阻塞式文件 I/O 添加 `asyncio.to_thread()` 包装
  - 生产环境请使用 `langgraph up`（多 worker）而不是 `langgraph dev`（单 worker）

## 已解决问题

- [x] 确保 `state.artifacts` 中不会出现重复文件
- [x] 长时间思考但内容为空（答案出现在 thinking 过程中）
