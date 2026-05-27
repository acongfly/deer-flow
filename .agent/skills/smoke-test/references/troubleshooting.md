# 故障排除指南

本文档列出了 DeerFlow 冒烟测试期间遇到的常见问题及其解决方法。

## 代码更新问题

### 问题：`git pull` 因合并冲突警告失败

**症状**：
```
error: Your local changes to the following files would be overwritten by merge
```

**解决方案**：
1. 方案 A：先提交本地更改
   ```bash
   git add .
   git commit -m "Save local changes"
   git pull origin main
   ```

2. 方案 B：暂存本地更改
   ```bash
   git stash
   git pull origin main
   git stash pop
   ```

3. 方案 C：丢弃本地更改（谨慎使用）
   ```bash
   git reset --hard HEAD
   git pull origin main
   ```

---

## 本地模式环境问题

### 问题：Node.js 版本过旧

**症状**：`Node.js version is too old. Requires 22+, got x.x.x`

**解决方案**：使用 nvm 安装 Node.js 22+，或从 https://nodejs.org/ 下载。

---

### 问题：pnpm 未安装

**解决方案**：`npm install -g pnpm` 或参考 https://pnpm.io/installation

---

### 问题：uv 未安装

**解决方案**：`curl -LsSf https://astral.sh/uv/install.sh | sh`

---

### 问题：nginx 未安装

**解决方案**：
- macOS：`brew install nginx`
- Ubuntu/Debian：`sudo apt install nginx`

---

### 问题：端口已被占用

**症状**：`Error: listen EADDRINUSE: address already in use :::2026`

**解决方案**：
```bash
lsof -i :2026
# 停止占用端口的进程，或运行：
make stop
```

---

## 本地模式依赖安装问题

### 问题：`make install` 因网络超时失败

**解决方案**：
```bash
pnpm config set registry https://registry.npmmirror.com
uv pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
make install
```

---

### 问题：Python 依赖安装失败

**解决方案**：
```bash
cd backend && uv cache clean && uv sync
```

---

### 问题：前端依赖安装失败

**解决方案**：
```bash
cd frontend && rm -rf node_modules pnpm-lock.yaml && pnpm install
```

---

## 本地模式服务启动问题

### 问题：服务在启动后立即退出

**解决方案**：
```bash
tail -f logs/langgraph.log
tail -f logs/gateway.log
tail -f logs/frontend.log
make stop && make dev-daemon
```

---

### 问题：nginx 因临时目录不存在而启动失败

**症状**：`nginx: [emerg] mkdir() "/opt/homebrew/var/run/nginx/client_body_temp" failed`

**解决方案**：在 `docker/nginx/nginx.local.conf` 的 `http` 块开头添加：
```nginx
client_body_temp_path temp/client_body_temp;
proxy_temp_path temp/proxy_temp;
fastcgi_temp_path temp/fastcgi_temp;
uwsgi_temp_path temp/uwsgi_temp;
scgi_temp_path temp/scgi_temp;
```

---

### 问题：nginx 启动失败（通用）

**解决方案**：
```bash
nginx -t -c docker/nginx/nginx.local.conf -p .
tail -f logs/nginx.log
```

---

### 问题：前端编译失败

**解决方案**：
```bash
cd frontend && rm -rf node_modules .next && pnpm install
make stop && make dev-daemon
```

---

### 问题：Gateway 启动失败

**解决方案**：
```bash
tail -f logs/gateway.log
cd backend && uv sync
```

---

### 问题：LangGraph 启动失败

**解决方案**：
```bash
tail -f logs/langgraph.log
# 检查 config.yaml 和端口 2024
```

---

## Docker 相关问题

### 问题：无法运行 Docker 命令

**解决方案**：确认 Docker Desktop 正在运行，或运行 `sudo systemctl start docker`。

---

### 问题：`make docker-init` 拉取镜像失败

**解决方案**：检查网络/代理，或切换到本地安装模式（推荐）。

---

## 配置文件问题

### 问题：config.yaml 缺失或无效

**解决方案**：
```bash
make config
# 检查 YAML 缩进（2 个空格，无 tab）
```

---

### 问题：模型 API 密钥未配置

**解决方案**：在 .env 文件中添加 `OPENAI_API_KEY=your-key`，然后重启服务。

---

## 服务健康检查问题

### 问题：前端页面无法访问

**解决方案**（本地模式）：
```bash
ps aux | grep nginx
tail -f logs/nginx.log
```

**解决方案**（Docker 模式）：
```bash
docker ps | grep nginx
```

---

### 问题：API Gateway 健康检查失败

**解决方案**：
```bash
tail -f logs/gateway.log
cd backend && uv sync
```

---

## 常用诊断命令

```bash
# 查看所有服务进程
ps aux | grep -E "(langgraph|uvicorn|next|nginx)" | grep -v grep

# 查看所有日志
tail -f logs/*.log

# 停止所有服务
make stop

# 完全重置本地环境
make stop && make clean && make config && make install && make dev-daemon

# Docker 诊断
docker ps -a
docker stats
docker exec -it deer-flow-gateway sh
```

---

## 获取更多帮助

1. 查看项目 GitHub issues：https://github.com/bytedance/deer-flow/issues
2. 查阅项目文档：README.md 和 `backend/docs/` 目录
3. 提交新 issue 并附上详细错误日志
