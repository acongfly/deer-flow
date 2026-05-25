---
name: web-design-guidelines
description: 审查 UI 代码是否符合 Web 界面规范。当被要求"审查我的 UI"、"检查无障碍性"、"审计设计"、"审查用户体验"或"对照最佳实践检查我的站点"时使用。
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---

# Web 界面规范

审查文件是否符合 Web 界面规范。

## 工作原理

1. 从下方源 URL 获取最新规范
2. 读取指定文件（或提示用户提供文件/模式）
3. 对照获取的规范中的所有规则进行检查
4. 以简洁的 `文件:行号` 格式输出发现的问题

## 规范来源

每次审查前获取最新规范：

```
https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md
```

使用 WebFetch 获取最新规则。获取的内容包含所有规则和输出格式说明。

## 使用方法

当用户提供文件或模式参数时：
1. 从上方源 URL 获取规范
2. 读取指定文件
3. 应用获取规范中的所有规则
4. 使用规范中指定的格式输出发现的问题

如果未指定文件，询问用户要审查哪些文件。
