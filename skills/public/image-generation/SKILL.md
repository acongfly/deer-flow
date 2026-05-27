---
name: image-generation
description: 当用户请求生成、创建、想象或可视化图像（包括角色、场景、产品或任何视觉内容）时使用此 skill。支持结构化 prompts 和参考图像，以进行引导式生成。
---

# 图像生成 Skill

## 概览

此 skill 使用结构化 prompts 和 Python 脚本生成高质量图像。工作流包括创建 JSON 格式的 prompt，以及在可选参考图像的辅助下执行图像生成。

## 核心能力

- 为 AIGC 图像生成创建结构化 JSON prompts
- 支持多张参考图像用于风格/构图引导
- 通过自动化 Python 脚本执行图像生成
- 处理多种图像生成场景（角色设计、场景、产品等）

## 工作流

### 步骤 1：理解需求

当用户请求图像生成时，识别：

- 主题/内容：图像中应该包含什么
- 风格偏好：艺术风格、情绪、配色
- 技术规格：宽高比、构图、光照
- 参考图像：任何用于引导生成的图像
- 你不需要检查 `/mnt/user-data` 下的文件夹

### 步骤 2：创建结构化 Prompt

在 `/mnt/user-data/workspace/` 中生成一个结构化 JSON 文件，命名模式为：`{descriptive-name}.json`

### 步骤 3：执行生成

调用 Python 脚本：
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/prompt-file.json \
  --reference-images /path/to/ref1.jpg /path/to/ref2.png \
  --output-file /mnt/user-data/outputs/generated-image.jpg
  --aspect-ratio 16:9
```

参数：

- `--prompt-file`：JSON prompt 文件的绝对路径（必需）
- `--reference-images`：参考图像的绝对路径（可选，空格分隔）
- `--output-file`：输出图像文件的绝对路径（必需）
- `--aspect-ratio`：生成图像的宽高比（可选，默认：16:9）

[!NOTE]
不要读取 python 文件，直接带参数调用它即可。

## 角色生成示例

用户请求："Create a Tokyo street style woman character in 1990s"

创建 prompt 文件：`/mnt/user-data/workspace/asian-woman.json`
```json
{
  "characters": [{
    "gender": "female",
    "age": "mid-20s",
    "ethnicity": "Japanese",
    "body_type": "slender, elegant",
    "facial_features": "delicate features, expressive eyes, subtle makeup with emphasis on lips, long dark hair partially wet from rain",
    "clothing": "stylish trench coat, designer handbag, high heels, contemporary Tokyo street fashion",
    "accessories": "minimal jewelry, statement earrings, leather handbag",
    "era": "1990s"
  }],
  "negative_prompt": "blurry face, deformed, low quality, overly sharp digital look, oversaturated colors, artificial lighting, studio setting, posed, selfie angle",
  "style": "Leica M11 street photography aesthetic, film-like rendering, natural color palette with slight warmth, bokeh background blur, analog photography feel",
  "composition": "medium shot, rule of thirds, subject slightly off-center, environmental context of Tokyo street visible, shallow depth of field isolating subject",
  "lighting": "neon lights from signs and storefronts, wet pavement reflections, soft ambient city glow, natural street lighting, rim lighting from background neons",
  "color_palette": "muted naturalistic tones, warm skin tones, cool blue and magenta neon accents, desaturated compared to digital photography, film grain texture"
}
```

执行生成：
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/cyberpunk-hacker.json \
  --output-file /mnt/user-data/outputs/cyberpunk-hacker-01.jpg \
  --aspect-ratio 2:3
```

