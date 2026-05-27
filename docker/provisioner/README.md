# DeerFlow Sandbox Provisioner（沙箱资源管理服务）

**Sandbox Provisioner** 是一个 FastAPI 服务，用于在 Kubernetes 中动态管理 sandbox Pod。它为 DeerFlow backend 提供 REST API，用于创建、监控和销毁隔离的 sandbox 环境，以执行代码。

## 架构

```
┌────────────┐  HTTP  ┌─────────────┐  K8s API  ┌──────────────┐
│  Backend   │ ─────▸ │ Provisioner │ ────────▸ │  Host K8s    │
│  (gateway/ │        │   :8002     │           │  API Server  │
│ langgraph) │        └─────────────┘           └──────┬───────┘
└────────────┘                                          │ creates
                                                        │
                          ┌─────────────┐         ┌────▼─────┐
                          │   Backend   │ ──────▸ │  Sandbox │
                          │ (via Docker │ NodePort│  Pod(s)  │
                          │   network)  │         └──────────┘
                          └─────────────┘
```

### 工作方式

1. **Backend 请求**：当 backend 需要执行代码时，它会发送一个 `POST /api/sandboxes` 请求，并携带 `sandbox_id`、`thread_id` 和可选的 `user_id`。

2. **创建 Pod**：provisioner 会在 `deer-flow` namespace 中创建一个专用 Pod，包含：
   - sandbox container image（all-in-one-sandbox）
   - 挂载 HostPath volume，用于：
     - `/mnt/skills` → 对公共 skills 的只读访问
     - `/mnt/user-data` → 对特定 thread 数据的读写访问
   - 资源限制（CPU、memory、ephemeral storage）
   - readiness/liveness probes

3. **创建 Service**：会创建一个 NodePort Service 来暴露该 Pod，Kubernetes 会自动从 NodePort 范围（通常是 30000-32767）分配端口。

4. **访问 URL**：provisioner 会向 backend 返回 `http://host.docker.internal:{NodePort}`，backend container 可以直接访问该地址。

5. **清理**：当会话结束时，`DELETE /api/sandboxes/{sandbox_id}` 会同时删除 Pod 和 Service。

## 要求

主机机器上需要有一个正在运行的 Kubernetes 集群（Docker Desktop K8s、OrbStack、minikube、kind 等）。

### 在 Docker Desktop 中启用 Kubernetes
1. 打开 Docker Desktop 设置
2. 进入 “Kubernetes” 标签页
3. 勾选 “Enable Kubernetes”
4. 点击 “Apply & Restart”

### 在 OrbStack 中启用 Kubernetes
1. 打开 OrbStack 设置
2. 进入 “Kubernetes” 标签页
3. 勾选 “Enable Kubernetes”

## API 接口

### `GET /health`
健康检查 endpoint。

**响应**：
```json
{
  "status": "ok"
}
```

### `POST /api/sandboxes`
创建一个新的 sandbox Pod + Service。

**请求**：
```json
{
  "sandbox_id": "abc-123",
  "thread_id": "thread-456",
  "user_id": "user-789"
}
```

`user_id` 是为了向后兼容而提供的可选字段，默认值为 `default`。当设置了 `USERDATA_PVC_NAME` 时，provisioner 会使用它来隔离基于 PVC 的 user-data 目录。

**响应**：
```json
{
  "sandbox_id": "abc-123",
  "sandbox_url": "http://host.docker.internal:32123",
  "status": "Pending"
}
```

**幂等**：使用相同的 `sandbox_id` 调用时，会返回已有的 sandbox 信息。

### `GET /api/sandboxes/{sandbox_id}`
获取指定 sandbox 的状态和 URL。

**响应**：
```json
{
  "sandbox_id": "abc-123",
  "sandbox_url": "http://host.docker.internal:32123",
  "status": "Running"
}
```

**状态值**：`Pending`、`Running`、`Succeeded`、`Failed`、`Unknown`、`NotFound`

### `DELETE /api/sandboxes/{sandbox_id}`
销毁一个 sandbox Pod + Service。

**响应**：
```json
{
  "ok": true,
  "sandbox_id": "abc-123"
}
```

### `GET /api/sandboxes`
列出当前所有受管理的 sandbox。

**响应**：
```json
{
  "sandboxes": [
    {
      "sandbox_id": "abc-123",
      "sandbox_url": "http://host.docker.internal:32123",
      "status": "Running"
    }
  ],
  "count": 1
}
```

## 配置

provisioner 通过环境变量进行配置（在 [docker-compose-dev.yaml](../docker-compose-dev.yaml) 中设置）：

