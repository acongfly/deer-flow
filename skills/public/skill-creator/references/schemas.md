# JSON 结构规范

本文档定义了 skill-creator 使用的 JSON 结构。

---

## evals.json

定义技能的评估用例。位于技能目录中的 `evals/evals.json`。

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "用户的示例提示词",
      "expected_output": "预期结果描述",
      "files": ["evals/files/sample1.pdf"],
      "expectations": [
        "输出包含 X",
        "技能使用了脚本 Y"
      ]
    }
  ]
}
```

**字段说明：**
- `skill_name`：与技能 frontmatter 匹配的名称
- `evals[].id`：唯一整数标识符
- `evals[].prompt`：要执行的任务
- `evals[].expected_output`：成功的人类可读描述
- `evals[].files`：可选的输入文件路径列表（相对于技能根目录）
- `evals[].expectations`：可验证的陈述列表

---

## history.json

跟踪改进模式中的版本进展。位于 workspace 根目录。

```json
{
  "started_at": "2026-01-15T10:30:00Z",
  "skill_name": "pdf",
  "current_best": "v2",
  "iterations": [
    {
      "version": "v0",
      "parent": null,
      "expectation_pass_rate": 0.65,
      "grading_result": "baseline",
      "is_current_best": false
    },
    {
      "version": "v1",
      "parent": "v0",
      "expectation_pass_rate": 0.75,
      "grading_result": "won",
      "is_current_best": false
    },
    {
      "version": "v2",
      "parent": "v1",
      "expectation_pass_rate": 0.85,
      "grading_result": "won",
      "is_current_best": true
    }
  ]
}
```

**字段说明：**
- `started_at`：改进开始时的 ISO 时间戳
- `skill_name`：被改进的技能名称
- `current_best`：最佳版本标识符
- `iterations[].version`：版本标识符（v0, v1, ...）
- `iterations[].parent`：派生自的父版本
- `iterations[].expectation_pass_rate`：评分通过率
- `iterations[].grading_result`："baseline"、"won"、"lost" 或 "tie"
- `iterations[].is_current_best`：是否为当前最佳版本

---

## grading.json

评分代理的输出。位于 `<run-dir>/grading.json`。

```json
{
  "expectations": [
    {
      "text": "输出包含姓名 'John Smith'",
      "passed": true,
      "evidence": "在步骤 3 的转录中找到：'提取的姓名：John Smith, Sarah Johnson'"
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": { "Read": 5, "Write": 2, "Bash": 8 },
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  }
}
```

**字段说明：**
- `expectations[]`：带证据的已评分期望
- `summary`：汇总通过/失败计数
- `execution_metrics`：工具使用和输出大小（来自 executor 的 metrics.json）
- `timing`：挂钟计时（来自 timing.json）

---

## metrics.json

执行器代理的输出。位于 `<run-dir>/outputs/metrics.json`。

```json
{
  "tool_calls": {
    "Read": 5, "Write": 2, "Bash": 8, "Edit": 1, "Glob": 2, "Grep": 0
  },
  "total_tool_calls": 18,
  "total_steps": 6,
  "files_created": ["filled_form.pdf", "field_values.json"],
  "errors_encountered": 0,
  "output_chars": 12450,
  "transcript_chars": 3200
}
```

---

## timing.json

运行的挂钟计时。位于 `<run-dir>/timing.json`。

**如何捕获：** 当子代理任务完成时，任务通知包含 `total_tokens` 和 `duration_ms`。立即保存——它们不会持久化到其他地方，事后无法恢复。

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z",
  "executor_duration_seconds": 165.0,
  "grader_start": "2026-01-15T10:32:46Z",
  "grader_end": "2026-01-15T10:33:12Z",
  "grader_duration_seconds": 26.0
}
```

---

## benchmark.json

基准测试模式的输出。位于 `benchmarks/<timestamp>/benchmark.json`。

```json
{
  "metadata": {
    "skill_name": "pdf",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "runs": [
    {
      "eval_id": 1,
      "eval_name": "Ocean",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      }
    }
  ],
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0},
      "tokens": {"mean": 3800, "stddev": 400}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08},
      "time_seconds": {"mean": 32.0, "stddev": 8.0},
      "tokens": {"mean": 2100, "stddev": 300}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },
  "notes": [
    "断言 '输出是 PDF 文件' 在两种配置中都 100% 通过——可能无法区分技能价值",
    "评估 3 显示高方差（50% ± 40%）——可能不稳定或依赖模型"
  ]
}
```

**重要：** 查看器精确读取这些字段名称。使用 `config` 而不是 `configuration`，或将 `pass_rate` 放在运行的顶层而不是嵌套在 `result` 下，将导致查看器显示空/零值。

---

## comparison.json

盲比较器的输出。位于 `<grading-dir>/comparison-N.json`。

```json
{
  "winner": "A",
  "reasoning": "输出 A 提供了完整的解决方案，格式正确且包含所有必需字段。",
  "rubric": {
    "A": {
      "content": {"correctness": 5, "completeness": 5},
      "overall_score": 9.0
    },
    "B": {
      "content": {"correctness": 3, "completeness": 2},
      "overall_score": 5.4
    }
  }
}
```

---

## analysis.json

事后分析器的输出。位于 `<grading-dir>/analysis.json`。

```json
{
  "comparison_summary": {
    "winner": "A",
    "winner_skill": "path/to/winner/skill",
    "loser_skill": "path/to/loser/skill"
  },
  "winner_strengths": ["清晰的多页文档处理步骤说明"],
  "loser_weaknesses": ["模糊的说明导致行为不一致"],
  "improvement_suggestions": [
    {
      "priority": "high",
      "category": "instructions",
      "suggestion": "将'适当处理文档'替换为明确的步骤",
      "expected_impact": "消除导致不一致行为的歧义"
    }
  ]
}
```
