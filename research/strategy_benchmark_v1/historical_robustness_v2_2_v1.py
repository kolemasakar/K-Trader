#!/usr/bin/env python3
from __future__ import annotations

import collections
import hashlib
import importlib.util
import json
import pathlib
from datetime import datetime, timedelta, timezone

DATASET = pathlib.Path("/data/research/phase11g/historical_robustness_v1_20260905T144500Z")
HARNESS = pathlib.Path("/data/research/phase11g/strategy_benchmark_v1/harness/candidate_v2_2_backtest.py")
EXPECTED_HARNESS_SHA = "b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08"
CUTOFF = datetime.fromisoformat("2026-09-05T14:45:00+00:00")
WINDOWS = {
    "R90": {"days": 90, "eval_m15": 8640},
    "R180": {"days": 180, "eval_m15": 17280},
    "R365": {"days": 365, "eval_m15": 35040},
}
OUT = DATASET / "results_v1"


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_harness():
    actual = sha(HARNESS)
    if actual != EXPECTED_HARNESS_SHA:
        raise SystemExit(f"FROZEN_HARNESS_SHA_MISMATCH {actual}")
    spec = importlib.util.spec_from_file_location("frozen_v22", HARNESS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, actual


def extra_metrics(trades):
    exits = collections.Counter(t["exit_reason"] for t in trades)
    sides = collections.Counter(t["side"] for t in trades)
    symbols = collections.Counter(t["symbol"] for t in trades)
    n = len(trades)
    return {
        "exit_reason_counts": dict(sorted(exits.items())),
        "side_counts": dict(sorted(sides.items())),
        "symbol_trade_counts": dict(sorted(symbols.items())),
        "top_symbol_trade_share": max(symbols.values()) / n if n else None,
        "aggregate_fee_R": sum(t["fee_pct"] / t["risk_pct"] for t in trades) if trades else 0.0,
        "aggregate_funding_R": sum(t["funding_pct"] / t["risk_pct"] for t in trades) if trades else 0.0,
    }


def direction_metrics(trades):
    out = {}
    for side in ("LONG", "SHORT"):
        items = [t for t in trades if t["side"] == side]
        rs = [t["net_R"] for t in items]
        out[side] = {
            "n": len(items),
            "wins": sum(r > 0 for r in rs),
            "losses": sum(r <= 0 for r in rs),
            "expectancy_R": sum(rs) / len(rs) if rs else None,
        }
    return out


def time_blocks(trades, start: datetime, days: int, count: int = 6):
    span = timedelta(days=days) / count
    parsed = [
        (datetime.fromisoformat(t["entry_time"].replace("Z", "+00:00")), t["net_R"])
        for t in trades
    ]
    blocks = []
    for index in range(count):
        left = start + span * index
        right = start + span * (index + 1)
        values = [r for ts, r in parsed if left <= ts < right]
        blocks.append({
            "block": index + 1,
            "start": left.isoformat().replace("+00:00", "Z"),
            "end": right.isoformat().replace("+00:00", "Z"),
            "n": len(values),
            "wins": sum(r > 0 for r in values),
            "losses": sum(r <= 0 for r in values),
            "expectancy_R": sum(values) / len(values) if values else None,
        })
    return blocks


v22, harness_sha = load_harness()
summary_path = DATASET / "dataset_summary.json"
funding_summary_path = DATASET / "funding_summary.json"
dataset_summary = json.loads(summary_path.read_text())
funding_summary = json.loads(funding_summary_path.read_text())
rows = {row["symbol"]: row for row in dataset_summary["rows"]}
fund_rows = {row["symbol"]: row for row in funding_summary["rows"]}

OUT.mkdir(parents=True, exist_ok=False)
reports = {}

for window_name, spec in WINDOWS.items():
    cohort = [
        symbol for symbol, row in rows.items()
        if row.get("status") == "PASS"
        and row.get("window_readiness_pre_outcome", {}).get(window_name, {}).get("ready") is True
    ]
    cohort.sort()
    loaded = {}
    coverage = []
    for symbol in sorted(rows):
        row = rows[symbol]
        ready = symbol in cohort
        coverage.append({
            "symbol": symbol,
            "included": ready,
            "readiness": row.get("window_readiness_pre_outcome", {}).get(window_name),
            "depths": row.get("depths"),
        })
        if not ready:
            continue
        m15 = v22.b.load_bars(DATASET / "bundles" / symbol / "15m.jsonl")
        h1 = v22.b.load_bars(DATASET / "bundles" / symbol / "1h.jsonl")
        funding = v22.b.load_funding(DATASET / "funding" / f"{symbol}.json")
        eval_bars = spec["eval_m15"]
        if len(m15) < eval_bars:
            raise SystemExit(f"{window_name} {symbol} M15_SHORT")
        start = len(m15) - eval_bars
        end = len(m15)
        first_open = m15[start]["open_dt"]
        last_close = m15[end - 1]["close_dt"]
        if not last_close < CUTOFF:
            raise SystemExit(f"{window_name} {symbol} CUTOFF_VIOLATION")
        fr = fund_rows.get(symbol)
        if not fr or not fr.get("record_count"):
            raise SystemExit(f"{window_name} {symbol} FUNDING_MISSING")
        first_funding = datetime.fromtimestamp(fr["first_funding_time"] / 1000.0, tz=timezone.utc)
        if first_funding > first_open:
            raise SystemExit(f"{window_name} {symbol} FUNDING_COVERAGE_LATE")
        loaded[symbol] = (m15, h1, funding, start, end, first_open, last_close)

    if not cohort:
        raise SystemExit(f"{window_name} EMPTY_COHORT")

    def run(bps):
        all_trades = []
        censored = 0
        per_symbol = {}
        for symbol in cohort:
            m15, h1, funding, start, end, _, _ = loaded[symbol]
            trades, cens = v22.backtest_symbol(symbol, m15, h1, funding, start, end, bps)
            all_trades.extend(trades)
            censored += cens
            metrics = v22.v.metrics(trades, [symbol], cens)
            metrics.update(extra_metrics(trades))
            per_symbol[symbol] = metrics
        all_trades.sort(key=lambda t: (t["entry_time"], t["symbol"]))
        aggregate = v22.v.metrics(all_trades, cohort, censored)
        aggregate.update(extra_metrics(all_trades))
        return aggregate, per_symbol, all_trades

    base, per_base, base_trades = run(v22.b.SLIPPAGE_BPS["base"])
    stress, per_stress, stress_trades = run(v22.b.SLIPPAGE_BPS["stress"])

    window_dir = OUT / window_name
    window_dir.mkdir()
    base_file = window_dir / "base_trades.jsonl"
    stress_file = window_dir / "stress_trades.jsonl"
    with base_file.open("w") as handle:
        for trade in base_trades:
            handle.write(json.dumps(trade, sort_keys=True) + "\n")
    with stress_file.open("w") as handle:
        for trade in stress_trades:
            handle.write(json.dumps(trade, sort_keys=True) + "\n")

    starts = sorted({loaded[s][5] for s in cohort})
    ends = sorted({loaded[s][6] for s in cohort})
    if len(starts) != 1 or len(ends) != 1:
        raise SystemExit(f"{window_name} NON_COMMON_CLOCK_WINDOW")
    common_start = starts[0]
    common_end = ends[0]

    report = {
        "schema_version": "ktrader.frozen_v2_2.historical_robustness_window.v1",
        "window": window_name,
        "days": spec["days"],
        "eval_m15": spec["eval_m15"],
        "strategy_id": "candidate_rule_set_v2_2",
        "research_only": True,
        "secondary_robustness": True,
        "prospective_evidence": False,
        "holdout_opened": False,
        "production_action": False,
        "frozen_harness_sha256": harness_sha,
        "hard_external_cutoff": "2026-09-05T14:45:00Z",
        "cohort_size": len(cohort),
        "cohort_symbols": cohort,
        "coverage": coverage,
        "window_start": common_start.isoformat().replace("+00:00", "Z"),
        "window_end": common_end.isoformat().replace("+00:00", "Z"),
        "base": base,
        "stress": stress,
        "direction_base": direction_metrics(base_trades),
        "time_blocks_base": time_blocks(base_trades, common_start, spec["days"], 6),
        "per_symbol_base": per_base,
        "per_symbol_stress": per_stress,
        "stress_delta_expectancy_R": (
            None if base.get("expectancy_R") is None or stress.get("expectancy_R") is None
            else stress["expectancy_R"] - base["expectancy_R"]
        ),
        "base_trades_sha256": sha(base_file),
        "stress_trades_sha256": sha(stress_file),
        "interpretation_guardrail": "Secondary historical robustness only; no in-place v2.2 retuning and no prospective family-count merge.",
    }
    report_file = window_dir / "report.json"
    report_file.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    reports[window_name] = {
        "report": str(report_file),
        "report_sha256": sha(report_file),
        "cohort_size": len(cohort),
        "window_start": report["window_start"],
        "window_end": report["window_end"],
        "base": base,
        "stress": stress,
        "direction_base": report["direction_base"],
        "stress_delta_expectancy_R": report["stress_delta_expectancy_R"],
    }

index = {
    "schema_version": "ktrader.frozen_v2_2.historical_robustness_v1",
    "frozen_harness_sha256": harness_sha,
    "dataset_summary_sha256": sha(summary_path),
    "funding_summary_sha256": sha(funding_summary_path),
    "holdout_opened": False,
    "production_action": False,
    "windows": reports,
}
index_file = OUT / "index.json"
index_file.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
print(json.dumps({"status": "PASS", "index": str(index_file), "index_sha256": sha(index_file), **index}, indent=2, sort_keys=True))