带参考图像时：
```json
{
  "characters": [{
    "gender": "based on [Image 1]",
    "age": "based on [Image 1]",
    "ethnicity": "human from [Image 1] adapted to Star Wars universe",
    "body_type": "based on [Image 1]",
    "facial_features": "matching [Image 1] with slight weathered look from space travel",
    "clothing": "Star Wars style outfit - worn leather jacket with utility vest, cargo pants with tactical pouches, scuffed boots, belt with holster",
    "accessories": "blaster pistol on hip, comlink device on wrist, goggles pushed up on forehead, satchel with supplies, personal vehicle based on [Image 2]",
    "era": "Star Wars universe, post-Empire era"
  }],
  "prompt": "Character inspired by [Image 1] standing next to a vehicle inspired by [Image 2] on a bustling alien planet street in Star Wars universe aesthetic. Character wearing worn leather jacket with utility vest, cargo pants with tactical pouches, scuffed boots, belt with blaster holster. The vehicle adapted to Star Wars aesthetic with weathered metal panels, repulsor engines, desert dust covering, parked on the street. Exotic alien marketplace street with multi-level architecture, weathered metal structures, hanging market stalls with colorful awnings, alien species walking by as background characters. Twin suns casting warm golden light, atmospheric dust particles in air, moisture vaporators visible in distance. Gritty lived-in Star Wars aesthetic, practical effects look, film grain texture, cinematic composition.",
  "negative_prompt": "clean futuristic look, sterile environment, overly CGI appearance, fantasy medieval elements, Earth architecture, modern city",
  "style": "Star Wars original trilogy aesthetic, lived-in universe, practical effects inspired, cinematic film look, slightly desaturated with warm tones",
  "composition": "medium wide shot, character in foreground with alien street extending into background, environmental storytelling, rule of thirds",
  "lighting": "warm golden hour lighting from twin suns, rim lighting on character, atmospheric haze, practical light sources from market stalls",
  "color_palette": "warm sandy tones, ochre and sienna, dusty blues, weathered metals, muted earth colors with pops of alien market colors",
  "technical": {
    "aspect_ratio": "9:16",
    "quality": "high",
    "detail_level": "highly detailed with film-like texture"
  }
}
```
```bash
python /mnt/skills/public/image-generation/scripts/generate.py \
  --prompt-file /mnt/user-data/workspace/star-wars-scene.json \
  --reference-images /mnt/user-data/uploads/character-ref.jpg /mnt/user-data/uploads/vehicle-ref.jpg \
  --output-file /mnt/user-data/outputs/star-wars-scene-01.jpg \
  --aspect-ratio 16:9
```

## 常见场景

针对不同场景使用不同的 JSON schema。

**角色设计**：
- 身体特征（性别、年龄、族裔、体型）
- 面部特征和表情
- 服装和配饰
- 历史时代或设定
- 姿态与上下文

**场景生成**：
- 环境描述
- 时间、天气
- 情绪与氛围
- 焦点与构图

**产品可视化**：
- 产品细节和材质
- 灯光设置
- 背景与上下文
- 展示角度

## 特定模板

仅在与用户请求匹配时读取以下模板文件。

- [Doraemon Comic](templates/doraemon.md)

## 输出处理

生成后：

- 图像通常保存在 `/mnt/user-data/outputs/`
- 使用 present_files tool 与用户分享生成的图像
- 简要说明生成结果
- 如果需要调整，主动提出继续迭代

## 提示：用参考图像增强生成效果

在视觉准确性很关键的场景中，**先使用 `image_search` tool** 查找参考图像，再进行生成。

**推荐使用 image_search tool 的场景：**
- **角色/肖像生成**：搜索相似姿势、表情或风格，以引导面部特征和身体比例
- **特定物体或产品**：查找真实物体的参考图像，以确保准确呈现
- **建筑或环境场景**：搜索地点参考，以捕捉真实细节
- **时尚与服装**：查找风格参考，确保服装细节和搭配准确

**示例工作流：**
1. 调用 `image_search` tool 查找合适的参考图像：
   ```
   image_search(query="Japanese woman street photography 1990s", size="Large")
   ```
2. 将返回的图像 URL 下载为本地文件
3. 将下载的图像作为生成脚本中的 `--reference-images` 参数使用

这种方法通过为模型提供具体的视觉引导，而不是仅依赖文字描述，可显著提升生成质量。

## 说明

- 无论用户使用什么语言，prompts 一律使用英文
- JSON 格式可确保 prompt 结构化且可解析
- 参考图像能显著提升生成质量
- 为达到最佳结果，迭代式优化是正常过程
- 对于角色生成，除详细角色对象外，还应包含一个汇总后的 prompt 字段
