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


def _base_url() -> str:
    base = os.getenv("BUSINESS_API_BASE_URL", "").strip()
    if not base:
        raise ValueError("BUSINESS_API_BASE_URL is not set.")
    return base if base.endswith("/") else f"{base}/"


def _headers() -> dict[str, str]:
    token = os.getenv("BUSINESS_API_TOKEN", "").strip()
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    return headers


def _parse_json(data: str) -> Any:
    if not data:
        return {}
    return json.loads(data)


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
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_headers(), params=query)
        resp.raise_for_status()
        return resp.text


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
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, headers=_headers(), json=payload)
        resp.raise_for_status()
        return resp.text


@mcp.tool()
def health_check() -> str:
    """Simple health check for connectivity and auth."""
    with httpx.Client(timeout=15.0) as client:
        resp = client.get(urljoin(_base_url(), "health"), headers=_headers())
        return json.dumps(
            {
                "status_code": resp.status_code,
                "ok": resp.is_success,
                "body": resp.text[:500],
            }
        )


if __name__ == "__main__":
    mcp.run()
