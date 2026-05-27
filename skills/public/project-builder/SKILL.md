---
name: project-builder
description: Build and ship user projects end-to-end from chat with minimal core changes. Trigger when users ask to create a project/app/site/service from requirements, integrate business APIs, push code to Git repositories, and deploy to get a live URL. Also trigger for Chinese intents like "创建项目", "新建应用", "生成代码并部署", "接入业务接口", "自动部署上线".
---

# Project Builder

Create a deployable project from conversation, integrate business APIs via MCP/tools, push code to Git, and deliver a live URL.

## Goal

Use DeerFlow extension points (skills + MCP + config) instead of modifying core runtime.

## Required Runtime Capabilities

- `bash`, `write_file`, `read_file`, `glob`, `grep`
- `web_fetch` (optional, for docs lookup)
- A deployment capability:
  - Preferred: `vercel-deploy-claimable` script
  - Alternative: business CI/CD MCP tool

## Inputs You Must Clarify First

Before generating files, confirm:

1. Project type (frontend/full-stack/API/worker)
2. Language and framework
3. Business API list and auth method
4. Target Git provider/repository URL
5. Deployment target (Vercel or custom platform)
6. Whether production deployment is required now

Do not start implementation until these are confirmed.

## Workflow

### 1) Initialize workspace

Run:

```bash
bash /mnt/skills/public/project-builder/scripts/setup.sh <absolute-project-dir> <project-name>
```

This script creates a safe baseline structure, `.env.example`, `.gitignore`, and `README.md`.

### 2) Integrate business APIs

Preferred path:

- Use MCP server from `business_api_mcp_server.py` template.
- Call MCP tools to retrieve API schema or perform test calls.
- Generate API client/service files in the project.

Fallback path:

- Use an existing custom tool registered in config and keep credentials in environment variables only.

### 3) Generate project code

- Generate files incrementally.
- After each major step, run project checks/build commands.
- Stop and fix failures before moving on.

### 4) Git publish

In the generated project directory:

```bash
git init
git add .
git commit -m "Initial scaffold from DeerFlow project-builder"
git branch -M main
git remote add origin <repo-url>
git push -u origin main
```

If repository already exists, skip `git init` and avoid force push.

### 5) Deployment

For Vercel claimable flow:

```bash
bash /mnt/skills/public/project-builder/scripts/deploy.sh <absolute-project-dir>
```

Always return both:

- Preview URL
- Claim URL (if present)

For non-Vercel targets, call deployment MCP/CI tool and return deployment result URL or release ID.

## Error Handling Rules

- If Git auth fails: stop, report exact failing command, ask for token/SSH setup.
- If deployment fails: show key error lines and recommend rollback/retry path.
- If business API call fails: return status code + endpoint + sanitized response.
- Never continue silently after a failed step.

## Security Rules (Mandatory)

- Never print secrets (tokens, keys, cookies) in chat output.
- Never hardcode credentials in source files.
- Use environment variables and `.env.example` placeholders only.
- Before deployment, request a quick user confirmation with changed file summary.

## Production Readiness Checklist

- Build/test/lint pass for generated project
- API endpoint configuration validated
- Git push completed
- Deployment succeeded
- User receives access URL

