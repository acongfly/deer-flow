# DeerFlow 冒烟测试报告

**测试日期**：{{test_date}}
**测试环境**：{{test_environment}}
**部署模式**：本地
**测试版本**：{{git_commit}}

---

## 执行摘要

| 指标 | 状态 |
|------|------|
| 总测试阶段 | 6 |
| 通过阶段 | {{passed_stages}} |
| 失败阶段 | {{failed_stages}} |
| 总体结论 | **{{overall_status}}** |

### 关键测试用例

| 用例 | 结果 | 详情 |
|------|------|------|
| 代码更新检查 | {{case_code_update}} | {{case_code_update_details}} |
| 环境检查 | {{case_env_check}} | {{case_env_check_details}} |
| 配置准备 | {{case_config_prep}} | {{case_config_prep_details}} |
| 部署 | {{case_deploy}} | {{case_deploy_details}} |
| 健康检查 | {{case_health_check}} | {{case_health_check_details}} |
| 前端路由 | {{case_frontend_routes_overall}} | {{case_frontend_routes_details}} |

---

## 详细测试结果

### 第一阶段：代码更新检查

- [x] 确认当前目录 - {{status_dir_check}}
- [x] 检查 Git 状态 - {{status_git_status}}
- [x] 拉取最新代码 - {{status_git_pull}}
- [x] 确认代码更新 - {{status_git_verify}}

**阶段状态**：{{stage1_status}}

---

### 第二阶段：本地环境检查

- [x] Node.js 版本 - {{status_node_version}}
- [x] pnpm - {{status_pnpm}}
- [x] uv - {{status_uv}}
- [x] nginx - {{status_nginx}}
- [x] 端口检查 - {{status_port_check}}

**阶段状态**：{{stage2_status}}

---

### 第三阶段：配置准备

- [x] config.yaml - {{status_config_yaml}}
- [x] .env 文件 - {{status_env_file}}
- [x] 模型配置 - {{status_model_config}}

**阶段状态**：{{stage3_status}}

---

### 第四阶段：本地部署

- [x] make check - {{status_make_check}}
- [x] make install - {{status_make_install}}
- [x] make dev-daemon / make dev - {{status_local_start}}
- [x] 服务启动等待 - {{status_wait_startup}}

**阶段状态**：{{stage4_status}}

---

### 第五阶段：服务健康检查

- [x] 进程状态 - {{status_processes}}
- [x] 前端服务 - {{status_frontend}}
- [x] API Gateway - {{status_api_gateway}}
- [x] LangGraph 服务 - {{status_langgraph}}

**阶段状态**：{{stage5_status}}

---

### 前端路由冒烟结果

| 路由 | 状态 | 详情 |
|------|------|------|
| 首页 `/` | {{landing_status}} | {{landing_details}} |
| Workspace 重定向 `/workspace` | {{workspace_redirect_status}} | 目标 {{workspace_redirect_target}} |
| 新对话 `/workspace/chats/new` | {{new_chat_status}} | {{new_chat_details}} |
| 对话列表 `/workspace/chats` | {{chats_list_status}} | {{chats_list_details}} |
| Agent 库 `/workspace/agents` | {{agents_gallery_status}} | {{agents_gallery_details}} |
| 文档 `{{docs_path}}` | {{docs_status}} | {{docs_details}} |

**摘要**：{{frontend_routes_summary}}

---

### 第六阶段：测试报告生成

- [x] 结果摘要 - {{status_summary}}
- [x] 问题日志 - {{status_issues}}
- [x] 报告生成 - {{status_report}}

**阶段状态**：{{stage6_status}}

---

## 问题日志

### 问题 1
**描述**：{{issue1_description}}
**严重性**：{{issue1_severity}}
**解决方案**：{{issue1_solution}}

---

## 环境信息

### 本地依赖版本
```text
Node.js: {{node_version_output}}
pnpm: {{pnpm_version_output}}
uv: {{uv_version_output}}
nginx: {{nginx_version_output}}
```

### Git 信息
```text
仓库：{{git_repo}}
分支：{{git_branch}}
提交：{{git_commit}}
提交信息：{{git_commit_message}}
```

### 配置摘要
- config.yaml 存在：{{config_exists}}
- .env 文件存在：{{env_exists}}
- 已配置模型数量：{{model_count}}

---

## 本地服务状态

| 服务 | 状态 | 端点 |
|------|------|------|
| Nginx | {{nginx_status}} | {{nginx_endpoint}} |
| Frontend | {{frontend_status}} | {{frontend_endpoint}} |
| Gateway | {{gateway_status}} | {{gateway_endpoint}} |
| LangGraph | {{langgraph_status}} | {{langgraph_endpoint}} |

---

## 建议和后续步骤

### 如果测试通过
1. [ ] 访问 http://localhost:2026 开始使用 DeerFlow
2. [ ] 如果尚未配置，配置你偏好的模型
3. [ ] 探索可用技能
4. [ ] 参阅文档了解更多功能

### 如果测试失败
1. [ ] 查阅 references/troubleshooting.md 寻找常见解决方案
2. [ ] 检查本地日志：`logs/{langgraph,gateway,frontend,nginx}.log`
3. [ ] 验证配置文件格式和内容
4. [ ] 如需要，完全重置环境：`make stop && make clean && make install && make dev-daemon`

---

## 附录

### 完整日志
{{full_logs}}

### 测试人员
{{tester_name}}

---

*报告生成时间：{{report_time}}*
