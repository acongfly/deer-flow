---
name: smoke-test
description: DeerFlow 端对端冒烟测试技能。引导完成：1）拉取最新代码，2）Docker 或本地安装部署（用户偏好，Docker 网络问题时默认本地），3）服务可用性验证，4）健康检查，5）最终测试报告。当用户说"运行冒烟测试"、"冒烟测试部署"、"验证安装"、"测试服务可用性"、"端到端测试"或类似表达时使用。
---

# DeerFlow 冒烟测试技能

此技能引导 Agent 完成 DeerFlow 的完整端对端冒烟测试工作流程，包括代码更新、部署（支持 Docker 和本地安装两种模式）、服务可用性验证和健康检查。

## 部署模式选择

此技能支持两种部署模式：
- **本地安装模式**（推荐，尤其在网络问题发生时）——直接在本地机器上运行所有服务
- **Docker 模式**——在 Docker 容器内运行所有服务

**选择策略**：
- 如果用户明确要求 Docker 模式，使用 Docker
- 如果发生网络问题（如镜像拉取缓慢），自动切换到本地模式
- 尽可能默认使用本地模式

## 目录结构

```
smoke-test/
├── SKILL.md                          ← 你在这里 - 核心工作流程和逻辑
├── scripts/
│   ├── check_docker.sh               ← 检查 Docker 环境
│   ├── check_local_env.sh            ← 检查本地环境依赖
│   ├── frontend_check.sh             ← 前端页面冒烟检查
│   ├── pull_code.sh                  ← 拉取最新代码
│   ├── deploy_docker.sh              ← Docker 部署
│   ├── deploy_local.sh               ← 本地部署
│   └── health_check.sh               ← 服务健康检查
├── references/
│   ├── SOP.md                        ← 标准操作程序
│   └── troubleshooting.md            ← 故障排除指南
└── templates/
    ├── report.local.template.md      ← 本地模式冒烟测试报告模板
    └── report.docker.template.md     ← Docker 模式冒烟测试报告模板
```

## 标准操作程序（SOP）

### 第一阶段：代码更新检查

1. **确认当前目录** - 验证当前工作目录是 DeerFlow 项目根目录
2. **检查 Git 状态** - 查看是否有未提交的更改
3. **拉取最新代码** - 使用 `git pull origin main` 获取最新更新
4. **确认代码更新** - 验证最新代码已成功拉取

### 第二阶段：部署模式选择和环境检查

**选择部署模式**：
- 询问用户偏好，或根据网络条件自动选择
- 默认使用本地安装模式

**本地模式环境检查**：
1. **检查 Node.js 版本** - 需要 22+
2. **检查 pnpm** - 包管理器
3. **检查 uv** - Python 包管理器
4. **检查 nginx** - 反向代理
5. **检查所需端口** - 确认端口 2026、3000、8001 和 2024 未被占用

**Docker 模式环境检查**（如选择 Docker）：
1. **检查 Docker 是否已安装** - 运行 `docker --version`
2. **检查 Docker 守护进程状态** - 运行 `docker info`
3. **检查 Docker Compose 可用性** - 运行 `docker compose version`
4. **检查所需端口** - 确认端口 2026 未被占用

### 第三阶段：配置准备

1. **检查 config.yaml 是否存在**
   - 如果不存在，运行 `make config` 生成
   - 如果已存在，检查是否需要使用 `make config-upgrade` 升级
2. **检查 .env 文件**
   - 验证必需的环境变量已配置
   - 尤其是 `OPENAI_API_KEY` 等模型 API 密钥

### 第四阶段：部署执行

**本地模式部署**：
1. **检查依赖** - 运行 `make check`
2. **安装依赖** - 运行 `make install`
3. **（可选）预拉取沙箱镜像** - 如需要，运行 `make setup-sandbox`
4. **启动服务** - 运行 `make dev-daemon`（后台模式，推荐）或 `make dev`（前台模式）
5. **等待启动** - 给所有服务足够的时间完全启动（建议 90-120 秒）

**Docker 模式部署**（如选择 Docker）：
1. **初始化 Docker 环境** - 运行 `make docker-init`
2. **启动 Docker 服务** - 运行 `make docker-start`
3. **等待启动** - 给所有容器足够的时间完全启动（建议 60 秒）

### 第五阶段：服务健康检查

