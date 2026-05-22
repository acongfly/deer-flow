# Apple Container 支持

DeerFlow 现在支持在 macOS 上将 Apple Container 作为首选容器运行时，并在需要时自动回退到 Docker。

## 概览

从此版本开始，DeerFlow 会在 macOS 上自动检测并优先使用 Apple Container；在以下情况下会回退到 Docker：
- 未安装 Apple Container
- 运行在非 macOS 平台上

这为 Apple Silicon Mac 提供了更好的性能，同时保持了跨平台兼容性。

## 优势

### 在配备 Apple Container 的 Apple Silicon Mac 上：
- **更好的性能**：原生 ARM64 执行，无需 Rosetta 2 转译
- **更低的资源占用**：比 Docker Desktop 更轻量
- **原生集成**：使用 macOS Virtualization.framework

### 回退到 Docker 时：
- 完整的向后兼容性
- 适用于所有平台（macOS、Linux、Windows）
- 无需修改配置

## 要求

### Apple Container（仅 macOS）：
- macOS 15.0 或更高版本
- Apple Silicon（M1/M2/M3/M4）
- 已安装 Apple Container CLI

### 安装：
```bash
# Download from GitHub releases
# https://github.com/apple/container/releases

# Verify installation
container --version

# Start the service
container system start
```

### Docker（所有平台）：
- Docker Desktop 或 Docker Engine

## 工作原理

### 自动检测

`AioSandboxProvider` 会自动检测可用的容器运行时：

1. 在 macOS 上：尝试执行 `container --version`
   - 成功 → 使用 Apple Container
   - 失败 → 回退到 Docker

2. 在其他平台上：直接使用 Docker

### 运行时差异

两种运行时使用几乎相同的命令语法：

**容器启动：**
```bash
# Apple Container
container run --rm -d -p 8080:8080 -v /host:/container -e KEY=value image

# Docker
docker run --rm -d -p 8080:8080 -v /host:/container -e KEY=value image
```

**容器清理：**
```bash
# Apple Container (with --rm flag)
container stop <id>  # Auto-removes due to --rm

# Docker (with --rm flag)
docker stop <id>     # Auto-removes due to --rm
```

### 实现细节

实现位于 `backend/packages/harness/deerflow/community/aio_sandbox/aio_sandbox_provider.py`：

- `_detect_container_runtime()`：在启动时检测可用运行时
- `_start_container()`：使用检测到的运行时；若为 Apple Container，则跳过 Docker 专属选项
- `_stop_container()`：根据运行时使用对应的停止命令

## 配置

无需任何配置改动！系统会自动工作。

不过，你可以通过日志确认当前使用的是哪种运行时：

```
INFO:deerflow.community.aio_sandbox.aio_sandbox_provider:Detected Apple Container: container version 0.1.0
INFO:deerflow.community.aio_sandbox.aio_sandbox_provider:Starting sandbox container using container: ...
```

或者在使用 Docker 时：
```
INFO:deerflow.community.aio_sandbox.aio_sandbox_provider:Apple Container not available, falling back to Docker
INFO:deerflow.community.aio_sandbox.aio_sandbox_provider:Starting sandbox container using docker: ...
```

## 容器镜像

两种运行时都使用兼容 OCI 的镜像。默认镜像可同时适用于二者：

```yaml
sandbox:
  use: deerflow.community.aio_sandbox:AioSandboxProvider
  image: enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest  # Default image
```

请确保镜像适用于对应架构：
- Apple Silicon 上的 Apple Container 需要 ARM64
- Intel Mac 上的 Docker 需要 AMD64
- 多架构镜像可同时兼容二者

### 预拉取镜像（推荐）

**重要**：容器镜像通常很大（500MB+），首次使用时才会拉取，这可能导致长时间等待且缺少清晰反馈。

**最佳实践**：在设置阶段先预拉取镜像：

```bash
# From project root
make setup-sandbox
```

该命令会：
1. 从 `config.yaml` 读取已配置镜像（若无则使用默认值）
2. 检测可用运行时（Apple Container 或 Docker）
3. 拉取镜像并显示进度
4. 验证镜像已可用

**手动预拉取**：

```bash
# Using Apple Container
container image pull enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest

# Using Docker
docker pull enterprise-public-cn-beijing.cr.volces.com/vefaas-public/all-in-one-sandbox:latest
```

如果跳过预拉取，镜像会在第一次执行 agent 时自动拉取，具体耗时取决于你的网络速度，可能需要数分钟。

## 清理脚本

项目内包含一个同时支持两种运行时的统一清理脚本：

**脚本：** `scripts/cleanup-containers.sh`

**用法：**
```bash
# Clean up all DeerFlow sandbox containers
./scripts/cleanup-containers.sh deer-flow-sandbox

# Custom prefix
./scripts/cleanup-containers.sh my-prefix
```

**Makefile 集成：**

`Makefile` 中的所有清理命令都会自动处理两种运行时：
```bash
make stop   # Stops all services and cleans up containers
make clean  # Full cleanup including logs
```

## 测试

测试容器运行时检测：

```bash
cd backend
python test_container_runtime.py
```

该测试会：
1. 检测可用运行时
2. 视情况启动一个测试容器
3. 验证连通性
4. 清理环境

## 故障排查

### 在 macOS 上未检测到 Apple Container

1. 检查是否已安装：
   ```bash
   which container
   container --version
   ```

2. 检查服务是否已启动：
   ```bash
   container system start
   ```

3. 检查日志中的检测信息：
   ```bash
   # Look for detection message in application logs
   grep "container runtime" logs/*.log
   ```

### 容器未被清理干净

1. 手动检查正在运行的容器：
   ```bash
   # Apple Container
   container list

   # Docker
   docker ps
   ```

2. 手动运行清理脚本：
   ```bash
   ./scripts/cleanup-containers.sh deer-flow-sandbox
   ```

### 性能问题

- 在 Apple Silicon 上，Apple Container 理应更快
- 如果遇到问题，可以通过临时重命名 `container` 命令来强制使用 Docker：
   ```bash
   # Temporary workaround - not recommended for permanent use
   sudo mv /opt/homebrew/bin/container /opt/homebrew/bin/container.bak
   ```

## 参考资料

- [Apple Container GitHub](https://github.com/apple/container)
- [Apple Container Documentation](https://github.com/apple/container/blob/main/docs/)
- [OCI Image Spec](https://github.com/opencontainers/image-spec)
