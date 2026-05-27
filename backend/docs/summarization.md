# 对话摘要

DeerFlow 包含自动对话摘要功能，用于处理接近模型 token 上限的长对话。启用后，系统会在保留最近上下文的同时，自动压缩较早的消息。

## 概述

摘要功能使用 LangChain 的 `SummarizationMiddleware` 监控对话历史，并根据可配置阈值触发摘要。启用后，它会：

1. 实时监控消息 token 数量
2. 在达到阈值时触发摘要
3. 在保留最近消息不变的同时摘要更早的交流内容
4. 将 AI/Tool 消息对保持在一起，以保证上下文连续性
5. 将摘要重新注入到对话中

## 配置

摘要功能在 `config.yaml` 中通过 `summarization` 键进行配置：

```yaml
summarization:
  enabled: true
  model_name: null  # Use default model or specify a lightweight model

  # Trigger conditions (OR logic - any condition triggers summarization)
  trigger:
    - type: tokens
      value: 4000
    # Additional triggers (optional)
    # - type: messages
    #   value: 50
    # - type: fraction
    #   value: 0.8  # 80% of model's max input tokens

  # Context retention policy
  keep:
    type: messages
    value: 20

  # Token trimming for summarization call
  trim_tokens_to_summarize: 4000

  # Custom summary prompt (optional)
  summary_prompt: null

  # Tool names treated as skill file reads for skill rescue
  skill_file_read_tool_names:
    - read_file
    - read
    - view
    - cat
```

### 配置选项

#### `enabled`
- **类型**：Boolean
- **默认值**：`false`
- **说明**：启用或禁用自动摘要

#### `model_name`
- **类型**：String 或 null
- **默认值**：`null`（使用默认模型）
- **说明**：用于生成摘要的模型。建议使用 `gpt-4o-mini` 或同类轻量、性价比高的模型。

#### `trigger`
- **类型**：单个 `ContextSize` 或 `ContextSize` 对象列表
- **必填**：启用时至少必须指定一个触发条件
- **说明**：触发摘要的阈值。采用 OR 逻辑——任意一个阈值满足时就会执行摘要。

**ContextSize 类型：**

1. **基于 token 的触发器**：当 token 数达到指定值时激活
   ```yaml
   trigger:
     type: tokens
     value: 4000
   ```

2. **基于消息数的触发器**：当消息数量达到指定值时激活
   ```yaml
   trigger:
     type: messages
     value: 50
   ```

3. **基于比例的触发器**：当 token 使用量达到模型最大输入 token 的某个比例时激活
   ```yaml
   trigger:
     type: fraction
     value: 0.8  # 80% of max input tokens
   ```

**多个触发器：**
```yaml
trigger:
  - type: tokens
    value: 4000
  - type: messages
    value: 50
```

#### `keep`
- **类型**：`ContextSize` 对象
- **默认值**：`{type: messages, value: 20}`
- **说明**：指定在摘要完成后要保留多少最近的对话历史。

**示例：**
```yaml
# Keep most recent 20 messages
keep:
  type: messages
  value: 20

# Keep most recent 3000 tokens
keep:
  type: tokens
  value: 3000

# Keep most recent 30% of model's max input tokens
keep:
  type: fraction
  value: 0.3
```

#### `trim_tokens_to_summarize`
- **类型**：Integer 或 null
- **默认值**：`4000`
- **说明**：为摘要调用准备消息时允许包含的最大 token 数。设为 `null` 可跳过裁剪（不建议用于非常长的对话）。

#### `summary_prompt`
- **类型**：String 或 null
- **默认值**：`null`（使用 LangChain 默认提示词）
- **说明**：用于生成摘要的自定义提示词模板。该提示词应引导模型提取最重要的上下文。

#### `preserve_recent_skill_count`
- **类型**：Integer（≥ 0）
- **默认值**：`5`
- **说明**：从摘要中“抢救”出来的、最近加载的 skill 文件数量。这里的 skill 文件读取是指：工具名在 `skill_file_read_tool_names` 中，且目标路径位于 `skills.container_path` 下（例如 `/mnt/skills/...`）的工具结果。这样可防止 agent 在压缩后丢失 skill 指令。设为 `0` 可完全禁用 skill rescue。

