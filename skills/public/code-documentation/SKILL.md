---
name: code-documentation
description: 当用户请求为代码、API、库、仓库或软件项目生成、创建或改进文档时使用此 skill。支持 README 生成、API 参考文档、行内代码注释、架构文档、changelog 生成以及开发者指南。当请求类似“document this code”“create a README”“generate API docs”“write developer guide”或出于文档目的分析代码库时触发。
---

# 代码文档 Skill

## 概述

此 skill 用于为软件项目、代码库、库和 API 生成专业且完整的文档。它借鉴 React、Django、Stripe 和 Kubernetes 等项目的行业最佳实践，生成准确、结构清晰且对新贡献者和资深开发者都实用的文档。

输出范围可以从单文件 README 到多文档开发者指南，并始终与项目复杂度和用户需求相匹配。

## 核心能力

- 生成完整的 README.md，包括徽章、安装、使用方式和 API 参考
- 通过分析源码创建 API 参考文档
- 生成包含图表的架构与设计文档
- 编写开发者入门与贡献指南
- 根据提交历史或发布说明生成 changelog
- 按语言特定约定创建行内代码文档
- 支持 JSDoc、docstrings、GoDoc、Javadoc 和 Rustdoc 格式
- 根据项目所用语言与生态调整文档风格

## 何时使用此 Skill

**在以下情况下始终加载此 skill：**

- 用户要求为任意代码“document”“create docs”或“write documentation”
- 用户请求 README、API 参考或开发者指南
- 用户分享代码库或仓库并希望自动生成文档
- 用户要求改进或更新现有文档
- 用户需要架构文档，包括图表
- 用户请求 changelog 或迁移指南

## 文档工作流

### 阶段 1：代码库分析

在编写任何文档之前，先彻底理解代码库。

#### 步骤 1.1：项目发现

识别项目基础信息：

| 字段 | 如何判断 |
|-------|-----------------|
| **Language(s)** | 检查文件扩展名、`package.json`、`pyproject.toml`、`go.mod`、`Cargo.toml` 等 |
| **Framework** | 查看依赖中是否存在已知框架（React、Django、Express、Spring 等） |
| **Build System** | 检查 `Makefile`、`CMakeLists.txt`、`webpack.config.js`、`build.gradle` 等 |
| **Package Manager** | npm/yarn/pnpm、pip/uv/poetry、cargo、go modules 等 |
| **Project Structure** | 梳理目录树以理解架构 |
| **Entry Points** | 查找主文件、CLI 入口、导出模块 |
| **Existing Docs** | 检查现有 README、docs/、wiki 或行内文档 |

#### 步骤 1.2：代码结构分析

使用 sandbox tools 探索代码库：

```bash
# Get directory structure
ls /mnt/user-data/uploads/project-dir/

# Read key files
read_file /mnt/user-data/uploads/project-dir/package.json
read_file /mnt/user-data/uploads/project-dir/pyproject.toml

# Search for public API surfaces
grep -r "export " /mnt/user-data/uploads/project-dir/src/
grep -r "def " /mnt/user-data/uploads/project-dir/src/ --include="*.py"
grep -r "func " /mnt/user-data/uploads/project-dir/ --include="*.go"
```

#### 步骤 1.3：确定文档范围

根据分析结果，确定应产出哪些文档：

| 项目规模 | 推荐文档 |
|-------------|--------------------------|
| **单文件 / 脚本** | 行内注释 + 使用说明头部 |
| **小型库** | README + API 参考 |
| **中型项目** | README + API 文档 + 示例 |
| **大型项目** | README + 架构 + API + Contributing + Changelog |

### 阶段 2：文档生成

#### 步骤 2.1：README 生成

每个项目都需要 README。遵循以下结构：

```markdown
# Project Name

[One-line project description — what it does and why it matters]

[![Badge](link)](#) [![Badge](link)](#)

## Features

- [Key feature 1 — brief description]
- [Key feature 2 — brief description]
- [Key feature 3 — brief description]

## Quick Start

### Prerequisites

- [Prerequisite 1 with version requirement]
- [Prerequisite 2 with version requirement]

### Installation

[Installation commands with copy-paste-ready code blocks]

### Basic Usage

[Minimal working example that demonstrates core functionality]

## Documentation

- [Link to full API reference if separate]
- [Link to architecture docs if separate]
- [Link to examples directory if applicable]

## API Reference

[Inline API reference for smaller projects OR link to generated docs]

## Configuration

[Environment variables, config files, or runtime options]

## Examples

[2-3 practical examples covering common use cases]

## Development

### Setup

[How to set up a development environment]

### Testing

[How to run tests]

### Building

[How to build the project]

## Contributing

[Contribution guidelines or link to CONTRIBUTING.md]

## License

[License information]
```

