# Memory 设置评审

在本地评审 Memory 设置的添加/编辑流程时，可使用本文档，以尽可能少的手动步骤完成验证。

## 快速评审

1. 使用你当前已经可用的任一本地开发方式启动 DeerFlow。

   示例：

   ```bash
   make dev
   ```

   或

   ```bash
   make docker-start
   ```

   如果你本地已经运行了 DeerFlow，也可以直接复用现有环境。

2. 加载示例 memory 固件数据。

   ```bash
   python scripts/load_memory_sample.py
   ```

3. 打开 `Settings > Memory`。

   默认本地 URL：
   - 应用：`http://localhost:2026`
   - 仅本地 frontend 的备用地址：`http://localhost:3000`

## 最小手动测试

1. 点击 `Add fact`。
2. 使用以下内容创建一条新事实：
   - 内容：`Reviewer-added memory fact`
   - 分类：`testing`
   - 置信度：`0.88`
3. 确认新事实会立即显示，并且来源标记为 `Manual`。
4. 编辑示例事实 `This sample fact is intended for edit testing.`，将其修改为：
   - 内容：`This sample fact was edited during manual review.`
   - 分类：`testing`
   - 置信度：`0.91`
5. 确认编辑后的事实会立即更新。
6. 刷新页面，确认新添加的事实和已编辑的事实都仍然存在。

## 可选健全性检查

- 搜索 `Reviewer-added`，确认能匹配到新事实。
- 搜索 `workflow`，确认分类文本可被搜索。
- 在 `All`、`Facts` 和 `Summaries` 之间切换。
- 删除可丢弃的示例事实 `Delete fact testing can target this disposable sample entry.`，确认列表立即更新。
- 清空所有 memory，确认页面进入空状态。

## 固件文件

- 示例固件：`backend/docs/memory-settings-sample.json`
- 默认本地运行目标：`backend/.deer-flow/memory.json`

加载脚本会在覆盖现有运行时 memory 文件之前，自动创建一个带时间戳的备份。
