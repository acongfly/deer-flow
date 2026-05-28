# DeerFlow 生产环境部署方案设计

> 文档版本：v1.0 | 最后更新：2026-05-28  
> 适用代码分支：当前主分支  
> 定位：面向对外提供多租户 AI Agent 服务的生产环境，涵盖高可用、高性能、安全、多租户改造方案

---

## 目录

1. [现有架构分析](#1-现有架构分析)
2. [生产环境核心挑战](#2-生产环境核心挑战)
3. [方案一：单机强化部署（低成本入门）](#3-方案一单机强化部署低成本入门)
4. [方案二：多副本 + 外部存储（推荐中规模）](#4-方案二多副本--外部存储推荐中规模)
5. [方案三：Kubernetes 云原生（大规模生产）](#5-方案三kubernetes-云原生大规模生产)
6. [多租户设计详解](#6-多租户设计详解)
7. [高可用配置](#7-高可用配置)
8. [高性能配置](#8-高性能配置)
9. [安全加固](#9-安全加固)
10. [方案对比总结](#10-方案对比总结)
11. [具体改造建议清单](#11-具体改造建议清单)

---

## 1. 现有架构分析

### 1.1 当前技术栈总览

```
Browser
  │
  ▼
Nginx (Port 2026)          ─ 统一反向代理入口
  │
  ├─→ Frontend (Next.js 3000)  ─ React 前端，BetterAuth session
  │
  └─→ Gateway API (FastAPI 8001) ─ 嵌入式 Agent Runtime
          │
          ├── AuthMiddleware + CSRFMiddleware   ─ JWT HttpOnly cookie
          ├── LangGraph-compatible runtime      ─ 多步骤 Agent 编排
          ├── SandboxMiddleware (lazy_init)     ─ 代码/命令执行隔离
          ├── SQLite (deerflow.db)              ─ threads_meta/users/runs
          └── 本地文件系统 .deer-flow/            ─ 线程数据/上传/输出

Sandbox Provider (按配置选择):
  ├── LocalSandboxProvider   ─ 开发用，直接本地执行
  └── AioSandboxProvider     ─ Docker/K3s 容器隔离（生产推荐）
        ├── LocalContainerBackend   ─ Docker in Docker (DooD)
        └── RemoteSandboxBackend    ─ K3s provisioner (8002)
```

**关键文件引用：**
- `docker/docker-compose.yaml` — 生产 Docker Compose，4个服务
- `docker/nginx/nginx.conf` — Nginx 反向代理配置，SSE/流式支持
- `backend/docs/ARCHITECTURE.md` — 官方架构文档
- `backend/docs/AUTH_DESIGN.md` — 认证与多租户隔离设计
- `config.example.yaml` — 完整配置示例

### 1.2 认证与多租户现状

已实现的能力（`AUTH_DESIGN.md`）：
- **JWT HttpOnly cookie** 认证，`token_version` 保证改密码/reset 立即失效
- **用户隔离**：threads、文件系统、memory、自定义 agent 均按 `user_id` 分桶
  ```
  .deer-flow/users/{user_id}/threads/{thread_id}/user-data/
  .deer-flow/users/{user_id}/memory.json
  .deer-flow/users/{user_id}/agents/{agent_name}/
  ```
- **CSRF double-submit** token 防护
- **AuthMiddleware** fail-closed，除 public 端点外全部拦截
- 基于 bcrypt 的密码存储，admin 初始化流程

当前边界（待改造）：
- 登录限速是**进程内 dict**，多 worker 下不全局精确（`AUTH_DESIGN.md` 已知边界）
- OAuth 端点**占位未实现**
- IM channel 使用 `default` 内部用户，无外部用户隔离
- **SQLite 不支持多进程写并发**（单节点可用，多副本需替换）
- session 状态存储在 LangGraph store（SQLite），无法跨实例共享

---

## 2. 生产环境核心挑战

### 2.1 存储层问题（高优先级）

| 问题 | 现状 | 影响 |
|------|------|------|
| SQLite 单写锁 | `deerflow.db` 是本地 SQLite | 多副本/多进程写冲突，数据损坏风险 |
| 文件系统本地化 | `.deer-flow/` 本地目录 | 多副本无法共享线程数据、上传文件 |
| LangGraph checkpoint | 存 SQLite InMemory/Local | 多实例无状态漂移，会话断裂 |
| 沙箱文件隔离 | Docker socket 挂载 | 需要 DooD（Docker out of Docker），权限风险 |

### 2.2 并发与性能问题

| 问题 | 现状 | 影响 |
|------|------|------|
| Gateway 单进程 | `uvicorn --workers 4`（docker-compose 默认） | CPU 密集型 Agent 推理阻塞其他请求 |
| Sandbox warm pool | AioSandboxProvider 有 warm pool | 冷启动仍需 2-5s（Docker 拉镜像） |
| SSE 长连接 | Nginx proxy_read_timeout 600s | 大并发时 Nginx 连接数耗尽 |
| LLM API 限速 | 无全局 rate limit | 单用户超额消耗影响他人 |
| 上传文件大小 | nginx `client_max_body_size 100M` | 大文件上传阻塞 I/O |

### 2.3 安全问题

| 问题 | 现状 | 影响 |
|------|------|------|
| Docker socket 暴露 | 挂载宿主机 `/var/run/docker.sock` | container escape 风险，沙箱内可控制宿主 |
| BETTER_AUTH_SECRET | 单一静态 secret | 轮换困难，泄露后需全量重签 |
| 登录限速非全局 | 进程内 dict | 多副本环境暴力破解保护失效 |
| TLS 终止 | Nginx 未配置 HTTPS | 明文传输 JWT cookie |
| secrets 管理 | `.env` 文件 | 建议迁移到 Vault/K8s Secrets |

### 2.4 多租户隔离问题

| 问题 | 现状 | 影响 |
|------|------|------|
| 沙箱共享宿主网络 | 默认无网络隔离 | 租户沙箱可互访内网 |
| LLM quota 无控制 | 无 per-user token limit | 单用户耗尽 API 配额 |
| Skill 权限 | skills 全局共享 | 无法按租户开放不同 skill |
| 角色粒度 | 仅 admin/user | 无法区分付费套餐、企业用户 |

---

## 3. 方案一：单机强化部署（低成本入门）

### 3.1 适用场景

- 用户量 < 100 并发
- 预算有限，快速上线
- 允许有计划停机维护

### 3.2 架构图

```
Internet
  │
  ▼
Nginx (TLS 443 → 2026)
  │  ├── Let's Encrypt / 手动证书
  │  └── rate limiting (limit_req_zone)
  │
  ├─→ Frontend (Next.js)
  │
  └─→ Gateway (uvicorn 4~8 workers)
          │
          ├── PostgreSQL (本机 Docker / 独立实例)
          │    └── 替代 SQLite：threads_meta, users, runs
          ├── Redis (本机)
          │    └── 登录限速、session cache
          └── NFS/本地 SSD
               └── .deer-flow/ 线程数据（单机无共享需求）
```

### 3.3 关键改造步骤

#### 3.3.1 TLS 配置（Nginx）

```nginx
# docker/nginx/nginx.conf 改造
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate     /etc/nginx/certs/fullchain.pem;
    ssl_certificate_key /etc/nginx/certs/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    # CSP
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; ...";

    # 其余 location 块保持不变
}

server {
    listen 80;
    return 301 https://$host$request_uri;
}
```

#### 3.3.2 登录限速（Nginx 层）

```nginx
# 在 http {} 块顶部添加
limit_req_zone $binary_remote_addr zone=login:10m rate=5r/m;

location /api/v1/auth/login {
    limit_req zone=login burst=10 nodelay;
    proxy_pass http://$gateway_upstream;
    # ...
}
```

#### 3.3.3 SQLite → PostgreSQL

**改造文件：** `backend/packages/harness/deerflow/persistence/` 及 LangGraph checkpoint 配置

当前 SQLite 数据库路径由 `config/paths.py` 的 `Paths.db_path` 控制。需要：

1. 安装依赖：`uv add asyncpg psycopg2-binary`
2. 更改 LangGraph 的 checkpointer：
   ```python
   # 当前使用 AsyncSqliteSaver，改为 AsyncPostgresSaver
   from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
   
   async with AsyncPostgresSaver.from_conn_string(
       os.environ["DATABASE_URL"]
   ) as checkpointer:
       ...
   ```
3. 更改 `threads_meta`、`users`、`runs` 等表的 SQLite → PostgreSQL 驱动

**环境变量：**
```env
DATABASE_URL=******localhost:5432/deerflow
```

#### 3.3.4 Redis 全局限速

```python
# app/gateway/auth_middleware.py — 改造登录限速
import redis.asyncio as redis

redis_client = redis.from_url(os.environ["REDIS_URL"])

async def check_rate_limit(ip: str) -> bool:
    key = f"login_attempt:{ip}"
    count = await redis_client.incr(key)
    if count == 1:
        await redis_client.expire(key, 60)  # 1分钟窗口
    return count <= 5  # 每分钟最多5次
```

### 3.4 方案一优缺点

| 维度 | 评估 |
|------|------|
| **改造成本** | 低（2-3周工程量） |
| **技术难度** | 中（PostgreSQL 迁移需仔细测试） |
| **优点** | 快速上线、运维简单、成本低 |
| **缺点** | 无水平扩展、单点故障、Sandbox 仍用 DooD |
| **适用规模** | < 100 并发用户 |

---

## 4. 方案二：多副本 + 外部存储（推荐中规模）

### 4.1 适用场景

- 用户量 100-1000 并发
- 需要零停机部署
- 有 DevOps 基础设施支撑

### 4.2 架构图

```
Internet
  │
  ▼
云 LB（ALB/CLB）+ TLS 终止
  │
  ▼
Nginx 集群（2+ 节点）
  │
  ├─→ Frontend Pod × 2（Next.js，无状态）
  │
  └─→ Gateway Pod × N（FastAPI，无状态目标）
          │
          ├── PostgreSQL（主从或 RDS）
          │    ├── 主：写操作
          │    └── 从：读操作（threads 查询、用户列表）
          ├── Redis Cluster
          │    ├── 登录限速（全局精确）
          │    ├── LangGraph checkpoint 缓存
          │    └── session 黑名单（JWT revoke）
          ├── 对象存储（S3/OSS/COS）
          │    └── 线程文件（uploads/outputs/workspace）
          └── Sandbox 集群
               └── AioSandboxProvider → RemoteSandboxBackend
                    └── K3s/K8s provisioner (8002)
```

### 4.3 关键改造步骤

#### 4.3.1 状态外置：文件系统 → 对象存储

当前线程文件存储在：
```
.deer-flow/users/{user_id}/threads/{thread_id}/user-data/
```
（`backend/packages/harness/deerflow/config/paths.py`）

**改造目标：** 抽象 `FileStorage` 接口，支持 S3 backend。

```python
# 新增 deerflow/storage/interface.py
class FileStorageBackend(Protocol):
    async def read(self, path: str) -> bytes: ...
    async def write(self, path: str, data: bytes) -> None: ...
    async def list_dir(self, path: str) -> list[str]: ...
    async def delete(self, path: str) -> None: ...

# 实现 deerflow/storage/s3_backend.py
class S3FileStorageBackend:
    def __init__(self, bucket: str, prefix: str):
        self.s3 = boto3.client("s3")
        self.bucket = bucket
        self.prefix = prefix
    
    async def read(self, path: str) -> bytes:
        obj = self.s3.get_object(Bucket=self.bucket, Key=f"{self.prefix}/{path}")
        return obj["Body"].read()
```

**配置变更（config.yaml）：**
```yaml
storage:
  backend: s3  # 或 local（默认）
  s3:
    bucket: deerflow-data
    prefix: production
    region: ap-beijing
    access_key: $AWS_ACCESS_KEY_ID
    secret_key: $AWS_SECRET_ACCESS_KEY
```

#### 4.3.2 LangGraph Checkpoint → PostgreSQL

```python
# backend/app/gateway/app.py 改造
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

@asynccontextmanager
async def lifespan(app: FastAPI):
    checkpointer = AsyncPostgresSaver.from_conn_string(
        settings.database_url
    )
    await checkpointer.setup()
    app.state.checkpointer = checkpointer
    yield
    await checkpointer.aclose()
```

#### 4.3.3 Gateway 无状态化

Gateway 需要去除所有进程内共享状态：

1. **MCP tools 缓存**（`deerflow/mcp/manager.py`）：`WeakValueDictionary` 缓存改为 Redis + 文件 mtime 检测
2. **Sandbox warm pool**（`aio_sandbox_provider.py`）：warm pool 在 K8s 下改为预创建 pod 池
3. **登录计数器**：进程内 dict → Redis
4. **技能缓存**（`deerflow/skills/loader.py`）：已基于文件 mtime，无状态，保持不变

#### 4.3.4 Sandbox 改造：DooD → Remote K3s

当前 DooD 模式（Docker out of Docker）在多副本下：
- 每个 Gateway Pod 都需要挂载 `/var/run/docker.sock`
- 安全风险：container escape → 宿主 root

**改造方向：** 使用已有的 `RemoteSandboxBackend` + provisioner 服务

```yaml
# config.yaml 改造
sandbox:
  use: deerflow.community.aio_sandbox.aio_sandbox_provider:AioSandboxProvider
  aio_sandbox:
    backend: remote  # 从 local_container 切换到 remote
    remote:
      provisioner_url: http://provisioner:8002
      # provisioner 通过 K8s API 管理 sandbox pod 生命周期
```

provisioner 服务（`docker/provisioner/app.py`）：
- 已实现 K3s namespace `deer-flow` 下的 sandbox pod 创建/删除/列举
- 支持 per-thread volume 挂载（线程数据隔离）
- 可配置 `SANDBOX_IMAGE`、资源限制

#### 4.3.5 水平扩展 Gateway

```yaml
# docker-compose.yaml 或 K8s Deployment
services:
  gateway:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Nginx 负载均衡（upstream）：
```nginx
upstream gateway_pool {
    least_conn;
    server gateway1:8001;
    server gateway2:8001;
    server gateway3:8001;
    keepalive 32;
}
```

**注意：** SSE 长连接（Agent 运行时）需要 `ip_hash` 或 sticky session，否则同一 thread 的多次请求可能路由到不同实例：
```nginx
upstream gateway_pool {
    ip_hash;  # 或使用 cookie-based sticky
    server gateway1:8001;
    server gateway2:8001;
}
```

### 4.4 方案二优缺点

| 维度 | 评估 |
|------|------|
| **改造成本** | 中（4-8周，需重构存储层） |
| **技术难度** | 高（异步 S3、PostgreSQL 迁移、无状态化） |
| **优点** | 水平扩展、零停机部署、容灾能力强 |
| **缺点** | 运维复杂度上升、S3 成本增加、调试难度增加 |
| **适用规模** | 100-1000 并发用户 |

---

## 5. 方案三：Kubernetes 云原生（大规模生产）

### 5.1 适用场景

- 用户量 > 1000 并发
- 企业级 SLA 要求（99.9%+）
- 有 K8s 运维团队

### 5.2 整体架构

```
Internet
  │
  ▼
Ingress Controller (Nginx/Traefik) + TLS (cert-manager)
  │
  ├── HPA 自动扩缩（基于 CPU/RPS）
  │
  ├── Frontend Deployment (2+ replicas)
  │    └── ConfigMap: BETTER_AUTH_SECRET, gateway URL
  │
  ├── Gateway Deployment (N replicas, HPA)
  │    ├── ConfigMap: config.yaml, extensions_config.json
  │    ├── Secret: API keys, DATABASE_URL, REDIS_URL
  │    └── 无 docker.sock 挂载（sandbox 全部走 provisioner）
  │
  ├── Provisioner Deployment (2 replicas)
  │    ├── ServiceAccount + RBAC（管理 sandbox namespace）
  │    └── 创建 sandbox pod，挂载 PVC
  │
  ├── PostgreSQL (RDS/CloudSQL 或 Operator)
  │    ├── 主库：写
  │    └── 读副本：查询优化
  │
  ├── Redis Cluster (Elasticache/Redis Operator)
  │
  ├── MinIO / S3 (对象存储)
  │    └── 线程数据、上传文件、输出文件
  │
  └── Sandbox Namespace (deer-flow-sandbox)
       └── 每次任务动态创建/销毁 sandbox pod
```

### 5.3 K8s 关键资源定义

#### 5.3.1 Gateway Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: deerflow-gateway
  namespace: deerflow
spec:
  replicas: 3
  selector:
    matchLabels:
      app: deerflow-gateway
  template:
    spec:
      containers:
      - name: gateway
        image: your-registry/deerflow-gateway:latest
        command:
          - sh
          - -c
          - "cd backend && PYTHONPATH=. uv run uvicorn app.gateway.app:app --host 0.0.0.0 --port 8001 --workers 4"
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: deerflow-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: deerflow-secrets
              key: redis-url
        - name: DEER_FLOW_STORAGE_BACKEND
          value: s3
        resources:
          requests:
            cpu: "1"
            memory: "2Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 5
          periodSeconds: 5
```

#### 5.3.2 HPA（水平自动扩缩）

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: deerflow-gateway-hpa
  namespace: deerflow
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: deerflow-gateway
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "100"
```

#### 5.3.3 Sandbox RBAC

```yaml
# provisioner 的 ServiceAccount，限制只能操作 deer-flow-sandbox namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: deer-flow-sandbox
  name: sandbox-manager
rules:
- apiGroups: [""]
  resources: ["pods", "pods/exec", "persistentvolumeclaims"]
  verbs: ["get", "list", "create", "delete", "watch"]
```

#### 5.3.4 NetworkPolicy（沙箱隔离）

```yaml
# 限制 sandbox pod 的网络访问
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: sandbox-isolation
  namespace: deer-flow-sandbox
spec:
  podSelector:
    matchLabels:
      app: sandbox
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: deerflow  # 只允许来自 gateway namespace
  egress:
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except:
        - 10.0.0.0/8    # 禁止访问内网
        - 172.16.0.0/12
        - 192.168.0.0/16
```

### 5.4 Helm Chart 结构建议

```
helm/deerflow/
├── Chart.yaml
├── values.yaml
├── values-production.yaml    # 生产环境覆盖值
├── templates/
│   ├── gateway-deployment.yaml
│   ├── gateway-hpa.yaml
│   ├── frontend-deployment.yaml
│   ├── provisioner-deployment.yaml
│   ├── nginx-ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml           # External Secrets Operator 引用
│   ├── networkpolicy.yaml
│   └── rbac.yaml
└── charts/                   # 子 chart：postgresql, redis, minio
```

### 5.5 方案三优缺点

| 维度 | 评估 |
|------|------|
| **改造成本** | 高（8-16周，需重构存储+部署体系） |
| **技术难度** | 非常高（K8s、Helm、Operator、安全策略） |
| **优点** | 弹性伸缩、完整隔离、企业级运维能力 |
| **缺点** | 运维成本高、学习曲线陡峭、基础设施成本高 |
| **适用规模** | > 1000 并发用户 |

---

## 6. 多租户设计详解

### 6.1 当前多租户能力（已实现）

根据 `AUTH_DESIGN.md`，DeerFlow 已具备基础多租户隔离：

| 维度 | 实现状态 | 隔离粒度 |
|------|---------|---------|
| HTTP 认证 | ✅ 完整实现 | JWT + HttpOnly cookie + CSRF |
| Thread 元数据 | ✅ 完整实现 | `user_id` 外键过滤 |
| 文件系统 | ✅ 完整实现 | `users/{user_id}/threads/{thread_id}/` |
| Memory | ✅ 完整实现 | `users/{user_id}/memory.json` |
| 自定义 agent | ✅ 完整实现 | `users/{user_id}/agents/` |
| 角色管理 | ⚠️ 仅 admin/user | 无细粒度 RBAC |
| API 配额 | ❌ 未实现 | 无 per-user token limit |
| Skill 权限 | ❌ 未实现 | skills 全局共享 |
| OAuth 登录 | ❌ 占位未实现 | 无第三方登录 |

### 6.2 生产多租户补充改造

#### 6.2.1 RBAC 角色扩展

```python
# app/gateway/auth/models.py — 扩展角色
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    PRO_USER = "pro_user"        # 新增：付费用户
    ENTERPRISE = "enterprise"    # 新增：企业用户
    READONLY = "readonly"        # 新增：只读用户
```

```python
# 路由级权限检查
@router.post("/api/threads/{thread_id}/runs")
async def create_run(
    thread_id: str,
    body: RunRequest,
    user: User = Depends(require_permission(min_role=UserRole.USER))
):
    # 检查用户配额
    await check_user_quota(user)
    ...
```

#### 6.2.2 API 配额与 Token 限制

```python
# 新增 deerflow/quota/manager.py
class QuotaManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def check_and_consume(
        self, 
        user_id: str, 
        tokens_requested: int
    ) -> bool:
        """检查并消费用户配额"""
        key = f"quota:{user_id}:{today()}"
        current = await self.redis.get(key) or 0
        limit = await self.get_user_limit(user_id)  # 从 DB 读取
        
        if int(current) + tokens_requested > limit:
            raise QuotaExceededError(f"用户 {user_id} 配额已满")
        
        await self.redis.incrby(key, tokens_requested)
        await self.redis.expire(key, 86400)  # 24h 滚动窗口
        return True
```

**配额配置（config.yaml）：**
```yaml
quota:
  enabled: true
  default_daily_tokens: 100000    # 普通用户每日 token 上限
  pro_daily_tokens: 1000000       # 付费用户
  enterprise_daily_tokens: -1     # 不限制
  default_concurrent_threads: 3   # 同时运行的 agent 数
```

#### 6.2.3 Skill 按租户权限控制

```python
# deerflow/skills/loader.py — 扩展 skill 权限
class SkillPermission:
    ROLES: list[str]  # 允许的角色列表，e.g. ["admin", "enterprise"]

# SKILL.md frontmatter 新增字段
# ---
# name: Advanced PDF Processing
# required-role: enterprise
# ---
```

#### 6.2.4 租户级别的 MCP 配置

当前 MCP 配置（`extensions_config.json`）是全局的。多租户改造：

```python
# 按用户或租户存储 MCP 配置
# {base_dir}/users/{user_id}/extensions_config.json

async def get_user_mcp_tools(user_id: str) -> list[Tool]:
    user_config_path = Paths.user_extensions_config(user_id)
    global_config_path = Paths.extensions_config_path()
    
    # 合并：全局基础 + 用户自定义
    config = merge_configs(global_config_path, user_config_path)
    return await load_mcp_tools(config)
```

---

## 7. 高可用配置

### 7.1 健康检查与自动恢复

当前 `/health` 端点（`app/gateway/app.py`）已存在，但只检查服务存活。

**增强型健康检查：**
```python
@app.get("/health")
async def health_check():
    checks = {}
    
    # 数据库连通性
    try:
        await db.execute("SELECT 1")
        checks["database"] = "ok"
    except Exception as e:
        checks["database"] = f"error: {e}"
    
    # Redis 连通性
    try:
        await redis.ping()
        checks["redis"] = "ok"
    except Exception as e:
        checks["redis"] = f"error: {e}"
    
    # Sandbox provisioner（如果启用）
    # ...
    
    status = "healthy" if all(v == "ok" for v in checks.values()) else "degraded"
    return {"status": status, "checks": checks}
```

### 7.2 数据库高可用

**PostgreSQL 主从（Patroni 方案）：**
```yaml
# patroni-config.yaml
bootstrap:
  dcs:
    ttl: 30
    loop_wait: 10
    retry_timeout: 10
    maximum_lag_on_failover: 1048576
  initdb:
  - encoding: UTF8
  - data-checksums

postgresql:
  use_pg_rewind: true
  parameters:
    wal_level: replica
    max_wal_senders: 5
    max_replication_slots: 5
```

**连接池（PgBouncer）：**
```ini
[databases]
deerflow = host=postgres-primary port=5432 dbname=deerflow

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

### 7.3 Redis 高可用

```yaml
# Redis Sentinel 最小配置（3 节点）
sentinel:
  - host: redis-sentinel-1
    port: 26379
  - host: redis-sentinel-2
    port: 26379
  - host: redis-sentinel-3
    port: 26379

master_name: deerflow-redis
```

### 7.4 Gateway 无状态保证

去除进程内状态后，Gateway Pod 可任意重启：
- ✅ 配置文件通过 ConfigMap/Secret 注入
- ✅ 线程数据在对象存储（S3）
- ✅ checkpoint 在 PostgreSQL
- ✅ session 状态在 Redis
- ⚠️ SSE 长连接中断需要客户端重连机制（前端已有 EventSource 重连，需验证）

### 7.5 灾难恢复

| 组件 | 备份策略 | RPO | RTO |
|------|---------|-----|-----|
| PostgreSQL | WAL 归档 + 每日全量备份到 S3 | 5分钟 | 30分钟 |
| Redis | AOF + RDB 定期备份 | 1分钟 | 5分钟 |
| 对象存储（S3） | 跨区域复制 | 实时 | 即时切换 |
| 配置文件 | Git 版本控制 | 实时 | 5分钟 |

---

## 8. 高性能配置

### 8.1 Gateway 性能调优

#### uvicorn worker 配置

```python
# backend/app/gateway/app.py — gunicorn + uvicorn workers
# 生产推荐：gunicorn -k uvicorn.workers.UvicornWorker
```

```bash
# 启动命令（替代当前 uvicorn 直接启动）
gunicorn app.gateway.app:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers $(( 2 * $(nproc) + 1 )) \
    --worker-connections 1000 \
    --timeout 600 \
    --graceful-timeout 30 \
    --bind 0.0.0.0:8001 \
    --access-logfile - \
    --error-logfile -
```

**对 agent 运行的影响：** Agent 运行是 CPU + I/O 混合型，推荐 `workers = 2 * CPU + 1`，CPU 4核则 9 workers。

#### 异步 LLM 调用

当前 LangChain 模型调用已是异步（`ainvoke`），无需改造。但需注意：
- 同一 worker 可以并发处理多个 agent run（asyncio 事件循环）
- CPU 密集型操作（token 计数、文档解析）可能阻塞事件循环，建议用 `asyncio.to_thread()`

### 8.2 Nginx 性能优化

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 65535;
    multi_accept on;
    use epoll;
}

http {
    # 连接复用
    keepalive_timeout 65;
    keepalive_requests 10000;
    
    # 压缩（JSON/HTML 响应）
    gzip on;
    gzip_types application/json text/html text/css;
    gzip_min_length 1024;
    
    # SSE 不压缩
    gzip_proxied off;
    
    # 缓冲调优
    proxy_buffer_size 16k;
    proxy_buffers 4 32k;
    
    # 上游连接池
    upstream gateway_pool {
        keepalive 100;       # 保持 100 个长连接
        server gateway1:8001 weight=1 max_fails=3 fail_timeout=30s;
        server gateway2:8001 weight=1 max_fails=3 fail_timeout=30s;
    }
}
```

### 8.3 Sandbox 性能：Warm Pool

当前 `AioSandboxProvider` 已实现 warm pool（`aio_sandbox_provider.py`），但需配置：

```yaml
# config.yaml
sandbox:
  aio_sandbox:
    warm_pool_size: 5          # 预启动 5 个 sandbox 容器
    idle_timeout_seconds: 300  # 空闲 5 分钟后回收
    max_concurrent: 20         # 最多同时 20 个 sandbox
    backend: remote            # 生产用 remote（K8s provisioner）
```

**Sandbox 冷启动时间参考：**
- Docker 拉取镜像：10-30s（首次）
- 容器启动：1-2s
- Warm pool 预热：< 100ms（直接从 pool 取）

### 8.4 数据库查询优化

关键索引（需要在 PostgreSQL 迁移时添加）：

```sql
-- threads_meta 表
CREATE INDEX idx_threads_user_id ON threads_meta(user_id);
CREATE INDEX idx_threads_created_at ON threads_meta(created_at DESC);
CREATE INDEX idx_threads_user_created ON threads_meta(user_id, created_at DESC);

-- runs 表
CREATE INDEX idx_runs_thread_id ON runs(thread_id);
CREATE INDEX idx_runs_status ON runs(status);

-- 全文搜索（可选）
CREATE INDEX idx_threads_title_fts ON threads_meta USING gin(to_tsvector('simple', title));
```

### 8.5 LLM 调用优化

```yaml
# config.yaml — 模型配置优化
models:
  - name: gpt-4
    max_retries: 2
    request_timeout: 120.0    # 适当超时，避免长时间占用 worker
    # 考虑使用带 streaming 的模型避免首 token 延迟
```

**LLM Gateway（可选）：** 在 DeerFlow 和 LLM provider 之间加一层 LiteLLM Proxy，实现：
- 统一的 token 计量
- 多 provider 负载均衡
- 本地缓存重复 prompt

---

## 9. 安全加固

### 9.1 网络安全

#### TLS 配置（Nginx）
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_prefer_server_ciphers off;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:...;
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
ssl_stapling on;
ssl_stapling_verify on;
```

#### 安全 Headers
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### 9.2 Sandbox 安全

#### 消除 Docker Socket 暴露
- **当前**：`/var/run/docker.sock` 挂载到 gateway 容器（DooD）
- **改造**：使用 `RemoteSandboxBackend`，Gateway 通过 HTTP API 与 provisioner 通信，provisioner 运行在独立 Pod，持有最小 K8s RBAC 权限

```yaml
# provisioner 的最小 RBAC
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "create", "delete", "watch"]
  resourceNames: []  # 可进一步限制为特定 namespace
- apiGroups: [""]
  resources: ["persistentvolumeclaims"]
  verbs: ["get", "create", "delete"]
```

#### Sandbox 资源限制
```yaml
# sandbox pod 资源配额
resources:
  requests:
    cpu: "0.5"
    memory: "512Mi"
  limits:
    cpu: "2"
    memory: "2Gi"
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  readOnlyRootFilesystem: false  # sandbox 需要写文件
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

#### SandboxAuditMiddleware（已实现）
当前 `SandboxAuditMiddleware` 对 bash 工具调用做 high/medium/pass 分级：
- `high`：拒绝（如 `rm -rf /`、curl 外网 pipe 执行）
- `medium`：记录审计日志
- `pass`：直接执行

**生产加固建议：** 将审计日志写入不可篡改的存储（S3 + Object Lock），并接入 SIEM（Splunk/ELK）。

### 9.3 认证加固

#### JWT Secret 轮换
```python
# 支持多个有效 secret，便于轮换
JWT_SECRETS = [
    os.environ["BETTER_AUTH_SECRET"],          # 当前 secret（签发+验证）
    os.environ.get("BETTER_AUTH_SECRET_OLD"),  # 旧 secret（仅验证，轮换期使用）
]
```

#### OAuth 接入（后续改造）
现有 `app/gateway/routers/auth.py` 已预留 OAuth 端点，需要接入：
1. GitHub OAuth App
2. Google OAuth 2.0
3. 企业 SSO（SAML 2.0 / OIDC）

```python
# 目标接口（已预留）
@router.get("/api/v1/auth/oauth/{provider}")
async def oauth_redirect(provider: str): ...

@router.get("/api/v1/auth/oauth/{provider}/callback")
async def oauth_callback(provider: str, code: str): ...
```

#### Session 管理
```python
# JWT 黑名单（用于强制登出）
# 当前依赖 token_version 机制，等效于"个人黑名单"
# 如需全局黑名单（如账户封禁），需要 Redis set

async def revoke_all_sessions(user_id: str):
    """封禁用户：increment token_version 使所有 JWT 失效"""
    await db.execute(
        "UPDATE users SET token_version = token_version + 1 WHERE id = ?",
        [user_id]
    )
```

### 9.4 输入验证与注入防护

```python
# 当前已有的防护（auth_middleware.py、authz.py）
# 需要额外加固：

# 1. 上传文件类型白名单
ALLOWED_UPLOAD_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".png", ".jpg"}

# 2. Thread ID 格式校验（防路径穿越）
THREAD_ID_PATTERN = re.compile(r'^[a-f0-9-]{36}$')  # UUID 格式

# 3. SQL 注入：使用参数化查询（当前 SQLAlchemy 已保证，迁移后需验证）
```

### 9.5 Secrets 管理

**推荐方案：** HashiCorp Vault 或 K8s External Secrets Operator

```yaml
# External Secrets Operator 示例
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: deerflow-secrets
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: ClusterSecretStore
  target:
    name: deerflow-secrets
  data:
  - secretKey: database-url
    remoteRef:
      key: deerflow/production
      property: database_url
  - secretKey: openai-api-key
    remoteRef:
      key: deerflow/production
      property: openai_api_key
```

---

## 10. 方案对比总结

| 维度 | 方案一：单机强化 | 方案二：多副本 | 方案三：K8s 云原生 |
|------|--------------|-------------|----------------|
| **改造工期** | 2-3周 | 4-8周 | 8-16周 |
| **技术难度** | 中 | 高 | 非常高 |
| **基础设施成本** | 低（1台服务器） | 中（2-5台VM） | 高（K8s集群） |
| **运维成本** | 低 | 中 | 高 |
| **并发能力** | < 100 | 100-1000 | 1000+ |
| **可用性** | 99% | 99.9% | 99.99% |
| **水平扩展** | ❌ | ✅ | ✅ 自动 |
| **零停机部署** | ❌ | ✅ | ✅ |
| **沙箱安全** | ⚠️ DooD | ✅ Remote | ✅ 隔离 namespace |
| **多租户隔离** | ✅ 基础 | ✅ 完整 | ✅ 完整 + 网络 |
| **适用阶段** | MVP/早期 | 成长期 | 规模化 |

### 推荐路径

```
阶段1（0-3月）: 方案一 — 快速上线，验证产品市场适配
    ↓
阶段2（3-9月）: 方案二 — 存储外置 + 多副本，支撑增长
    ↓
阶段3（9月+）:  方案三 — K8s 化，弹性应对高峰
```

---

## 11. 具体改造建议清单

### 11.1 P0（上线前必做）

| 编号 | 改造项 | 文件/模块 | 说明 |
|------|-------|---------|------|
| P0-1 | 启用 TLS | `docker/nginx/nginx.conf` | Let's Encrypt 或商业证书 |
| P0-2 | 设置安全 HTTP Headers | `docker/nginx/nginx.conf` | X-Frame-Options, HSTS 等 |
| P0-3 | 配置 Nginx 登录限速 | `docker/nginx/nginx.conf` | `limit_req_zone` |
| P0-4 | 强化 BETTER_AUTH_SECRET | `.env` | 至少 32 字节随机，不使用弱密码 |
| P0-5 | 禁用 Swagger UI（生产） | `app/gateway/app.py` | `if not DEBUG: app.openapi_url = None` |
| P0-6 | 配置 GATEWAY_CORS_ORIGINS | `config.yaml` | 明确白名单，不用 `*` |
| P0-7 | 切换 Sandbox to AioProvider | `config.yaml` | 启用 Docker 容器隔离 |
| P0-8 | 备份策略 | infra | 数据库+文件每日备份 |

### 11.2 P1（上线后 1 个月内）

| 编号 | 改造项 | 文件/模块 | 说明 |
|------|-------|---------|------|
| P1-1 | SQLite → PostgreSQL | `persistence/` + LangGraph | 支持多进程并发写 |
| P1-2 | Redis 全局登录限速 | `auth_middleware.py` | 替换进程内 dict |
| P1-3 | 健康检查增强 | `app/gateway/app.py` | 检查 DB/Redis 连通性 |
| P1-4 | per-user Token 配额 | 新增 `quota/manager.py` | 防止单用户耗尽资源 |
| P1-5 | 审计日志持久化 | `sandbox/audit_middleware.py` | 写入不可篡改存储 |
| P1-6 | 消除 Docker socket | `config.yaml` + provisioner | 切换到 RemoteSandboxBackend |

### 11.3 P2（长期改造）

| 编号 | 改造项 | 文件/模块 | 说明 |
|------|-------|---------|------|
| P2-1 | 文件系统 → S3 | `config/paths.py` + 新增 storage 抽象 | 支持多副本共享 |
| P2-2 | OAuth 登录 | `routers/auth.py` | GitHub/Google/企业 SSO |
| P2-3 | RBAC 角色细化 | `auth/models.py` | pro_user/enterprise 角色 |
| P2-4 | Helm Chart | 新增 `helm/` | K8s 部署标准化 |
| P2-5 | 可观测性 | 新增 OpenTelemetry | 链路追踪 + 指标 + 日志 |
| P2-6 | 多区域部署 | infra | 数据库主从跨区，S3 跨区复制 |
| P2-7 | 租户级 MCP 配置 | `mcp/manager.py` | per-user extensions_config |
| P2-8 | Sandbox 沙箱网络隔离 | K8s NetworkPolicy | 防租户间网络互访 |

---

## 附录：关键配置示例（生产 config.yaml 摘要）

```yaml
# 生产环境 config.yaml 关键部分

log_level: warning  # 生产用 warning/error，减少 I/O

# 认证
auth:
  jwt_expiry_hours: 8         # 较短 JWT 有效期
  cors_origins:               # 明确白名单
    - https://yourdomain.com

# Sandbox（生产推荐）
sandbox:
  use: deerflow.community.aio_sandbox.aio_sandbox_provider:AioSandboxProvider
  aio_sandbox:
    backend: remote
    warm_pool_size: 5
    idle_timeout_seconds: 300
    max_concurrent: 20
    remote:
      provisioner_url: http://provisioner:8002

# 配额（需自行实现）
quota:
  enabled: true
  default_daily_tokens: 200000

# 摘要（减少超长 context 的 LLM 调用成本）
summarization:
  enabled: true
  trigger_at_token_fraction: 0.7

# Token 用量记录
token_usage:
  enabled: true
```

---

## 附录：可观测性建议

生产环境最小可观测性栈：

```
DeerFlow Gateway
  │
  ├── Prometheus metrics（/metrics 端点）
  │    ├── http_requests_total（by endpoint, status）
  │    ├── agent_run_duration_seconds
  │    ├── sandbox_acquire_duration_seconds
  │    └── llm_tokens_total（by model, user）
  │
  ├── Structured JSON logs → ELK/Loki
  │    ├── request_id 串联全链路
  │    └── user_id 追踪用户操作
  │
  └── OpenTelemetry traces → Jaeger/Tempo
       └── LangGraph agent run → tool call → sandbox → LLM call
```

**FastAPI 集成 OpenTelemetry：**
```python
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor

FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()  # 追踪 LLM API 调用
```

---

*本文档基于 DeerFlow 仓库 `acongfly/deer-flow` 当前代码分析撰写。具体实现细节请参考：*
- `backend/docs/ARCHITECTURE.md` — 系统架构总览
- `backend/docs/AUTH_DESIGN.md` — 认证与隔离详设
- `docker/docker-compose.yaml` — 部署配置
- `docs/sandbox-agent-analysis.md` — Sandbox 机制分析