**本地模式健康检查**：
1. **检查进程状态** - 确认 LangGraph、Gateway、Frontend 和 Nginx 进程都在运行
2. **检查前端服务** - 访问 `http://localhost:2026` 并验证页面加载
3. **检查 API Gateway** - 验证 `http://localhost:2026/health` 端点
4. **检查 LangGraph 服务** - 验证相关端点的可用性
5. **前端路由冒烟检查** - 运行 `bash .agent/skills/smoke-test/scripts/frontend_check.sh` 验证 `/workspace` 下的关键路由

**Docker 模式健康检查**（使用 Docker 时）：
1. **检查容器状态** - 运行 `docker ps` 并确认所有容器正在运行
2. **检查前端服务** - 访问 `http://localhost:2026` 并验证页面加载
3. **检查 API Gateway** - 验证 `http://localhost:2026/health` 端点
4. **检查 LangGraph 服务** - 验证相关端点的可用性
5. **前端路由冒烟检查** - 运行 `bash .agent/skills/smoke-test/scripts/frontend_check.sh` 验证 `/workspace` 下的关键路由

### 可选功能验证

1. **列出可用模型** - 验证模型配置是否正确加载
2. **列出可用技能** - 验证技能目录是否正确挂载
3. **简单聊天测试** - 发送简单消息验证端对端流程

### 第六阶段：生成测试报告

1. **收集所有测试结果** - 总结每个阶段的执行状态
2. **记录遇到的问题** - 如果有任何失败，记录错误详情
3. **生成最终报告** - 使用与所选部署模式匹配的模板创建完整测试报告，包括总体结论、详细关键测试用例和明确的前端页面/路由结果
4. **提供后续建议** - 根据测试结果提供建议

## 执行规则

- **遵循顺序** - 严格按照上述描述的顺序执行
- **幂等性** - 每个步骤应该可以安全重复
- **错误处理** - 如果一个步骤失败，停止并报告问题，然后提供故障排除建议
- **详细日志** - 记录每个步骤的执行结果和状态
- **用户确认** - 在可能有风险的操作（如覆盖配置）之前请求确认
- **模式偏好** - 优先使用本地模式以避免网络相关问题
- **模板要求** - 最终报告必须使用 `templates/` 下的匹配模板；不要输出自由格式摘要代替基于模板的报告
- **报告清晰度** - 执行摘要必须包括总体通过/失败结论以及每个用例的结果说明，前端冒烟检查结果必须在报告中明确列出
- **可选阶段处理** - 如果功能验证未执行，不要在最终报告中将其呈现为单独的跳过阶段

## 已知可接受的警告

以下警告可能在冒烟测试期间出现，不会阻止成功结果：
- 如果飞书/Lark 渠道未启用，Gateway 日志中的 SSL 错误（证书验证失败）可以忽略
- LangGraph 日志中关于自定义检查点器中缺少方法（如 `adelete_for_runs` 或 `aprune`）的警告不影响核心功能

## 关键工具

执行期间使用以下工具：

1. **bash** - 运行 shell 命令
2. **present_file** - 显示生成的报告和重要文件
3. **task_tool** - 需要时用子任务组织复杂步骤

## 成功标准

冒烟测试通过标准（本地模式）：
- [x] 最新代码拉取成功
- [x] 本地环境检查通过（Node.js 22+、pnpm、uv、nginx）
- [x] 配置文件设置正确
- [x] `make check` 通过
- [x] `make install` 成功完成
- [x] `make dev` 成功启动
- [x] 所有服务进程正常运行
- [x] 前端页面可访问
- [x] 前端路由冒烟检查通过（`/workspace` 关键路由）
- [x] API Gateway 健康检查通过
- [x] 测试报告完整生成

冒烟测试通过标准（Docker 模式）：
- [x] 最新代码拉取成功
- [x] Docker 环境检查通过
- [x] 配置文件设置正确
- [x] `make docker-init` 成功完成
- [x] `make docker-start` 成功完成
- [x] 所有 Docker 容器正常运行
- [x] 前端页面可访问
- [x] 前端路由冒烟检查通过（`/workspace` 关键路由）
- [x] API Gateway 健康检查通过
- [x] 测试报告完整生成

## 读取参考文件

开始执行前，读取以下参考文件：
1. `references/SOP.md` - 详细的分步操作说明
2. `references/troubleshooting.md` - 常见问题和解决方案
3. `templates/report.local.template.md` - 本地模式测试报告模板
4. `templates/report.docker.template.md` - Docker 模式测试报告模板
