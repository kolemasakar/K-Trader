from __future__ import annotations

import re
from urllib.parse import urlsplit


PLACEHOLDER_SERVER = "https://api.k-trader.invalid"
REQUIRED_OPERATION_IDS = frozenset(
    {
        "getHealth",
        "getScannerStatus",
        "listUniverse",
        "getMarketSnapshot",
        "getCandles",
        "getAnalysis",
        "listCandidates",
        "listSignals",
    }
)
_WRITE_METHOD_RE = re.compile(r"(?mi)^\s+(post|put|patch|delete|trace|connect):\s*$")
_OPERATION_ID_RE = re.compile(r"(?m)^\s+operationId:\s*([A-Za-z0-9_.-]+)\s*$")
_SERVER_RE = re.compile(r"(?m)^\s*-\s+url:\s*(https://\S+)\s*$")


def validate_server_url(server_url: str) -> str:
    value = server_url.strip().rstrip("/")
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Action server URL must use HTTPS and include a hostname")
    if parsed.username or parsed.password:
        raise ValueError("Action server URL must not contain credentials")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("Action server URL must be an origin without path/query/fragment")
    return value


def validate_action_schema_text(text: str, *, allow_placeholder: bool = True) -> tuple[str, ...]:
    if _WRITE_METHOD_RE.search(text):
        raise ValueError("Custom GPT Action schema must remain read-only")
    operation_ids = tuple(_OPERATION_ID_RE.findall(text))
    if len(operation_ids) != len(set(operation_ids)):
        raise ValueError("Custom GPT Action operationId values must be unique")
    missing = REQUIRED_OPERATION_IDS - set(operation_ids)
    if missing:
        raise ValueError(f"Custom GPT Action schema missing operations: {sorted(missing)}")
    servers = _SERVER_RE.findall(text)
    if len(servers) != 1:
        raise ValueError("Custom GPT Action schema must define exactly one HTTPS server")
    server = servers[0]
    if server == PLACEHOLDER_SERVER:
        if not allow_placeholder:
            raise ValueError("Custom GPT Action server placeholder has not been replaced")
    else:
        validate_server_url(server)
    if "type: http" not in text or "scheme: bearer" not in text:
        raise ValueError("Custom GPT Action schema must declare Bearer authentication")
    return operation_ids


def render_action_schema(text: str, server_url: str) -> str:
    server = validate_server_url(server_url)
    validate_action_schema_text(text, allow_placeholder=True)
    servers = _SERVER_RE.findall(text)
    current_server = servers[0]
    rendered = text.replace(current_server, server, 1)
    validate_action_schema_text(rendered, allow_placeholder=False)
    return rendered
