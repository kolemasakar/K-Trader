#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


def request_json(base_url: str, path: str, api_key: str | None = None):
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = Request(urljoin(base_url.rstrip("/") + "/", path.lstrip("/")), headers=headers)
    with urlopen(request, timeout=10) as response:
        return response.status, json.loads(response.read().decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Live acceptance for the K-Trader Custom GPT Action endpoint.")
    parser.add_argument("--base-url", required=True, help="Deployed HTTPS origin")
    parser.add_argument("--api-key", default=os.getenv("KTRADER_ACTION_API_KEY"))
    parser.add_argument("--allow-not-ready", action="store_true")
    args = parser.parse_args()

    if not args.base_url.startswith("https://"):
        raise SystemExit("FAIL base URL must use HTTPS")

    try:
        _, health = request_json(args.base_url, "/health")
        if health.get("mode") != "read_only":
            raise SystemExit("FAIL /health mode is not read_only")
        if not args.allow_not_ready and not health.get("data_ready"):
            raise SystemExit("FAIL scanner is not data_ready")
        if health.get("action_auth_enabled") and not args.api_key:
            raise SystemExit("FAIL endpoint requires Action API key")

        if args.api_key and health.get("action_auth_enabled"):
            try:
                request_json(args.base_url, "/v1/scanner/status")
            except HTTPError as exc:
                if exc.code != 401:
                    raise
            else:
                raise SystemExit("FAIL unauthenticated /v1 request was not rejected")

        _, status = request_json(args.base_url, "/v1/scanner/status", args.api_key)
        _, signals = request_json(args.base_url, "/v1/signals?limit=5", args.api_key)
        _, candidates = request_json(args.base_url, "/v1/candidates?limit=5", args.api_key)
        if "data_ready" not in status or "items" not in signals or "items" not in candidates:
            raise SystemExit("FAIL required Action response fields are missing")
        for decision in signals.get("items", ()) + candidates.get("items", ()):
            for field in ("provider_id", "canonical_symbol", "side", "grade", "setup_score", "freshness_status"):
                if field not in decision:
                    raise SystemExit(f"FAIL decision missing field: {field}")
        print("PASS Phase 10 Action live acceptance")
        return 0
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FAIL Action acceptance: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