| 变量 | 默认值 | 说明 |
|----------|---------|-------------|
| `K8S_NAMESPACE` | `deer-flow` | sandbox 资源所在的 Kubernetes namespace |
| `SANDBOX_IMAGE` | `enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest` | sandbox Pod 使用的 container image |
| `SKILLS_HOST_PATH` | - | **主机机器** 上 skills 目录的路径（必须为绝对路径） |
| `THREADS_HOST_PATH` | - | **主机机器** 上 threads 数据目录的路径（必须为绝对路径） |
| `SKILLS_PVC_NAME` | 空（使用 hostPath） | skills volume 的 PVC 名称；设置后，sandbox Pod 将使用 PVC 而不是 hostPath |
| `USERDATA_PVC_NAME` | 空（使用 hostPath） | user-data volume 的 PVC 名称；设置后，使用带有 `subPath: deer-flow/users/{user_id}/threads/{thread_id}/user-data` 的 PVC |
| `KUBECONFIG_PATH` | `/root/.kube/config` | provisioner container **内部** 的 kubeconfig 路径 |
| `NODE_HOST` | `host.docker.internal` | backend container 用于访问主机 NodePort 的主机名 |
| `K8S_API_SERVER` | （来自 kubeconfig） | 覆盖 K8s API server URL（例如 `https://host.docker.internal:26443`） |

### PVC User-Data 升级说明

旧版 provisioner 会从 `threads/{thread_id}/user-data` 挂载 PVC user-data。按用户作用域划分的新布局会从 `deer-flow/users/{user_id}/threads/{thread_id}/user-data` 挂载。

如果现有部署已经在旧布局下使用了基于 PVC 的 user-data，请在依赖新的 PVC subPath 之前迁移 DeerFlow 数据目录。挂载 gateway 用作 DeerFlow 基础目录的同一路径 PVC，然后运行现有的 user-isolation 迁移脚本：

```bash
cd backend
PYTHONPATH=. python scripts/migrate_user_isolation.py --dry-run
PYTHONPATH=. python scripts/migrate_user_isolation.py --user-id <target-user-id>
```

这会把旧的 `threads/{thread_id}/user-data` 数据迁移到 `users/<target-user-id>/threads/{thread_id}/user-data` 下；当 gateway 基础目录以 `deer-flow/` 挂载到 PVC 上时，这与新的 provisioner PVC subPath 保持一致。只有当旧数据应继续保留在默认无认证用户 namespace 中时，才把 `default` 用作目标用户。请在没有 gateway 或 sandbox Pod 正在写入这些路径时执行迁移。

### 重要说明：K8S_API_SERVER 覆盖

如果你的 kubeconfig 将 API server 地址设置为 `localhost`、`127.0.0.1` 或 `0.0.0.0`（OrbStack、minikube、kind 中很常见），provisioner **无法** 从 Docker container 内部访问它。

**解决方案**：将 `K8S_API_SERVER` 设置为使用 `host.docker.internal`：

```yaml
# docker-compose-dev.yaml
provisioner:
  environment:
    - K8S_API_SERVER=https://host.docker.internal:26443  # Replace 26443 with your API port
```

检查你的 kubeconfig API server：
```bash
kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'
```

## 前置条件

### 主机机器要求

1. **Kubernetes 集群**：
   - 已启用 Kubernetes 的 Docker Desktop，或
   - OrbStack（内置 K8s），或
   - minikube、kind、k3s 等。

2. **已配置 kubectl**：
   - `~/.kube/config` 必须存在且有效
   - 当前 context 应指向你的本地集群

3. **Kubernetes 访问权限**：
   - provisioner 需要具备以下权限：
     - 在 `deer-flow` namespace 中创建/读取/删除 Pod
     - 在 `deer-flow` namespace 中创建/读取/删除 Service
     - 读取 Namespace（以便在缺失时创建 `deer-flow`）

4. **Host 路径**：
   - `SKILLS_HOST_PATH` 和 `THREADS_HOST_PATH` 必须是**主机机器上的绝对路径**
   - 这些路径会通过 K8s HostPath volume 挂载到 sandbox Pod 中
   - 这些路径必须存在，并且 K8s node 可读

### Docker Compose 设置

provisioner 作为 docker-compose-dev stack 的一部分运行：

```bash
# Start Docker services (provisioner starts only when config.yaml enables provisioner mode)
make docker-start

# Or start just the provisioner
docker compose -p deer-flow-dev -f docker/docker-compose-dev.yaml up -d provisioner
```

compose 文件会：
- 将主机的 `~/.kube/config` 挂载到 container 中
- 添加 `host.docker.internal` 的 `extra_hosts` 条目（Linux 上必需）
- 为 K8s 访问配置环境变量

## 测试

### 手动 API 测试

