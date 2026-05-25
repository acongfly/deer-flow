---
name: chart-visualization
description: 当用户想要将数据可视化时，应使用此 skill。它会从 26 种可用图表中智能选择最合适的图表类型，根据详细规格提取参数，并通过 JavaScript 脚本生成图表图片。
compatibility:
  nodejs: ">=18.0.0"
---

# 图表可视化 Skill

此 skill 提供将数据转换为可视化图表的完整工作流。它负责图表选择、参数提取和图片生成。

## 工作流

要可视化数据，请按以下步骤操作：

### 1. 智能图表选择
分析用户数据的特征，以确定最合适的图表类型。使用以下准则（并查阅 `references/` 获取详细规格）：

- **时间序列**：使用 `generate_line_chart`（趋势）或 `generate_area_chart`（累计趋势）。对于两个不同量纲，使用 `generate_dual_axes_chart`。
- **比较**：使用 `generate_bar_chart`（类别型）或 `generate_column_chart`。频率分布使用 `generate_histogram_chart`。
- **整体中的部分**：使用 `generate_pie_chart` 或 `generate_treemap_chart`（层级结构）。
- **关系与流向**：使用 `generate_scatter_chart`（相关性）、`generate_sankey_chart`（流向）或 `generate_venn_chart`（重叠）。
- **地图**：使用 `generate_district_map`（区域）、`generate_pin_map`（点位）或 `generate_path_map`（路线）。
- **层级与树结构**：使用 `generate_organization_chart` 或 `generate_mind_map`。
- **专项图表**：
    - `generate_radar_chart`：多维比较。
    - `generate_funnel_chart`：流程阶段。
    - `generate_liquid_chart`：百分比/进度。
    - `generate_word_cloud_chart`：文本频率。
    - `generate_boxplot_chart` 或 `generate_violin_chart`：统计分布。
    - `generate_network_graph`：复杂节点-边关系。
    - `generate_fishbone_diagram`：因果分析。
    - `generate_flow_diagram`：流程图。
    - `generate_spreadsheet`：表格型数据或数据透视表，用于结构化数据展示与交叉分析。

### 2. 参数提取
一旦确定图表类型，就读取 `references/` 目录中的对应文件（例如 `references/generate_line_chart.md`）以识别必填和可选字段。
将用户输入中的数据提取出来，并映射到预期的 `args` 格式。

### 3. 生成图表
使用 JSON payload 调用 `scripts/generate.js` 脚本。

**Payload 格式：**
```json
{
  "tool": "generate_chart_type_name",
  "args": {
    "data": [...],
    "title": "...",
    "theme": "...",
    "style": { ... }
  }
}
```

**执行命令：**
```bash
node ./scripts/generate.js '<payload_json>'
```

### 4. 返回结果
脚本会输出生成的图表图片 URL。
向用户返回以下内容：
- 图片 URL。
- 用于生成的完整 `args`（规格）。

## 参考资料
每种图表类型的详细规格都位于 `references/` 目录中。请查阅这些文件，确保传给脚本的 `args` 符合预期 schema。

## 许可证

此 `SKILL.md` 由 [antvis/chart-visualization-skills](https://github.com/antvis/chart-visualization-skills) 提供。
遵循 [MIT License](https://github.com/antvis/chart-visualization-skills/blob/master/LICENSE) 许可。