#### 步骤 2.2：API 参考生成

对于每一个公开 API 面，都应记录：

**Function / Method 文档：**

```markdown
### `functionName(param1, param2, options?)`

Brief description of what this function does.

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `param1` | `string` | Yes | — | Description of param1 |
| `param2` | `number` | Yes | — | Description of param2 |
| `options` | `Object` | No | `{}` | Configuration options |
| `options.timeout` | `number` | No | `5000` | Timeout in milliseconds |

**Returns:** `Promise<Result>` — Description of return value

**Throws:**
- `ValidationError` — When param1 is empty
- `TimeoutError` — When the operation exceeds the timeout

**Example:**

\`\`\`javascript
const result = await functionName("hello", 42, { timeout: 10000 });
console.log(result.data);
\`\`\`
```

**Class 文档：**

```markdown
### `ClassName`

Brief description of the class and its purpose.

**Constructor:**

\`\`\`javascript
new ClassName(config)
\`\`\`

| Parameter | Type | Description |
|-----------|------|-------------|
| `config.option1` | `string` | Description |
| `config.option2` | `boolean` | Description |

**Methods:**

- [`method1()`](#method1) — Brief description
- [`method2(param)`](#method2) — Brief description

**Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `property1` | `string` | Description |
| `property2` | `number` | Read-only. Description |
```

#### 步骤 2.3：架构文档

对于中大型项目，应包含架构文档：

```markdown
# Architecture Overview

## System Diagram

[Include a Mermaid diagram showing the high-level architecture]

\`\`\`mermaid
graph TD
    A[Client] --> B[API Gateway]
    B --> C[Service A]
    B --> D[Service B]
    C --> E[(Database)]
    D --> E
\`\`\`

## Component Overview

### Component Name
- **Purpose**: What this component does
- **Location**: `src/components/name/`
- **Dependencies**: What it depends on
- **Public API**: Key exports or interfaces

## Data Flow

[Describe how data flows through the system for key operations]

## Design Decisions

### Decision Title
- **Context**: What situation led to this decision
- **Decision**: What was decided
- **Rationale**: Why this approach was chosen
- **Trade-offs**: What was sacrificed
```

#### 步骤 2.4：行内代码文档

生成符合语言习惯的行内文档：

**Python（Docstrings — Google 风格）：**
```python
def process_data(input_path: str, options: dict | None = None) -> ProcessResult:
    """Process data from the given file path.

    Reads the input file, applies transformations based on the provided
    options, and returns a structured result object.

    Args:
        input_path: Absolute path to the input data file.
            Supports CSV, JSON, and Parquet formats.
        options: Optional configuration dictionary.
            - "validate" (bool): Enable input validation. Defaults to True.
            - "format" (str): Output format ("json" or "csv"). Defaults to "json".

    Returns:
        A ProcessResult containing the transformed data and metadata.

    Raises:
        FileNotFoundError: If input_path does not exist.
        ValidationError: If validation is enabled and data is malformed.

    Example:
        >>> result = process_data("/data/input.csv", {"validate": True})
        >>> print(result.row_count)
        1500
    """
```

**TypeScript（JSDoc / TSDoc）：**
```typescript
/**
 * Fetches user data from the API and transforms it for display.
 *
 * @param userId - The unique identifier of the user
 * @param options - Configuration options for the fetch operation
 * @param options.includeProfile - Whether to include the full profile. Defaults to `false`.
 * @param options.cache - Cache duration in seconds. Set to `0` to disable.
 * @returns The transformed user data ready for rendering
 * @throws {NotFoundError} When the user ID does not exist
 * @throws {NetworkError} When the API is unreachable
 *
 * @example
 * ```ts
 * const user = await fetchUser("usr_123", { includeProfile: true });
 * console.log(user.displayName);
 * ```
 */
```

