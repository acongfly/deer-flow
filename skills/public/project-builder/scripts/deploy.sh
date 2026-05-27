#!/usr/bin/env bash

set -euo pipefail

PROJECT_PATH="${1:-.}"

if [[ "$PROJECT_PATH" != /* ]]; then
  if ! PROJECT_PATH="$(cd "$PROJECT_PATH" && pwd)"; then
    echo "Error: failed to resolve project path: $PROJECT_PATH" >&2
    exit 1
  fi
fi

if [[ ! -d "$PROJECT_PATH" ]]; then
  echo "Error: project directory not found: $PROJECT_PATH" >&2
  exit 1
fi

PUBLIC_DEPLOY_SCRIPT="/mnt/skills/public/vercel-deploy-claimable/scripts/deploy.sh"
USER_DEPLOY_SCRIPT="/mnt/skills/user/vercel-deploy/scripts/deploy.sh"

if [[ -x "$PUBLIC_DEPLOY_SCRIPT" ]]; then
  DEPLOY_SCRIPT="$PUBLIC_DEPLOY_SCRIPT"
elif [[ -x "$USER_DEPLOY_SCRIPT" ]]; then
  DEPLOY_SCRIPT="$USER_DEPLOY_SCRIPT"
else
  echo "Error: vercel deploy script not found. Install/enable vercel deploy skill first." >&2
  exit 1
fi

echo "Deploying project from: $PROJECT_PATH" >&2
echo "Using deploy script: $DEPLOY_SCRIPT" >&2

RESULT_JSON="$(bash "$DEPLOY_SCRIPT" "$PROJECT_PATH")"

if [[ -z "$RESULT_JSON" ]]; then
  echo "Error: empty deployment response." >&2
  exit 1
fi

if ! printf '%s' "$RESULT_JSON" | python3 -c 'import json,sys
try:
    data = json.load(sys.stdin)
except json.JSONDecodeError:
    print("invalid json response", file=sys.stderr)
    raise SystemExit(1)
preview = data.get("previewUrl")
if not isinstance(preview, str) or not preview:
    print("missing previewUrl in response", file=sys.stderr)
    raise SystemExit(1)
'; then
  echo "Error: deployment response is not valid JSON with previewUrl." >&2
  exit 1
fi

echo "$RESULT_JSON"
