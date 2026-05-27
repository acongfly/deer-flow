---
name: video-generation
description: 当用户请求生成、创建或想象视频时使用此技能。支持结构化提示词和参考图像进行引导式生成。
---

# 视频生成技能

## 概述

此技能使用结构化提示词和 Python 脚本生成高质量视频。工作流程包括创建 JSON 格式的提示词，以及使用可选参考图像执行视频生成。

## 核心能力

- 为 AIGC 视频生成创建结构化 JSON 提示词
- 支持参考图像作为引导或视频的首帧/末帧
- 通过自动化 Python 脚本执行生成视频

## 工作流程

### 第一步：了解需求

当用户请求视频生成时，确认：

- 主题/内容：图像中应该包含什么
- 风格偏好：艺术风格、氛围、色调
- 技术规格：纵横比、构图、光照
- 参考图像：任何用于引导生成的图像
- 不需要检查 `/mnt/user-data` 下的文件夹

### 第二步：创建结构化提示词

在 `/mnt/user-data/workspace/` 中生成结构化 JSON 文件，命名格式：`{描述性名称}.json`

### 第三步：创建参考图像（当 image-generation 技能可用时为可选项）

为视频生成生成参考图像。

- 如果只提供了 1 张图像，将其用作视频的引导帧

### 第三步：执行生成

调用 Python 脚本：
```bash
python /mnt/skills/public/video-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/prompt-file.json \
  --reference-images /path/to/ref1.jpg \
  --output-file /mnt/user-data/outputs/generated-video.mp4 \
  --aspect-ratio 16:9
```

参数：

- `--prompt-file`：JSON 提示词文件的绝对路径（必填）
- `--reference-images`：参考图像的绝对路径（可选）
- `--output-file`：输出图像文件的绝对路径（必填）
- `--aspect-ratio`：生成图像的纵横比（可选，默认：16:9）

[!NOTE]
不要读取 Python 文件，直接使用参数调用即可。

## 视频生成示例

用户请求："生成一个描绘《纳尼亚传奇：狮子、女巫和魔衣橱》开场场景的短视频片段"

第一步：在网上搜索《纳尼亚传奇：狮子、女巫和魔衣橱》的开场场景

第二步：创建包含以下内容的 JSON 提示词文件：

```json
{
  "title": "纳尼亚传奇 - 火车站告别",
  "background": {
    "description": "二战疏散场景，伦敦拥挤的火车站。蒸汽和烟雾弥漫，孩子们被送往乡下逃离闪电战。",
    "era": "1940年代战时英国",
    "location": "伦敦铁路站台"
  },
  "characters": ["Pevensie太太", "Lucy Pevensie"],
  "camera": {
    "type": "近景双人镜头",
    "movement": "静止带轻微手持晃动",
    "angle": "侧面视角，亲密构图",
    "focus": "双方脸部对焦，背景柔焦"
  },
  "dialogue": [
    {
      "character": "Pevensie太太",
      "text": "你要为我勇敢，亲爱的。我会来接你的……我保证。"
    },
    {
      "character": "Lucy Pevensie",
      "text": "我会的，妈妈。我保证。"
    }
  ],
  "audio": [
    {
      "type": "火车汽笛声（发车信号）",
      "volume": 1
    },
    {
      "type": "弦乐情感高涨，随后淡出",
      "volume": 0.5
    },
    {
      "type": "火车站环境音",
      "volume": 0.5
    }
  ]
}
```

第三步：使用 image-generation 技能生成参考图像

加载 image-generation 技能，按照技能说明生成单张参考图像 `narnia-farewell-scene-01.jpg`。

第四步：使用 generate.py 脚本生成视频
```bash
python /mnt/skills/public/video-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/narnia-farewell-scene.json \
  --reference-images /mnt/user-data/outputs/narnia-farewell-scene-01.jpg \
  --output-file /mnt/user-data/outputs/narnia-farewell-scene-01.mp4 \
  --aspect-ratio 16:9
```
> 不要读取 Python 文件，直接使用参数调用即可。

## 输出处理

生成后：

- 视频通常保存在 `/mnt/user-data/outputs/` 中
- 使用 `present_files` 工具与用户分享生成的视频（优先展示）以及生成的图像（如适用）
- 简要描述生成结果
- 如需调整，提供迭代建议

## 注意事项

- 无论用户使用何种语言，提示词始终使用英文
- JSON 格式确保结构化、可解析的提示词
- 参考图像能显著提高生成质量
- 迭代优化是获得最佳结果的正常过程