**Go（GoDoc）：**
```go
// ProcessData reads the input file at the given path, applies the specified
// transformations, and returns the processed result.
//
// The input path must be an absolute path to a CSV or JSON file.
// If options is nil, default options are used.
//
// ProcessData returns an error if the file does not exist or cannot be parsed.
func ProcessData(inputPath string, options *ProcessOptions) (*Result, error) {
```

### 阶段 3：质量保证

#### 步骤 3.1：文档完整性检查

确认文档覆盖以下内容：

- [ ] **它是什么** —— 清晰的项目描述，新手也能理解
- [ ] **为什么存在** —— 它解决的问题与价值主张
- [ ] **如何安装** —— 可直接复制粘贴的安装命令
- [ ] **如何使用** —— 至少一个最小可运行示例
- [ ] **API 面** —— 所有公开函数、类和类型均有文档
- [ ] **配置** —— 所有环境变量、配置文件和选项
- [ ] **错误处理** —— 常见错误及其解决方式
- [ ] **Contributing** —— 如何搭建开发环境并提交变更

#### 步骤 3.2：质量标准

| 标准 | 检查项 |
|----------|-------|
| **Accuracy** | 每个代码示例都必须与描述的 API 真正匹配并可运行 |
| **Completeness** | 不得遗漏任何公开 API 面 |
| **Consistency** | 全文格式与结构保持一致 |
| **Freshness** | 文档必须对应当前代码，而不是旧版本 |
| **Accessibility** | 不解释的术语不要出现，缩写首次出现时要定义 |
| **Examples** | 每个复杂概念至少给出一个实际示例 |

#### 步骤 3.3：交叉引用校验

确保：
- 所有提到的文件路径都真实存在于项目中
- 所有引用的函数和类都存在于代码中
- 所有代码示例都使用正确的函数签名
- 版本号与项目实际版本一致
- 所有链接（内部与外部）都有效

## 文档风格指南

### 写作原则

1. **先讲“为什么”** —— 在解释某物如何工作之前，先解释它为什么存在
2. **渐进式披露** —— 从简单开始，逐步增加复杂度
3. **以示例代替空谈** —— 优先使用代码示例，而非冗长说明
4. **主动语态** —— 写 “The function returns X”，而不是 “X is returned by the function”
5. **现在时** —— 写 “The server starts on port 8080”，而不是 “The server will start on port 8080”
6. **第二人称** —— 写 “You can configure...”，而不是 “Users can configure...”

### 格式规则

- 使用 ATX 风格标题（`#`、`##`、`###`）
- 使用带语言标识的围栏代码块（` ```python `、` ```bash `）
- 对结构化信息（参数、选项、配置）使用表格
- 对重要说明、警告和提示使用 admonitions
- 保持行宽易读（源码中的正文建议在 ~80-100 字符换行）
- 对函数名、文件路径、变量名和 CLI 命令使用 `code formatting`

### 语言特定约定

| 语言 | 文档格式 | 风格指南 |
|----------|-----------|-------------|
| Python | Google 风格 docstrings | PEP 257 |
| TypeScript/JavaScript | TSDoc / JSDoc | TypeDoc conventions |
| Go | GoDoc comments | Effective Go |
| Rust | Rustdoc (`///`) | Rust API Guidelines |
| Java | Javadoc | Oracle Javadoc Guide |
| C/C++ | Doxygen | Doxygen manual |

## 输出处理

生成后：

- 将文档文件保存到 `/mnt/user-data/outputs/`
- 对于多文件文档，保持项目目录结构
- 使用 `present_files` tool 向用户展示生成的文件
- 提供继续迭代特定章节或调整细节层级的选项
- 建议可能同样有价值的附加文档

## 说明

- 在编写文档前，始终分析真实代码——绝不要猜测 API 签名或行为
- 如果已存在文档，除非用户明确要求重写，否则保留其结构
- 对于大型代码库，优先记录公开 API 面和关键抽象
- 文档应使用与项目现有文档相同的语言；如果没有现有文档，默认使用英文
- 生成 changelog 时，使用 [Keep a Changelog](https://keepachangelog.com/) 格式
- 此 skill 可与 `deep-research` skill 搭配使用，用于记录第三方集成或依赖
