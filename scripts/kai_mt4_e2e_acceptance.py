from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from ktrader.providers.base import ProviderError
from ktrader.providers.kai_mt4 import KAIMT4MarketContextAdapter


def _summary(payload: dict[str, Any]) -> dict[str, Any]:
    scopes = payload["scopes"]
    return {
        "schema_version": "ktrader.kai_mt4_e2e_acceptance.v1",
        "status": "PASS",
        "producer_schema_version": payload.get("schema_version"),
        "run_id": payload.get("run_id"),
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
        "provider_registered": False,
        "production_activation": False,
        "trading_authorized": False,
    }


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

    current_not_after = copy.deepcopy(payload)
    current_not_after["scopes"]["M15"]["current_bar_time"] = current_not_after["scopes"]["M15"]["latest_closed_bar_time"]
    cases.append(("current_not_after_closed", current_not_after, "current_bar_time must be after"))

    results: list[dict[str, str]] = []
    for name, candidate, expected_message in cases:
        try:
            KAIMT4MarketContextAdapter.validate_market_context(
                candidate,
                expected_symbol=str(payload["symbol"]),
                expected_market=str(payload["market"]),
                expected_bar_depths=KAIMT4MarketContextAdapter.canonical_bar_depths,
                require_m15=True,
            )
        except ProviderError as exc:
            if expected_message not in str(exc):
                raise RuntimeError(f"negative case {name} failed with unexpected error: {exc}") from exc
            results.append({"case": name, "status": "PASS"})
        else:
            raise RuntimeError(f"negative case {name} did not fail closed")
    return results


def _load_payload(path: str | None) -> dict[str, Any]:
    if path:
        raw = Path(path).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    if not raw.strip():
        raise ValueError("no MARKET_CONTEXT payload supplied; use --input or stdin")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("MARKET_CONTEXT payload must be a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a freshly delivered K_AI MARKET_CONTEXT payload on the K-Trader side. "
            "Cross-system delivery is intentionally transport-neutral."
        )
    )
    parser.add_argument("--input", help="path to a freshly delivered MARKET_CONTEXT JSON; stdin if omitted")
    parser.add_argument("--symbol", default="ETHUSDt")
    parser.add_argument("--market", default="crypto")
    parser.add_argument("--negative-contract-smoke", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()

    try:
        payload = _load_payload(args.input)
        adapter = KAIMT4MarketContextAdapter()
        accepted = adapter.accept_market_context(
            payload,
            symbol=args.symbol,
            market=args.market,
            require_m15=True,
        )
        result = _summary(accepted)
        if args.negative_contract_smoke:
            result["negative_contract_smoke"] = _negative_contract_smoke(accepted)
    except Exception as exc:
        result = {
            "schema_version": "ktrader.kai_mt4_e2e_acceptance.v1",
            "status": "FAIL",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "provider_registered": False,
            "production_activation": False,
            "trading_authorized": False,
        }

    rendered = json.dumps(result, indent=2, sort_keys=True)
    print(rendered)
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered + "\n", encoding="utf-8")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
