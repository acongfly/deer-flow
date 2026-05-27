---
name: data-analysis
description: 当用户上传 Excel（.xlsx/.xls）或 CSV 文件并希望进行数据分析、生成统计结果、创建摘要、透视表、SQL 查询，或任何形式的结构化数据探索时使用此 skill。支持多工作表 Excel 工作簿、聚合、筛选、连接以及将结果导出为 CSV/JSON/Markdown。
---

# 数据分析 Skill

## 概述

此 skill 使用 DuckDB（一个进程内分析型 SQL 引擎）分析用户上传的 Excel/CSV 文件。它通过一个 Python 脚本统一支持 schema 检查、基于 SQL 的查询、统计摘要与结果导出。

## 核心能力

- 检查 Excel/CSV 文件结构（工作表、列、类型、行数）
- 对上传数据执行任意 SQL 查询
- 生成统计摘要（均值、中位数、stddev、百分位数、空值）
- 支持多工作表 Excel 工作簿（每个工作表都会成为一张表）
- 将查询结果导出为 CSV、JSON 或 Markdown
- 借助 DuckDB 的列式引擎高效处理大文件

## 工作流

### 步骤 1：理解需求

当用户上传数据文件并请求分析时，识别：

- **文件位置**：上传到 `/mnt/user-data/uploads/` 下的 Excel/CSV 文件路径
- **分析目标**：用户想获得什么洞察（摘要、筛选、聚合、比较等）
- **输出格式**：结果应如何展示（表格、CSV 导出、JSON 等）
- 你不需要检查 `/mnt/user-data` 下的文件夹

### 步骤 2：检查文件结构

先检查上传文件以理解其 schema：

```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action inspect
```

这将返回：
- 工作表名称（Excel）或文件名（CSV）
- 列名、数据类型与非空计数
- 每个工作表/文件的行数
- 示例数据（前 5 行）

### 步骤 3：执行分析

根据 schema，构造 SQL 查询来回答用户的问题。

#### 运行 SQL 查询

```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action query \
  --sql "SELECT category, COUNT(*) as count, AVG(amount) as avg_amount FROM Sheet1 GROUP BY category ORDER BY count DESC"
```

#### 生成统计摘要

```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action summary \
  --table Sheet1
```

对于每个数值列，这会返回：count、mean、std、min、25%、50%、75%、max、null_count。
对于字符串列，这会返回：count、unique、top value、frequency、null_count。

#### 导出结果

```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/data.xlsx \
  --action query \
  --sql "SELECT * FROM Sheet1 WHERE amount > 1000" \
  --output-file /mnt/user-data/outputs/filtered-results.csv
```

支持的输出格式（根据扩展名自动识别）：
- `.csv` —— 逗号分隔值
- `.json` —— JSON 记录数组
- `.md` —— Markdown 表格

### 参数

| 参数 | 必填 | 说明 |
|-----------|----------|-------------|
| `--files` | 是 | 以空格分隔的 Excel/CSV 文件路径 |
| `--action` | 是 | 以下之一：`inspect`、`query`、`summary` |
| `--sql` | 对 `query` 必填 | 要执行的 SQL 查询 |
| `--table` | 对 `summary` 必填 | 要汇总的表/工作表名称 |
| `--output-file` | 否 | 导出结果的路径（CSV/JSON/MD） |

> [!NOTE]
> 不要读取这个 Python 文件，只需按参数调用它。

## 表命名规则

- **Excel 文件**：每个工作表都会成为以工作表名命名的表（例如 `Sheet1`、`Sales`、`Revenue`）
- **CSV 文件**：表名为去掉扩展名后的文件名（例如 `data.csv` → `data`）
- **多个文件**：所有文件中的所有表都可在同一查询上下文中使用，因此可以跨文件 join
- **特殊字符**：带空格或特殊字符的工作表/文件名会被自动清洗（空格 → 下划线）。对于以数字开头或包含特殊字符的名称，请使用双引号，例如 `"2024_Sales"`

## 分析模式

### 基础探索
```sql
-- Row count
SELECT COUNT(*) FROM Sheet1

-- Distinct values in a column
SELECT DISTINCT category FROM Sheet1

-- Value distribution
SELECT category, COUNT(*) as cnt FROM Sheet1 GROUP BY category ORDER BY cnt DESC

-- Date range
SELECT MIN(date_col), MAX(date_col) FROM Sheet1
```

