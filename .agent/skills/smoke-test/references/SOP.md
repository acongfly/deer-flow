# DeerFlow 冒烟测试标准操作程序（SOP）

本文档描述了 DeerFlow 冒烟测试每个阶段的详细操作步骤。

## 第一阶段：代码更新检查

### 1.1 确认当前目录

**目标**：验证当前工作目录是 DeerFlow 项目根目录。

**步骤**：
1. 运行 `pwd` 查看当前工作目录
2. 检查该目录是否包含以下文件/目录：
   - `Makefile`
   - `backend/`
   - `frontend/`
   - `config.example.yaml`

**成功标准**：当前目录包含以上所有文件/目录。

---

### 1.2 检查 Git 状态

**目标**：检查是否有未提交的更改。

**步骤**：
1. 运行 `git status`
2. 检查输出是否包含"Changes not staged for commit"或"Untracked files"

**注意**：
- 如果有未提交的更改，建议用户先提交或暂存，以避免拉取时冲突
- 如果用户确认要继续，可以跳过此步骤

---

### 1.3 拉取最新代码

**目标**：获取最新代码更新。

**步骤**：
1. 运行 `git fetch origin main`
2. 运行 `git pull origin main`

**成功标准**：
- 命令成功执行，无错误
- 输出显示"Already up to date"或表示成功拉取了新提交

---

### 1.4 确认代码更新

**目标**：验证最新代码已成功拉取。

**步骤**：
1. 运行 `git log -1 --oneline` 查看最新提交
2. 记录提交哈希和信息

---

## 第二阶段：部署模式选择和环境检查

### 2.1 选择部署模式

**目标**：决定使用本地模式还是 Docker 模式。

**决策流程**：
1. 优先选择本地模式以避免网络相关问题
2. 如果用户明确要求 Docker，则使用 Docker
3. 如果发生 Docker 网络问题，自动切换到本地模式

---

### 2.2 本地模式环境检查

**目标**：验证本地开发环境依赖是否满足。

#### 2.2.1 检查 Node.js 版本

**步骤**：
1. 如果使用 nvm，运行 `nvm use 22` 切换到 Node 22+
2. 运行 `node --version`

**成功标准**：版本 >= 22.x

**失败处理**：
- 如果版本过低，让用户使用 nvm 安装/切换 Node.js：
  ```bash
  nvm install 22
  nvm use 22
  ```
- 或从官网安装：https://nodejs.org/

---

#### 2.2.2 检查 pnpm

**步骤**：运行 `pnpm --version`

**成功标准**：命令返回 pnpm 版本信息。

**失败处理**：如果未安装 pnpm，让用户运行 `npm install -g pnpm`

---

#### 2.2.3 检查 uv

**步骤**：运行 `uv --version`

**成功标准**：命令返回 uv 版本信息。

**失败处理**：如果未安装 uv，让用户安装 uv

---

#### 2.2.4 检查 nginx

**步骤**：运行 `nginx -v`

**成功标准**：命令返回 nginx 版本信息。

**失败处理**：
- macOS：使用 Homebrew 安装，`brew install nginx`
- Linux：使用系统包管理器安装

---

#### 2.2.5 检查所需端口

**步骤**：
1. 运行以下命令检查端口：
   ```bash
   lsof -i :2026  # 主端口
   lsof -i :3000  # 前端
   lsof -i :8001  # Gateway
   lsof -i :2024  # LangGraph
   ```

**成功标准**：所有端口空闲，或仅被 DeerFlow 相关进程占用。

**失败处理**：如果端口被占用，让用户停止相关进程

---

### 2.3 Docker 模式环境检查（如选择 Docker）

#### 2.3.1 检查 Docker 是否已安装

**步骤**：运行 `docker --version`

**成功标准**：命令返回 Docker 版本信息，例如"Docker version 24.x.x"。

---

#### 2.3.2 检查 Docker 守护进程状态

**步骤**：运行 `docker info`

**成功标准**：命令成功运行并显示 Docker 系统信息。

**失败处理**：如果失败，让用户启动 Docker Desktop 或 Docker 服务

---

#### 2.3.3 检查 Docker Compose 可用性

**步骤**：运行 `docker compose version`

**成功标准**：命令返回 Docker Compose 版本信息。

---

#### 2.3.4 检查所需端口

**步骤**：运行 `lsof -i :2026`（macOS/Linux）或 `netstat -ano | findstr :2026`（Windows）

**成功标准**：端口 2026 空闲，或仅被 DeerFlow 相关进程占用。

---

## 第三阶段：配置准备

### 3.1 检查 config.yaml

**步骤**：
1. 检查 `config.yaml` 是否存在
2. 如果不存在，运行 `make config`
3. 如果已存在，考虑运行 `make config-upgrade` 合并新字段

**验证**：
- 检查 config.yaml 中是否至少配置了一个模型
- 检查模型配置是否正确引用了环境变量

