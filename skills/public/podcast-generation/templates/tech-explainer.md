# Tech Explainer Podcast 模板

当需要将技术文档、API 指南或开发者教程转换为 podcast 时，请使用此模板。

## 输入准备

当用户想把技术内容转换为 podcast 时，帮助他们整理输入：

1. **简化代码示例**：将代码片段替换为自然语言描述
   - 不要展示实际代码，而是描述代码做了什么
   - 聚焦概念而非语法

2. **移除复杂符号**：
   - 数学公式应改为文字解释
   - API endpoints 用功能说明而不是 URL 路径来描述
   - 配置示例应概括为设置说明

3. **补充上下文**：
   - 解释为什么这项技术重要
   - 包含真实世界的使用场景
   - 为复杂概念添加类比

## 转换示例

### 原始技术内容：
```markdown
# Using the API

POST /api/v1/users
{
  "name": "John",
  "email": "john@example.com"
}

Response: 201 Created
```

### 适合 Podcast 的内容：
```markdown
# Creating Users with the API

The user creation feature allows applications to register new users in the system.
When you want to add a new user, you send their name and email address to the server.
If everything goes well, the server confirms the user was created successfully.
This is commonly used in signup flows, admin dashboards, or when importing users from other systems.
```

## 生成命令

```bash
python /mnt/skills/public/podcast-generation/scripts/generate.py \
  --script-file /mnt/user-data/workspace/tech-explainer-script.json \
  --output-file /mnt/user-data/outputs/tech-explainer-podcast.mp3 \
  --transcript-file /mnt/user-data/outputs/tech-explainer-transcript.md
```

## 技术类 Podcast 提示

- 让每期聚焦一个核心概念
- 使用类比解释抽象概念
- 加入实用的 “why this matters” 上下文
- 避免使用未解释的术语
- 让对话对初学者也易于理解