#### `preserve_recent_skill_tokens`
- **类型**：Integer（≥ 0）
- **默认值**：`25000`
- **说明**：为被抢救的 skill 读取结果预留的总 token 预算。一旦该预算耗尽，较旧的 skill bundle 将允许被摘要。

#### `preserve_recent_skill_tokens_per_skill`
- **类型**：Integer（≥ 0）
- **默认值**：`5000`
- **说明**：单个 skill 的 token 上限。若某个 skill 读取结果超过该大小，则不会被抢救（会像普通内容一样进入摘要流程）。

#### `skill_file_read_tool_names`
- **类型**：字符串列表
- **默认值**：`["read_file", "read", "view", "cat"]`
- **说明**：在摘要 rescue 过程中被视为 skill 文件读取的工具名称。只有当工具名称出现在该列表中，且其目标路径位于 `skills.container_path` 下时，该次工具调用才有资格进行 skill rescue。

**默认提示词行为：**
默认的 LangChain 提示词会指导模型：
- 提取质量最高、最相关的上下文
- 聚焦对整体目标至关重要的信息
- 避免重复已完成的动作
- 仅返回提取出的上下文

## 工作原理

### 摘要流程

1. **监控**：在每次模型调用前，middleware 会统计消息历史中的 token
2. **触发检查**：如果任意已配置阈值满足，就触发摘要
3. **消息划分**：消息会被拆分为：
   - 需要摘要的消息（超出 `keep` 阈值的较旧消息）
   - 需要保留的消息（位于 `keep` 阈值内的最近消息）
4. **摘要生成**：模型会为较旧消息生成精炼摘要
5. **上下文替换**：消息历史会更新为：
   - 移除所有旧消息
   - 添加一条摘要消息
   - 保留最近消息
6. **AI/Tool 对保护**：系统会确保 AI 消息及其对应的 tool 消息保持在一起
7. **Skill Rescue**：在生成摘要之前，最近加载的 skill 文件（工具名位于 `skill_file_read_tool_names` 中，且目标路径位于 `skills.container_path` 下的工具结果）会先从待摘要集合中提取出来，并追加到保留尾部之前。选择过程按“从新到旧”进行，并同时受 `preserve_recent_skill_count`、`preserve_recent_skill_tokens` 和 `preserve_recent_skill_tokens_per_skill` 三个预算约束。触发该工具调用的 AIMessage 及其配对的所有 ToolMessages 会一起移动，以保持 `tool_call` ↔ `tool_result` 的配对关系完整。

### Token 计数

- 使用基于字符数的近似 token 计数
- 对 Anthropic 模型：约 3.3 个字符对应 1 个 token
- 对其他模型：使用 LangChain 默认估算方式
- 可通过自定义 `token_counter` 函数进行定制

### 消息保留

middleware 会智能保留消息上下文：

- **最近消息**：始终根据 `keep` 配置原样保留
- **AI/Tool 对**：绝不会被拆开——如果截断点落在 tool 消息之间，系统会调整，以保持整个 AI + Tool 消息序列完整
- **摘要格式**：摘要会以 HumanMessage 的形式注入，格式如下：
  ```
  Here is a summary of the conversation to date:

  [Generated summary text]
  ```

## 最佳实践

### 选择触发阈值

1. **基于 token 的触发器**：适用于大多数场景，推荐使用
   - 建议设置为模型上下文窗口的 60-80%
   - 示例：对于 8K 上下文，可使用 4000-6000 tokens

2. **基于消息数的触发器**：适合控制对话长度
   - 适用于包含大量短消息的应用
   - 示例：根据平均消息长度设置为 50-100 条消息

3. **基于比例的触发器**：适合使用多个模型的场景
   - 会自动适配每个模型的容量
   - 示例：0.8（模型最大输入 token 的 80%）

### 选择保留策略（`keep`）

1. **基于消息数的保留**：适合大多数场景
   - 可保留自然的对话流
   - 推荐：15-25 条消息

2. **基于 token 的保留**：适用于需要精确控制时
   - 有助于精确管理 token 预算
   - 推荐：2000-4000 tokens