---

### 3.2 检查 .env 文件

**步骤**：
1. 检查 `.env` 文件是否存在
2. 如果不存在，从 `.env.example` 复制
3. 检查是否配置了以下环境变量：
   - `OPENAI_API_KEY`（或其他模型 API 密钥）
   - 其他必需设置

---

## 第四阶段：部署执行

### 4.1 本地模式部署

#### 4.1.1 检查依赖

**步骤**：运行 `make check`

**描述**：此命令验证所有必需工具（Node.js 22+、pnpm、uv、nginx）。

---

#### 4.1.2 安装依赖

**步骤**：运行 `make install`

**描述**：此命令安装后端和前端依赖。

**注意**：此步骤可能需要一些时间；如果网络问题导致失败，尝试使用更近的镜像包仓库。

---

#### 4.1.3 （可选）预拉取沙箱镜像

**步骤**：如果使用 Docker/容器沙箱，运行 `make setup-sandbox`

**描述**：此步骤是可选的，本地沙箱模式不需要。

---

#### 4.1.4 启动服务

**步骤**：运行 `make dev-daemon`（后台模式）

**描述**：此命令启动所有服务（LangGraph、Gateway、Frontend、Nginx）。

**注意**：
- `make dev` 在前台运行，按 Ctrl+C 停止
- `make dev-daemon` 在后台运行
- 使用 `make stop` 停止服务

---

#### 4.1.5 等待服务启动

**步骤**：
1. 等待 90-120 秒让所有服务完全启动
2. 可以通过检查这些日志文件监控启动进度：
   - `logs/langgraph.log`
   - `logs/gateway.log`
   - `logs/frontend.log`
   - `logs/nginx.log`

---

### 4.2 Docker 模式部署（如选择 Docker）

#### 4.2.1 初始化 Docker 环境

**步骤**：运行 `make docker-init`

**描述**：此命令在需要时拉取沙箱镜像。

---

#### 4.2.2 启动 Docker 服务

**步骤**：运行 `make docker-start`

**描述**：此命令构建并启动所有必需的 Docker 容器。

---

#### 4.2.3 等待服务启动

**步骤**：
1. 等待 60-90 秒让所有服务完全启动
2. 可以运行 `make docker-logs` 监控启动进度

---

## 第五阶段：服务健康检查

### 5.1 本地模式健康检查

#### 5.1.1 检查进程状态

**步骤**：
1. 运行以下命令检查进程：
   ```bash
   ps aux | grep -E "(langgraph|uvicorn|next|nginx)" | grep -v grep
   ```

**成功标准**：确认以下进程正在运行：
- LangGraph（`langgraph dev`）
- Gateway（`uvicorn app.gateway.app:app`）
- Frontend（`next dev` 或 `next start`）
- Nginx（`nginx`）

---

#### 5.1.2 检查前端服务

**步骤**：
1. 使用 curl 或浏览器访问 `http://localhost:2026`
2. 验证页面正常加载

**示例 curl 命令**：
```bash
curl -I http://localhost:2026
```

**成功标准**：返回 HTTP 200 状态码。

---

#### 5.1.3 检查 API Gateway

**步骤**：
1. 访问 `http://localhost:2026/health`

**示例 curl 命令**：
```bash
curl http://localhost:2026/health
```

**成功标准**：返回健康状态 JSON。

---

#### 5.1.4 检查 LangGraph 服务

**步骤**：访问相关 LangGraph 端点验证可用性

---

### 5.2 Docker 模式健康检查（使用 Docker 时）

#### 5.2.1 检查容器状态

**步骤**：
1. 运行 `docker ps`
2. 确认以下容器正在运行：
   - `deer-flow-nginx`
   - `deer-flow-frontend`
   - `deer-flow-gateway`
   - `deer-flow-langgraph`（如果不在 gateway 模式下）

---

#### 5.2.2 检查前端服务

**步骤**：使用 curl 或浏览器访问 `http://localhost:2026`，验证页面正常加载。

---

#### 5.2.3 检查 API Gateway

**步骤**：运行 `curl http://localhost:2026/health`，验证返回健康状态 JSON。

---

#### 5.2.4 检查 LangGraph 服务

**步骤**：访问相关 LangGraph 端点验证可用性

---

## 可选功能验证

### 6.1 列出可用模型

**步骤**：通过 API 或 UI 验证模型列表。

---

### 6.2 列出可用技能

**步骤**：通过 API 或 UI 验证技能列表。

---

### 6.3 简单聊天测试

**步骤**：发送简单消息测试完整工作流程。

---

## 第六阶段：生成测试报告

### 6.1 收集测试结果

总结每个阶段的执行状态，记录成功和失败项目。

### 6.2 记录问题

如果有任何失败，记录详细错误信息。

### 6.3 生成报告

使用模板创建完整的测试报告。

### 6.4 提供建议

根据测试结果提供后续建议。
