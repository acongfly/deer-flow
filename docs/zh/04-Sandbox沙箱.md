# 04 — 核心模块：Sandbox 沙箱系统

> 原始资料：[`backend/CLAUDE.md`](../../backend/CLAUDE.md) · [`backend/docs/ARCHITECTURE.md`](../../backend/docs/ARCHITECTURE.md)  
> 源码位置：`backend/packages/harness/deerflow/sandbox/`

---

## 1. 总体结构

```
deerflow/sandbox/
├── __init__.py
├── sandbox.py           # 抽象接口 Sandbox
├── sandbox_provider.py  # 抽象接口 SandboxProvider
├── middleware.py        # SandboxMiddleware（生命周期管理）
├── security.py          # 安全检查工具
├── search.py            # 沙箱发现/搜索
├── exceptions.py        # 沙箱相关异常
├── file_operation_lock.py # 文件操作锁
├── tools.py             # 沙箱工具：bash / ls / read_file / write_file / str_replace
└── local/               # 本地沙箱实现
    └── provider.py      # LocalSandboxProvider
```

社区沙箱（Docker 隔离）位于：
```
deerflow/community/
└── aio_sandbox/         # AioSandboxProvider（Docker-based）
```

---

## 2. 核心抽象接口

### Sandbox（抽象沙箱）

```python
class Sandbox(ABC):
    @abstractmethod
    def execute_command(self, command: str, timeout: int = 30) -> CommandResult: ...
    
    @abstractmethod
    def read_file(self, path: str) -> str: ...
    
    @abstractmethod
    def write_file(self, path: str, content: str, append: bool = False) -> None: ...
    
    @abstractmethod
    def list_dir(self, path: str) -> list[DirEntry]: ...
```

### SandboxProvider（沙箱提供者）

```python
class SandboxProvider(ABC):
    @abstractmethod
    def acquire(self, thread_id: str | None = None) -> Sandbox: ...
    
    @abstractmethod
    async def acquire_async(self, thread_id: str | None = None) -> Sandbox: ...
    
    @abstractmethod
    def get(self, sandbox_id: str) -> Sandbox | None: ...
    
    @abstractmethod
    def release(self, sandbox_id: str) -> None: ...
```

---

## 3. 两种实现

### 3.1 LocalSandboxProvider（本地文件系统）

- `acquire(thread_id)` 返回每线程独立的 `LocalSandbox`（id：`local:{thread_id}`）
- `path_mappings` 将虚拟路径 `/mnt/user-data/{workspace,uploads,outputs}` 映射到宿主机上该线程对应的物理路径
- 使用 LRU 缓存（默认 256 条），由 `threading.Lock` 保护
- `acquire(None)` 或 `acquire()` 保留传统通用单例（id：`local`），供无线程上下文的调用者使用

### 3.2 AioSandboxProvider（Docker 容器隔离，社区版）

- 每次使用 Docker 启动隔离容器
- 相同的虚拟路径 `/mnt/user-data/...` 通过 volume 挂载到容器内
- 提供完整的进程隔离和网络隔离

---

## 4. 虚拟路径系统

沙箱对 Agent 暴露统一的虚拟路径，屏蔽宿主机的真实路径：

| 虚拟路径 | 物理路径（本地沙箱）| 说明 |
|----------|---------------------|------|
| `/mnt/user-data/workspace/` | `backend/.deer-flow/users/{user_id}/threads/{thread_id}/user-data/workspace/` | Agent 工作区（读写）|
| `/mnt/user-data/uploads/` | `backend/.deer-flow/users/{user_id}/threads/{thread_id}/user-data/uploads/` | 用户上传文件（只读）|
| `/mnt/user-data/outputs/` | `backend/.deer-flow/users/{user_id}/threads/{thread_id}/user-data/outputs/` | 输出文件（读写）|
| `/mnt/skills/` | `deer-flow/skills/` | 技能目录（只读）|
| `/mnt/acp-workspace/` | `{base_dir}/users/{user_id}/threads/{thread_id}/acp-workspace/` | ACP Agent 工作区 |

**路径转换**：
- `LocalSandboxProvider` 在 `acquire` 时构建每线程的 `PathMapping` 列表
- `tools.py` 的 `replace_virtual_path()` / `replace_virtual_paths_in_command()` 作为纵深防御层
- **检测本地沙箱**：`is_local_sandbox()` 接受 `sandbox_id == "local"` 和 `sandbox_id.startswith("local:")`

---

## 5. 沙箱工具（暴露给 Agent 的工具）

**文件**：`backend/packages/harness/deerflow/sandbox/tools.py`

| 工具 | 签名 | 说明 |
|------|------|------|
| `bash` | `bash(command: str)` | 执行 shell 命令，含路径转换和错误处理 |
| `ls` | `ls(path: str)` | 目录列表（树形格式，最多 2 层）|
| `read_file` | `read_file(path: str, start_line: int, end_line: int)` | 读取文件内容，支持行范围 |
| `write_file` | `write_file(path: str, content: str, append: bool)` | 写入/追加文件，自动创建目录 |
| `str_replace` | `str_replace(path: str, old: str, new: str, replace_all: bool)` | 字符串替换（单次或全部）|

> **并发安全**：`str_replace` 的路径锁作用域是 `(sandbox.id, path)`，不同线程/沙箱不会相互干扰。

---

## 6. SandboxMiddleware 生命周期

**文件**：`backend/packages/harness/deerflow/sandbox/middleware.py`

```
before_model:
  → provider.acquire_async(thread_id)  # 异步获取/创建沙箱
  → state.sandbox = sandbox
  → state.thread_data.sandbox_id = sandbox.id

after_run（清理阶段）:
  → provider.release(sandbox_id)       # 释放沙箱资源
```

---

## 7. 配置

在 `config.yaml` 中配置：

```yaml
sandbox:
  use: local    # 可选：local | aio（Docker）| provisioner（K8s）
  
  # 如果 use: aio
  aio:
    image: "deerflow-sandbox:latest"
    timeout: 300
```

---

## 8. 开发步骤：实现自定义沙箱提供者

1. 继承 `SandboxProvider` 和 `Sandbox` 抽象类
2. 实现 `acquire`、`acquire_async`、`get`、`release` 方法
3. 在 `SandboxMiddleware` 中注册新提供者
4. 在 `config.yaml` 中配置 `sandbox.use: your_provider_class_path`

```python
# 示例：自定义沙箱提供者
from deerflow.sandbox.sandbox_provider import SandboxProvider
from deerflow.sandbox.sandbox import Sandbox

class MyCustomSandbox(Sandbox):
    def execute_command(self, command: str, timeout: int = 30):
        # 执行命令逻辑
        ...

class MyCustomSandboxProvider(SandboxProvider):
    def acquire(self, thread_id: str | None = None) -> Sandbox:
        return MyCustomSandbox(thread_id=thread_id)
    
    async def acquire_async(self, thread_id: str | None = None) -> Sandbox:
        return MyCustomSandbox(thread_id=thread_id)
```

---

## 9. 安全注意事项

- **本地沙箱没有进程隔离**：Agent 执行的 bash 命令在宿主机上运行，务必在生产环境中使用 AIO（Docker）沙箱
- **Guardrail 中间件**：在工具调用前可拦截危险操作（详见认证与安全文档）
- **SandboxAuditMiddleware**：记录所有沙箱操作的安全审计日志
- **路径验证**：`tools.py` 对虚拟路径进行验证，防止路径遍历攻击
