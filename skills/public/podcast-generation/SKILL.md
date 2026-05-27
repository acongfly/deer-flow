---
name: podcast-generation
description: 当用户请求从文本内容生成、创建或制作 podcast 时使用此 skill。它会将书面内容转换为双主持人对话式 podcast 音频格式，具有自然对话效果。
---

# Podcast 生成 Skill

## 概览

此 skill 可根据文本内容生成高质量 podcast 音频。工作流包括创建结构化 JSON 脚本（对话式内容），并通过 text-to-speech 合成执行音频生成。

## 核心能力

- 将任意文本内容（文章、报告、文档）转换为 podcast 脚本
- 生成自然的双主持人对话（男主持和女主持）
- 使用 text-to-speech 合成语音音频
- 将多个音频片段混合成最终 podcast MP3 文件
- 支持英文和中文内容

## 工作流

### 步骤 1：理解需求

当用户请求生成 podcast 时，识别：

- 源内容：要转换为 podcast 的文本/文章/报告
- 语言：英文或中文（根据内容决定）
- 输出位置：生成的 podcast 保存到哪里
- 你不需要检查 `/mnt/user-data` 下的文件夹

### 步骤 2：创建结构化脚本 JSON

在 `/mnt/user-data/workspace/` 中生成一个结构化 JSON 脚本文件，命名模式为：`{descriptive-name}-script.json`

JSON 结构：
```json
{
  "locale": "en",
  "lines": [
    {"speaker": "male", "paragraph": "dialogue text"},
    {"speaker": "female", "paragraph": "dialogue text"}
  ]
}
```

### 步骤 3：执行生成

调用 Python 脚本：
```bash
python /mnt/skills/public/podcast-generation/scripts/generate.py \
  --script-file /mnt/user-data/workspace/script-file.json \
  --output-file /mnt/user-data/outputs/generated-podcast.mp3 \
  --transcript-file /mnt/user-data/outputs/generated-podcast-transcript.md
```

参数：

- `--script-file`：JSON 脚本文件的绝对路径（必需）
- `--output-file`：输出 MP3 文件的绝对路径（必需）
- `--transcript-file`：输出 transcript markdown 文件的绝对路径（可选，但推荐）

> [!IMPORTANT]
> - 一次完整调用执行脚本。不要把工作流拆成多个步骤。
> - 脚本会在内部处理所有 TTS API 调用和音频生成。
> - 不要读取 Python 文件，直接带参数调用它即可。
> - 始终包含 `--transcript-file`，以便为用户生成可读 transcript。

## 脚本 JSON 格式

脚本 JSON 文件必须遵循以下结构：

```json
{
  "title": "The History of Artificial Intelligence",
  "locale": "en",
  "lines": [
    {"speaker": "male", "paragraph": "Hello Deer! Welcome back to another episode."},
    {"speaker": "female", "paragraph": "Hey everyone! Today we have an exciting topic to discuss."},
    {"speaker": "male", "paragraph": "That's right! We're going to talk about..."}
  ]
}
```

字段：
- `title`：podcast 单集标题（可选，用作 transcript 标题）
- `locale`：语言代码 —— 英文用 `"en"`，中文用 `"zh"`
- `lines`：对话行数组
  - `speaker`：`"male"` 或 `"female"`
  - `paragraph`：该说话人的对白文本

## 脚本撰写指南

创建脚本 JSON 时，请遵循以下指南：

### 格式要求
- 只有两位主持人：男主持和女主持，自然轮换
- 目标时长：约 10 分钟对话（约 40-60 行）
- 开头必须由男主持打招呼，并包含 "Hello Deer"

### 语气与风格
- 自然、对话式的交流 —— 像两个朋友在聊天
- 使用随意表达和自然过渡
- 避免过于正式的语言或学术语气
- 包含反应、追问和自然插话

### 内容指南
- 主持人之间要频繁来回互动
- 句子保持简短，便于口语表达和理解
- 仅使用纯文本 —— 输出中不要包含 markdown 格式
- 将技术概念转换为易懂语言
- 不要出现数学公式、代码或复杂符号
- 让内容对仅通过音频收听的听众也具有吸引力和可理解性
- 排除日期、作者名或文档结构等元信息

## Podcast 生成示例

用户请求："Generate a podcast about the history of artificial intelligence"

步骤 1：创建脚本文件 `/mnt/user-data/workspace/ai-history-script.json`：
```json
{
  "title": "The History of Artificial Intelligence",
  "locale": "en",
  "lines": [
    {"speaker": "male", "paragraph": "Hello Deer! Welcome back to another fascinating episode. Today we're diving into something that's literally shaping our future - the history of artificial intelligence."},
    {"speaker": "female", "paragraph": "Oh, I love this topic! You know, AI feels so modern, but it actually has roots going back over seventy years."},
    {"speaker": "male", "paragraph": "Exactly! It all started back in the 1950s. The term artificial intelligence was actually coined by John McCarthy in 1956 at a famous conference at Dartmouth."},
    {"speaker": "female", "paragraph": "Wait, so they were already thinking about machines that could think back then? That's incredible!"},
    {"speaker": "male", "paragraph": "Right? The early pioneers were so optimistic. They thought we'd have human-level AI within a generation."},
    {"speaker": "female", "paragraph": "But things didn't quite work out that way, did they?"},
    {"speaker": "male", "paragraph": "No, not at all. The 1970s brought what's called the first AI winter..."}
  ]
}
```

步骤 2：执行生成：
```bash
python /mnt/skills/public/podcast-generation/scripts/generate.py \
  --script-file /mnt/user-data/workspace/ai-history-script.json \
  --output-file /mnt/user-data/outputs/ai-history-podcast.mp3 \
  --transcript-file /mnt/user-data/outputs/ai-history-transcript.md
```

这将生成：
- `ai-history-podcast.mp3`：podcast 音频文件
- `ai-history-transcript.md`：可读的 podcast markdown transcript

## 特定模板

仅在与用户请求匹配时读取以下模板文件。

- [Tech Explainer](templates/tech-explainer.md) - 用于转换技术文档和教程

## 输出格式

生成的 podcast 采用 “Hello Deer” 格式：
- 两位主持人：一位男主持，一位女主持
- 自然的对话式交流
- 以 “Hello Deer” 问候开场
- 目标时长：约 10 分钟
- 说话人交替出现，保持流畅与吸引力

## 输出处理

生成后：

- podcasts 和 transcripts 保存在 `/mnt/user-data/outputs/`
- 使用 `present_files` tool 与用户分享 podcast MP3 和 transcript MD
- 简要说明生成结果（主题、时长、主持人）
- 如果需要调整，主动提出重新生成

## 要求

必须设置以下环境变量：
- `VOLCENGINE_TTS_APPID`：Volcengine TTS application ID
- `VOLCENGINE_TTS_ACCESS_TOKEN`：Volcengine TTS access token
- `VOLCENGINE_TTS_CLUSTER`：Volcengine TTS cluster（可选，默认值为 `"volcano_tts"`）

## 说明

- **始终一次调用执行完整流水线** —— 无需测试单个步骤，也不用担心超时
- 脚本 JSON 应与内容语言一致（en 或 zh）
- 技术内容在脚本中应简化，以适应音频收听
- 复杂符号（公式、代码）应在脚本中转写为自然语言
- 较长内容可能会生成更长的 podcast
