"""Template MCP server for integrating business APIs with DeerFlow.

Run:
  python /absolute/path/business_api_mcp_server.py

Then register in extensions_config.json under mcpServers.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urljoin

import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("business-api")
REQUEST_TIMEOUT_SECONDS = 30.0
HEALTH_CHECK_TIMEOUT_SECONDS = 15.0
MAX_BODY_PREVIEW_CHARS = 500
SENSITIVE_FIELD_MARKER = "<redacted>"
SENSITIVE_KEY_PARTS = ("token", "secret", "password", "authorization", "api_key", "apikey")


def _normalize_base_url(base: str) -> str:
    return base if base.endswith("/") else f"{base}/"


def _truncate(text: str) -> str:
    return text[:MAX_BODY_PREVIEW_CHARS]


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(part in lowered for part in SENSITIVE_KEY_PARTS)


def _redact(value: Any, parent_key: str | None = None) -> Any:
    if isinstance(value, dict):
        return {
            key: (SENSITIVE_FIELD_MARKER if _is_sensitive_key(key) else _redact(val, key))
            for key, val in value.items()
        }
    if isinstance(value, list):
        return [_redact(item, parent_key) for item in value]
    if parent_key and _is_sensitive_key(parent_key):
        return SENSITIVE_FIELD_MARKER
    return value


def _base_url() -> str:
    base = os.getenv("BUSINESS_API_BASE_URL", "").strip()
    if not base:
        raise ValueError("BUSINESS_API_BASE_URL is not set.")
    return _normalize_base_url(base)


def _headers() -> dict[str, str]:
    token = os.getenv("BUSINESS_API_TOKEN", "").strip()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    return headers


def _parse_json(data: str) -> Any:
    if not data:
        return {}
    try:
        return json.loads(data)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON payload.") from exc


@mcp.tool()
def get_resource(path: str, query_json: str = "{}") -> str:
    """GET business API resource.

    Args:
      path: Relative API path, e.g. "v1/orders".
      query_json: JSON string for query params, e.g. {"status":"open"}.
    """
    query = _parse_json(query_json)
    if not isinstance(query, dict):
        raise ValueError("query_json must be a JSON object.")
    url = urljoin(_base_url(), path.lstrip("/"))
    with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        try:
            resp = client.get(url, headers=_headers(), params=query)
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPStatusError as exc:
            safe_query = _redact(query)
            raise RuntimeError(
                f"GET failed for {url} with params={json.dumps(safe_query, ensure_ascii=False)}: "
                f"status={exc.response.status_code}, body={_truncate(exc.response.text)}"
            ) from exc
        except httpx.RequestError as exc:
            safe_query = _redact(query)
            raise RuntimeError(
                f"GET request error for {url} with params={json.dumps(safe_query, ensure_ascii=False)}: "
                f"{exc!s}"
            ) from exc


@mcp.tool()
def post_action(path: str, payload_json: str = "{}") -> str:
    """POST business API action.

    Args:
      path: Relative API path, e.g. "v1/projects/create".
      payload_json: JSON object body.
    """
    payload = _parse_json(payload_json)
    if not isinstance(payload, dict):
        raise ValueError("payload_json must be a JSON object.")
    url = urljoin(_base_url(), path.lstrip("/"))
    with httpx.Client(timeout=REQUEST_TIMEOUT_SECONDS) as client:
        try:
            resp = client.post(url, headers=_headers(), json=payload)
            resp.raise_for_status()
            return resp.text
        except httpx.HTTPStatusError as exc:
            safe_payload = _redact(payload)
            raise RuntimeError(
                f"POST failed for {url} with payload={json.dumps(safe_payload, ensure_ascii=False)}: "
                f"status={exc.response.status_code}, body={_truncate(exc.response.text)}"
            ) from exc
        except httpx.RequestError as exc:
            safe_payload = _redact(payload)
            raise RuntimeError(
                f"POST request error for {url} with payload={json.dumps(safe_payload, ensure_ascii=False)}: "
                f"{exc!s}"
            ) from exc


@mcp.tool()
def health_check() -> str:
    """Simple health check for connectivity and auth."""
    with httpx.Client(timeout=HEALTH_CHECK_TIMEOUT_SECONDS) as client:
        resp = client.get(urljoin(_base_url(), "health"), headers=_headers())
        return json.dumps(
            {
                "status_code": resp.status_code,
                "ok": resp.is_success,
                "body": _truncate(resp.text),
            }
        )


if __name__ == "__main__":
    try:
        _base_url()
        mcp.run()
    except ValueError as exc:
        raise SystemExit(
            f"{exc}\n"
            "Please set BUSINESS_API_BASE_URL and optionally BUSINESS_API_TOKEN "
            "before starting this MCP server."
        ) from exc