### 聚合与分组
```sql
-- Revenue by category and month
SELECT category, DATE_TRUNC('month', order_date) as month,
       SUM(revenue) as total_revenue
FROM Sales
GROUP BY category, month
ORDER BY month, total_revenue DESC

-- Top 10 customers by spend
SELECT customer_name, SUM(amount) as total_spend
FROM Orders GROUP BY customer_name
ORDER BY total_spend DESC LIMIT 10
```

### 跨文件 Join
```sql
-- Join sales with customer info from different files
SELECT s.order_id, s.amount, c.customer_name, c.region
FROM sales s
JOIN customers c ON s.customer_id = c.id
WHERE s.amount > 500
```

### 窗口函数
```sql
-- Running total and rank
SELECT order_date, amount,
       SUM(amount) OVER (ORDER BY order_date) as running_total,
       RANK() OVER (ORDER BY amount DESC) as amount_rank
FROM Sales
```

### 类透视分析
```sql
-- Pivot: monthly revenue by category
SELECT category,
       SUM(CASE WHEN MONTH(date) = 1 THEN revenue END) as Jan,
       SUM(CASE WHEN MONTH(date) = 2 THEN revenue END) as Feb,
       SUM(CASE WHEN MONTH(date) = 3 THEN revenue END) as Mar
FROM Sales
GROUP BY category
```

## 完整示例

用户上传 `sales_2024.xlsx`（包含工作表：`Orders`、`Products`、`Customers`），并请求：“分析我的销售数据——展示收入最高的产品和月度趋势。”

### 步骤 1：检查文件

```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/sales_2024.xlsx \
  --action inspect
```

### 步骤 2：按收入排序的热门产品

```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/sales_2024.xlsx \
  --action query \
  --sql "SELECT p.product_name, SUM(o.quantity * o.unit_price) as total_revenue, SUM(o.quantity) as total_units FROM Orders o JOIN Products p ON o.product_id = p.id GROUP BY p.product_name ORDER BY total_revenue DESC LIMIT 10"
```

### 步骤 3：月度收入趋势

```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/sales_2024.xlsx \
  --action query \
  --sql "SELECT DATE_TRUNC('month', order_date) as month, SUM(quantity * unit_price) as revenue FROM Orders GROUP BY month ORDER BY month" \
  --output-file /mnt/user-data/outputs/monthly-trends.csv
```

### 步骤 4：统计摘要

```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/sales_2024.xlsx \
  --action summary \
  --table Orders
```

向用户展示结果时，要清晰解释发现、趋势和可执行洞察。

## 多文件示例

用户上传 `orders.csv` 和 `customers.xlsx`，并问：“哪个地区的平均订单价值最高？”

```bash
python /mnt/skills/public/data-analysis/scripts/analyze.py \
  --files /mnt/user-data/uploads/orders.csv /mnt/user-data/uploads/customers.xlsx \
  --action query \
  --sql "SELECT c.region, AVG(o.amount) as avg_order_value, COUNT(*) as order_count FROM orders o JOIN Customers c ON o.customer_id = c.id GROUP BY c.region ORDER BY avg_order_value DESC"
```

## 输出处理

分析完成后：

- 直接在对话中以格式化表格展示查询结果
- 对于大结果，导出到文件并通过 `present_files` tool 分享
- 始终用易懂语言解释发现并提炼关键结论
- 当模式有趣时，建议后续分析方向
- 如果用户希望保留结果，主动提出导出

## 缓存

该脚本会自动缓存已加载数据，避免每次调用时都重新解析文件：

- 首次加载时，文件会被解析并存储到 `/mnt/user-data/workspace/.data-analysis-cache/` 下的持久 DuckDB 数据库中
- 缓存键为所有输入文件内容的 SHA256 哈希——如果文件变化，就会创建新的缓存
- 后续使用同一批文件的调用将直接复用缓存数据库（几乎瞬时启动）
- 缓存是透明的——无需额外参数

当针对同一批数据文件执行多次查询（inspect → query → summary）时，这尤其有用。

## 说明

- DuckDB 支持完整 SQL，包括窗口函数、CTE、子查询和高级聚合
- Excel 日期列会被自动解析；请使用 DuckDB 日期函数（`DATE_TRUNC`、`EXTRACT` 等）
- 对于超大文件（100MB+），DuckDB 可高效处理而无需全部载入内存
- 带空格的列名可通过双引号访问：`"Column Name"`