3. **基于比例的保留**：适合多模型设置
   - 会随模型容量自动缩放
   - 推荐：0.2-0.4（最大输入的 20-40%）

### 模型选择

- **推荐**：使用轻量、成本更低的模型生成摘要
  - 示例：`gpt-4o-mini`、`claude-haiku` 或同类模型
  - 摘要任务不需要最强大的模型
  - 对高调用量应用可显著节省成本

- **默认**：如果 `model_name` 为 `null`，则使用默认模型
  - 可能更昂贵，但可确保一致性
  - 适合简单配置

### 优化建议

1. **平衡触发器**：组合 token 和消息数触发器，以获得更稳健的处理效果
   ```yaml
   trigger:
     - type: tokens
       value: 4000
     - type: messages
       value: 50
   ```

2. **保守保留**：一开始保留更多消息，再根据表现进行调整
   ```yaml
   keep:
     type: messages
     value: 25  # Start higher, reduce if needed
   ```

3. **策略性裁剪**：限制发送给摘要模型的 token 数
   ```yaml
   trim_tokens_to_summarize: 4000  # Prevents expensive summarization calls
   ```

4. **持续监控并迭代**：跟踪摘要质量，并调整配置

## 故障排查

### 摘要质量问题

**问题**：摘要丢失了重要上下文

**解决方案**：
1. 增大 `keep` 的值以保留更多消息
2. 降低触发阈值以更早进行摘要
3. 自定义 `summary_prompt`，强调关键信息
4. 为摘要使用能力更强的模型

### 性能问题

**问题**：摘要调用耗时过长

**解决方案**：
1. 为摘要使用更快的模型（例如 `gpt-4o-mini`）
2. 减少 `trim_tokens_to_summarize`，发送更少上下文
3. 提高触发阈值，降低摘要频率

### Token 上限错误

**问题**：即使启用了摘要，仍然触发 token 上限

**解决方案**：
1. 降低触发阈值，更早开始摘要
2. 减少 `keep` 的值，保留更少消息
3. 检查是否存在特别大的单条消息
4. 考虑使用基于比例的触发器

## 实现细节

### 代码结构

- **配置**：`packages/harness/deerflow/config/summarization_config.py`
- **集成**：`packages/harness/deerflow/agents/lead_agent/agent.py`
- **Middleware**：使用 `langchain.agents.middleware.SummarizationMiddleware`

### Middleware 顺序

摘要会在线程数据和 Sandbox 初始化之后、Title 和 Clarification 之前运行：

1. ThreadDataMiddleware
2. SandboxMiddleware
3. **SummarizationMiddleware** ← 在此运行
4. TitleMiddleware
5. ClarificationMiddleware

### 状态管理

- 摘要是无状态的——配置会在启动时加载一次
- 摘要会作为普通消息添加到对话历史中
- checkpointer 会自动持久化摘要后的历史记录

## 配置示例

### 最简配置
```yaml
summarization:
  enabled: true
  trigger:
    type: tokens
    value: 4000
  keep:
    type: messages
    value: 20
```

### 生产环境配置
```yaml
summarization:
  enabled: true
  model_name: gpt-4o-mini  # Lightweight model for cost efficiency
  trigger:
    - type: tokens
      value: 6000
    - type: messages
      value: 75
  keep:
    type: messages
    value: 25
  trim_tokens_to_summarize: 5000
```

### 多模型配置
```yaml
summarization:
  enabled: true
  model_name: gpt-4o-mini
  trigger:
    type: fraction
    value: 0.7  # 70% of model's max input
  keep:
    type: fraction
    value: 0.3  # Keep 30% of max input
  trim_tokens_to_summarize: 4000
```

### 保守配置（高质量）
```yaml
summarization:
  enabled: true
  model_name: gpt-4  # Use full model for high-quality summaries
  trigger:
    type: tokens
    value: 8000
  keep:
    type: messages
    value: 40  # Keep more context
  trim_tokens_to_summarize: null  # No trimming
```

## 参考资料

- [LangChain Summarization Middleware Documentation](https://docs.langchain.com/oss/python/langchain/middleware/built-in#summarization)
- [LangChain Source Code](https://github.com/langchain-ai/langchain)
