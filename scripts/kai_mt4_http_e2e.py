from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from ktrader.providers.base import ProviderError
from ktrader.providers.kai_mt4 import KAIMT4MarketContextAdapter

DEFAULT_BASE_URL = "http://127.0.0.1:18765"
DEFAULT_TIMEOUT_SECONDS = 70.0
TOKEN_ENV = "KAI_MARKET_CONTEXT_DELIVERY_TOKEN"


def _request_payload(*, base_url: str, symbol: str, market: str, timeout: float) -> dict[str, Any]:
    token = os.getenv(TOKEN_ENV)
    if not token:
        raise RuntimeError(f"{TOKEN_ENV} is not configured")

    body = json.dumps({"symbol": symbol, "market": market}, separators=(",", ":")).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/market-context/acquire",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "K-Trader/0.1 kai-mt4-e2e",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        detail = raw[:500].decode("utf-8", errors="replace")
        raise RuntimeError(f"K_AI delivery HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"K_AI delivery transport failed: {exc}") from exc

    if status != 200:
        raise RuntimeError(f"K_AI delivery returned unexpected HTTP status {status}")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("K_AI delivery returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("K_AI delivery payload must be a JSON object")
    return payload


def _negative_contract_smoke(payload: dict[str, Any]) -> list[dict[str, str]]:
    cases: list[tuple[str, dict[str, Any], str]] = []

    legacy = copy.deepcopy(payload)
    legacy["schema_version"] = "1.0"
    legacy["scopes"].pop("M15", None)
    legacy.pop("timestamp_semantics", None)
    legacy.pop("utc_offset_minutes", None)
    cases.append(("schema_1_0_require_m15", legacy, "M15 requires"))

    wrong_depth = copy.deepcopy(payload)
    wrong_depth["scopes"]["M15"]["bar_depth"] = 299
    wrong_depth["scopes"]["M15"]["bars"] = wrong_depth["scopes"]["M15"]["bars"][-299:]
    cases.append(("m15_depth_mismatch", wrong_depth, "bar_depth mismatch"))

    wrong_semantics = copy.deepcopy(payload)
    wrong_semantics["timestamp_semantics"] = "UTC"
    cases.append(("timestamp_semantics", wrong_semantics, "timestamp_semantics"))

    wrong_offset = copy.deepcopy(payload)
    wrong_offset["utc_offset_minutes"] = 0
    cases.append(("utc_offset_minutes", wrong_offset, "utc_offset_minutes"))

    duplicate = copy.deepcopy(payload)
    duplicate["scopes"]["M15"]["bars"][-1]["time"] = duplicate["scopes"]["M15"]["bars"][-2]["time"]
    duplicate["scopes"]["M15"]["latest_closed_bar_time"] = duplicate["scopes"]["M15"]["bars"][-1]["time"]
    cases.append(("duplicate_m15_timestamp", duplicate, "strictly chronological"))

    current_not_after = copy.deepcopy(payload)
    current_not_after["scopes"]["M15"]["current_bar_time"] = current_not_after["scopes"]["M15"]["latest_closed_bar_time"]
    cases.append(("current_not_after_closed", current_not_after, "current_bar_time must be after"))

    results: list[dict[str, str]] = []
    for name, candidate, expected in cases:
        try:
            KAIMT4MarketContextAdapter.validate_market_context(
                candidate,
                expected_symbol=str(payload["symbol"]),
                expected_market=str(payload["market"]),
                expected_bar_depths=KAIMT4MarketContextAdapter.canonical_bar_depths,
                require_m15=True,
            )
        except ProviderError as exc:
            if expected not in str(exc):
                raise RuntimeError(f"negative case {name} failed with unexpected error: {exc}") from exc
            results.append({"case": name, "status": "PASS"})
        else:
            raise RuntimeError(f"negative case {name} did not fail closed")
    return results


def _summary(payload: dict[str, Any]) -> dict[str, Any]:
    scopes = payload["scopes"]
    return {
        "schema_version": "ktrader.kai_mt4_http_e2e.v1",
        "status": "PASS",
        "run_id": payload.get("run_id"),
        "producer_schema_version": payload.get("schema_version"),
        "symbol": payload.get("symbol"),
        "market": payload.get("market"),
        "source_name": payload.get("source_name"),
        "time_source": payload.get("time_source"),
        "timestamp_semantics": payload.get("timestamp_semantics"),
        "utc_offset_minutes": payload.get("utc_offset_minutes"),
        "closed_bars_only": payload.get("closed_bars_only"),
        "scopes": sorted(scopes),
        "bar_depths": {name: scopes[name].get("bar_depth") for name in sorted(scopes)},
        "m15_latest_closed_bar_time": scopes["M15"].get("latest_closed_bar_time"),
        "m15_current_bar_time": scopes["M15"].get("current_bar_time"),
        "transport": "bounded_loopback_http_over_restricted_reverse_ssh",
        "base_url": DEFAULT_BASE_URL,
        "credential_source": TOKEN_ENV,
        "credential_logged": False,
        "provider_registered": False,
        "production_activation": False,
        "trading_authorized": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded read-only K_AI -> K-Trader live HTTP E2E acceptance")
    parser.add_argument("--symbol", default="ETHUSDt")
    parser.add_argument("--market", default="crypto")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--output")
    parser.add_argument("--save-payload")
    parser.add_argument("--negative-contract-smoke", action="store_true")
    args = parser.parse_args()

    try:
        payload = _request_payload(
            base_url=args.base_url,
            symbol=args.symbol,
            market=args.market,
            timeout=args.timeout,
        )
        adapter = KAIMT4MarketContextAdapter()
        adapter.accept_market_context(
            payload,
            symbol=args.symbol,
            market=args.market,
            require_m15=True,
        )
        result = _summary(payload)
        if args.negative_contract_smoke:
            result["negative_contract_smoke"] = _negative_contract_smoke(payload)
        if args.save_payload:
            payload_path = Path(args.save_payload)
            payload_path.parent.mkdir(parents=True, exist_ok=True)
            payload_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    except Exception as exc:
        result = {
            "schema_version": "ktrader.kai_mt4_http_e2e.v1",
            "status": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "credential_logged": False,
            "provider_registered": False,
            "production_activation": False,
            "trading_authorized": False,
        }

    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
