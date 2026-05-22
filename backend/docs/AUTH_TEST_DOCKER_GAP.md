# Docker 测试缺口（第七节 7.4）

本文档记录了在完整发布验证轮次结束后，`backend/docs/AUTH_TEST_PLAN.md` 中唯一**未执行**的测试用例。

## 为什么会存在这个缺口

发布验证环境（sg_dev：`10.251.229.92`）**没有安装 Docker 守护进程**。TC-DOCKER 用例属于容器运行时行为测试，需要真实的 Docker 引擎来启动 `docker/docker-compose.yaml` 中的服务。

```bash
$ ssh sg_dev "which docker; docker --version"
# (empty)
# bash: docker: command not found
```

测试计划中的其他所有章节都已在以下环境之一执行：
- 本地开发机器（Mac，所有服务均在本地运行），或
- 已部署的 sg_dev 实例（通过 SSH 隧道访问 gateway + frontend + nginx）

## 未执行的用例

| 用例 | 标题 | 覆盖内容 | 未执行原因 |
|---|---|---|---|
| TC-DOCKER-01 | `deerflow.db` 卷持久化 | 验证 `DEER_FLOW_HOME` 绑定挂载在容器重启后仍然保留 | 需要 `docker compose up` |
| TC-DOCKER-02 | 容器重启后的会话持久化 | `AUTH_JWT_SECRET` 环境变量可在 `docker compose down && up` 后保持 cookie 仍然有效 | 需要 `docker compose down/up` |
| TC-DOCKER-03 | 每个 worker 的限流器状态分叉 | 确认进程内 `_login_attempts` 字典不会在 `gunicorn` worker（compose 文件默认 4 个）之间共享；这是已知限制，已有文档说明 | 需要多 worker 容器 |
| TC-DOCKER-04 | IM 渠道使用内部 Gateway 认证 | 验证 Feishu/Slack/Telegram 分发器在调用兼容 Gateway 的 LangGraph API 时，会附加进程内本地内部认证 header，以及 CSRF cookie/header | 需要 `docker logs` |
| TC-DOCKER-05 | 重置凭据的暴露方式 | `reset_admin` 会在 `DEER_FLOW_HOME` 中写入一个权限为 0600 的凭据文件，而不是在日志中输出明文。非 Docker 的重置测试已验证文件写入行为，因此唯一尚未覆盖的 Docker 特有缺口，是确认卷挂载会把该文件带到宿主机 | 需要容器 + 宿主机卷 |
| TC-DOCKER-06 | Gateway 模式 Docker 部署 | `./scripts/deploy.sh --gateway` 会产生一个 3 容器拓扑（不含 `langgraph` 容器）；认证流程与标准模式一致 | 需要 `docker compose --profile gateway` |

## 非 Docker 测试已提供的覆盖

每个 Docker 用例中与**认证相关**的行为，都已经由在 sg_dev 或本地执行过的测试用例覆盖：

| Docker 用例 | 已覆盖该认证行为的测试 |
|---|---|
| TC-DOCKER-01（卷持久化） | sg_dev 上的 TC-REENT-01（admin 记录在 gateway 重启后仍然存在）—— 使用的是同一个 SQLite 文件，只是中间没有容器这一层 |
| TC-DOCKER-02（会话持久化） | TC-API-02/03/06（cookie 往返）以及 TC-REENT-04（多 cookie）—— JWT 校验不依赖进程状态，容器重启等价于 `pkill uvicorn && uv run uvicorn` |
| TC-DOCKER-03（每个 worker 的限流） | TC-GW-04 + TC-REENT-09（单 worker 限流 + 5 分钟过期）。跨 worker 状态分叉是内存字典的架构属性；认证代码路径本身没有差异 |
| TC-DOCKER-04（IM 渠道使用内部认证） | 代码层面：`app/channels/manager.py` 使用 `create_internal_auth_headers()` 加上 CSRF cookie/header 创建 `langgraph_sdk` client，因此渠道 worker 不依赖浏览器 cookie |
| TC-DOCKER-05（凭据暴露方式） | `reset_admin` 会写入权限为 0600 的 `.deer-flow/admin_initial_credentials.txt`，日志中只记录路径—— Docker 唯一特有的一步，是确认绑定挂载是否把该路径映射到宿主机，这属于 `docker compose` 配置检查，而不是运行时行为变化 |
| TC-DOCKER-06（Gateway 模式容器） | 第七节 7.2 已由 TC-GW-01..05 覆盖，加上第二节（sg_dev 上 Gateway 模式认证流程）—— 使用的是同一套 Gateway 代码，容器只是打包方式变化 |

## Docker 可用后的复现步骤

任何安装了 `docker` 和 `docker compose` 的人，都可以按测试计划原文复现这个缺口。执行前请先完成以下准备：

```bash
# Required on the host
docker --version           # >=24.x
docker compose version     # plugin >=2.x

# Required env var (otherwise sessions reset on every container restart)
echo "AUTH_JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" \
  >> .env

# Optional: pin DEER_FLOW_HOME to a stable host path
echo "DEER_FLOW_HOME=$HOME/deer-flow-data" >> .env
```

然后按测试计划所写执行 TC-DOCKER-01..06。

## 决策记录

- **不阻塞本次发布。** 每个 Docker 用例中与认证相关的行为，都已有裸机环境下已验证的等价测试。当前缺口纯粹与*容器打包*细节有关（绑定挂载、多 worker、日志采集），而不是认证代码路径本身是否工作。
- **已直接更新 `AUTH_TEST_PLAN.md` 中的 TC-DOCKER-05。** 其内容现已反映当前重置流程（`reset_admin` → 0600 凭据文件，不会泄露到日志）。旧的“在 docker logs 里 grep `'Password:'`”预期会静默失败，并给出错误的覆盖感。