```bash
# Health check
curl http://localhost:8002/health

# Create a sandbox (via provisioner container for internal DNS)
docker exec deer-flow-provisioner curl -X POST http://localhost:8002/api/sandboxes \
  -H "Content-Type: application/json" \
  -d '{"sandbox_id":"test-001","thread_id":"thread-001","user_id":"user-001"}'

# Check sandbox status
docker exec deer-flow-provisioner curl http://localhost:8002/api/sandboxes/test-001

# List all sandboxes
docker exec deer-flow-provisioner curl http://localhost:8002/api/sandboxes

# Verify Pod and Service in K8s
kubectl get pod,svc -n deer-flow -l sandbox-id=test-001

# Delete sandbox
docker exec deer-flow-provisioner curl -X DELETE http://localhost:8002/api/sandboxes/test-001
```

### 从 Backend Containers 验证

创建 sandbox 后，backend containers（gateway、langgraph）即可访问它：

```bash
# Get sandbox URL from provisioner
SANDBOX_URL=$(docker exec deer-flow-provisioner curl -s http://localhost:8002/api/sandboxes/test-001 | jq -r .sandbox_url)

# Test from gateway container
docker exec deer-flow-gateway curl -s $SANDBOX_URL/v1/sandbox
```

## 故障排查

### 问题：“Kubeconfig not found”

**原因**：挂载路径上的 kubeconfig 文件不存在。

**解决方案**：
- 确认主机机器上的 `~/.kube/config` 存在
- 运行 `kubectl config view` 进行验证
- 检查 docker-compose-dev.yaml 中的 volume 挂载

### 问题：“Kubeconfig path is a directory”

**原因**：挂载的 `KUBECONFIG_PATH` 指向的是目录而不是文件。

**解决方案**：
- 确保 compose 挂载源是文件（例如 `~/.kube/config`），而不是目录
- 在 container 内验证：
  ```bash
  docker exec deer-flow-provisioner ls -ld /root/.kube/config
  ```
- 期望输出应显示为普通文件（`-`），而不是目录（`d`）

### 问题：连接 K8s API 时出现 “Connection refused”

**原因**：provisioner 无法访问 K8s API server。

**解决方案**：
1. 检查你的 kubeconfig server 地址：
   ```bash
   kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}'
   ```
2. 如果它是 `localhost` 或 `127.0.0.1`，请设置 `K8S_API_SERVER`：
   ```yaml
   environment:
     - K8S_API_SERVER=https://host.docker.internal:PORT
   ```

### 问题：创建 Pod 时出现 “Unprocessable Entity”

**原因**：HostPath volume 包含无效路径（例如带 `..` 的相对路径）。

**解决方案**：
- 为 `SKILLS_HOST_PATH` 和 `THREADS_HOST_PATH` 使用绝对路径
- 在主机机器上验证这些路径存在：
  ```bash
  ls -la /path/to/skills
  ls -la /path/to/backend/.deer-flow/threads
  ```

### 问题：Pod 卡在 “ContainerCreating”

**原因**：通常是在从 registry 拉取 sandbox image。

**解决方案**：
- 预先拉取 image：`make docker-init`
- 检查 Pod 事件：`kubectl describe pod sandbox-XXX -n deer-flow`
- 检查 node：`kubectl get nodes`

### 问题：Backend 无法访问 sandbox URL

**原因**：NodePort 不可达，或 `NODE_HOST` 配置错误。

**解决方案**：
- 确认 Service 存在：`kubectl get svc -n deer-flow`
- 从主机测试：`curl http://localhost:NODE_PORT/v1/sandbox`
- 确保 docker-compose 中设置了 `extra_hosts`（Linux）
- 检查 `NODE_HOST` 环境变量是否与 backend 访问主机的方式一致

## 安全注意事项

1. **HostPath Volumes**：默认情况下，provisioner 会将主机目录挂载到 sandbox Pod 中。请确保这些路径只包含受信任的数据。对于生产环境，优先使用基于 PVC 的 volume（设置 `SKILLS_PVC_NAME` 和 `USERDATA_PVC_NAME`），以避免 node 特定的数据丢失风险。

2. **资源限制**：每个 sandbox Pod 都设置了 CPU、memory 和 storage 限制，以防止资源耗尽。

3. **网络隔离**：sandbox Pod 运行在 `deer-flow` namespace 中，但通过 NodePort 共享主机的网络 namespace。如需更严格的隔离，请考虑使用 NetworkPolicies。

4. **kubeconfig 访问权限**：provisioner 通过挂载的 kubeconfig 对你的 Kubernetes 集群拥有完整访问权限。请仅在受信任的环境中运行它。

5. **image 信任**：sandbox image 应来自受信任的 registry。请审查并审核 image 内容。

## 后续增强

- [ ] 支持为每个 sandbox 自定义 resource request/limit
- [x] 支持更大数据需求的 PersistentVolume
- [ ] 自动清理陈旧 sandbox（基于超时）
- [ ] Metrics 和监控（Prometheus 集成）
- [ ] 多集群支持（路由到不同的 K8s 集群）
- [ ] Pod affinity/anti-affinity 规则以改进调度
- [ ] 用于 sandbox 隔离的 NetworkPolicy 模板
