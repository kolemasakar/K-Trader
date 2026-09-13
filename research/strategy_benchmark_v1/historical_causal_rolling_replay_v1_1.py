#!/usr/bin/env python3
from __future__ import annotations

import bisect
import collections
import hashlib
import importlib.util
import json
import pathlib
import statistics
from datetime import datetime, timedelta, timezone

DATASET = pathlib.Path("/data/research/phase11g/historical_robustness_v1_20260905T144500Z")
HARNESS = pathlib.Path("/data/research/phase11g/strategy_benchmark_v1/harness/candidate_v2_2_backtest.py")
EXPECTED_HARNESS_SHA = "b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08"
CUTOFF = datetime.fromisoformat("2026-09-05T14:45:00+00:00")
PROSPECTIVE_SNAPSHOT = pathlib.Path("/data/research/phase11g/v2_2_shadow_20260913T083000Z/bundles")
M15_CONTEXT = 400
H1_CONTEXT = 300
PARITY_M15_BARS = 96
WINDOWS = {
    "P25": {"days": 25, "eval_m15": 2400},
    "R90": {"days": 90, "eval_m15": 8640},
    "R180": {"days": 180, "eval_m15": 17280},
    "R365": {"days": 365, "eval_m15": 35040},
}
OUT = DATASET / "results_rolling_context_v1"


def sha(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def z(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def load_harness():
    actual = sha(HARNESS)
    if actual != EXPECTED_HARNESS_SHA:
        raise SystemExit(f"FROZEN_HARNESS_SHA_MISMATCH {actual}")
    spec = importlib.util.spec_from_file_location("frozen_v22", HARNESS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, actual


v22, harness_sha = load_harness()
indicator_globals = v22.b.indicators.__globals__
ema = indicator_globals["ema"]
atr_wilder = indicator_globals["atr_wilder"]
rsi_wilder = indicator_globals["rsi_wilder"]

protocol = json.loads(pathlib.Path("/data/research/phase11g/strategy_benchmark_v1/protocol.json").read_text())
panel = list(protocol["primary_panel"]["symbols"])
dataset_summary_path = DATASET / "dataset_summary.json"
funding_summary_path = DATASET / "funding_summary.json"
dataset_summary = json.loads(dataset_summary_path.read_text())
funding_summary = json.loads(funding_summary_path.read_text())
rows = {row["symbol"]: row for row in dataset_summary["rows"]}
fund_rows = {row["symbol"]: row for row in funding_summary["rows"]}


def m15_indicators_exact_sparse(bars):
    closes = [bar["close"] for bar in bars]
    n = len(bars)
    qv = [None] * n
    i = n - 1
    if i >= 20:
        qv[i] = sum(bar["quote_volume"] for bar in bars[i - 20 : i]) / 20
    return {
        "ema20": ema(closes, 20),
        "ema50": [None] * n,
        "atr14": atr_wilder(bars, 14),
        "rsi14": rsi_wilder(closes, 14),
        "qv20prev": qv,
    }


def h1_indicators_exact_sparse(bars):
    closes = [bar["close"] for bar in bars]
    n = len(bars)
    return {
        "ema20": ema(closes, 20),
        "ema50": ema(closes, 50),
        "atr14": atr_wilder(bars, 14),
        "rsi14": [None] * n,
        "qv20prev": [None] * n,
    }


def rolling_signal_at(m15, h1, h1cts, i, h1_cache):
    m_start = max(0, i - M15_CONTEXT + 1)
    lm = m15[m_start : i + 1]
    mx = m15_indicators_exact_sparse(lm)
    decision_dt = lm[-1]["close_dt"]
    h_abs = bisect.bisect_right(h1cts, decision_dt) - 1
    if h_abs < 0:
        return None, {
            "m15_count": len(lm), "h1_count": 0, "m15_start_abs": m_start,
            "h1_start_abs": None, "h1_decision_abs": None,
        }
    cached = h1_cache.get(h_abs)
    if cached is None:
        h_start = max(0, h_abs - H1_CONTEXT + 1)
        lh = h1[h_start : h_abs + 1]
        hx = h1_indicators_exact_sparse(lh)
        lhcts = [bar["close_dt"] for bar in lh]
        cached = (h_start, lh, hx, lhcts)
        h1_cache[h_abs] = cached
    h_start, lh, hx, lhcts = cached
    raw = v22.v.signal_at(len(lm) - 1, lm, mx, lh, hx, lhcts)
    audit = {
        "m15_count": len(lm), "h1_count": len(lh), "m15_start_abs": m_start,
        "h1_start_abs": h_start, "h1_decision_abs": h_abs,
    }
    if raw is None:
        return None, audit

    local_pullback = int(raw["features"]["pullback_episode_index"])
    global_pullback = m_start + local_pullback
    features = dict(raw["features"])
    features.update({
        "rolling_context_m15_count": len(lm),
        "rolling_context_h1_count": len(lh),
        "rolling_m15_start_abs_index": m_start,
        "rolling_h1_start_abs_index": h_start,
        "h1_abs_index": h_start + int(raw["features"]["h1_index"]),
        "pullback_episode_abs_index": global_pullback,
    })
    return {
        "side": raw["side"],
        "stop_raw": raw["stop_raw"],
        "episode_key": f"{raw['side']}:{global_pullback}",
        "features": features,
        "_h1": lh,
        "_hx": hx,
        "_decision_idx_local": int(raw["features"]["h1_index"]),
    }, audit


def stripped_rolling_signal(signal, direct_episode_key):
    if signal is None:
        return None
    features = dict(signal["features"])
    for key in (
        "rolling_context_m15_count", "rolling_context_h1_count",
        "rolling_m15_start_abs_index", "rolling_h1_start_abs_index",
        "h1_abs_index", "pullback_episode_abs_index",
    ):
        features.pop(key, None)
    return {
        "side": signal["side"],
        "stop_raw": signal["stop_raw"],
        "episode_key": direct_episode_key,
        "features": features,
    }


def same_json(a, b):
    return json.dumps(a, sort_keys=True, separators=(",", ":"), allow_nan=False) == json.dumps(
        b, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def parity_gate():
    if not PROSPECTIVE_SNAPSHOT.exists():
        raise SystemExit("PARITY_SNAPSHOT_MISSING")
    result_rows = []
    mismatches = []
    total_signals = 0
    structural_cases = 0
    for symbol in panel:
        m15 = v22.b.load_bars(PROSPECTIVE_SNAPSHOT / symbol / "15m.jsonl")
        h1 = v22.b.load_bars(PROSPECTIVE_SNAPSHOT / symbol / "1h.jsonl")
        if len(m15) != M15_CONTEXT or len(h1) != H1_CONTEXT:
            mismatches.append({"symbol": symbol, "reason": "DEPTH_MISMATCH", "m15": len(m15), "h1": len(h1)})
            continue
        mx_full = v22.b.indicators(m15)
        hx_full = v22.b.indicators(h1)
        h1cts = [bar["close_dt"] for bar in h1]
        h1_cache = {}
        begin = max(1, len(m15) - PARITY_M15_BARS)
        row_signals = 0
        row_structural = 0
        for i in range(begin, len(m15)):
            direct = v22.v.signal_at(i, m15, mx_full, h1, hx_full, h1cts)
            rolling, audit = rolling_signal_at(m15, h1, h1cts, i, h1_cache)
            if audit["m15_count"] > M15_CONTEXT or audit["h1_count"] > H1_CONTEXT:
                mismatches.append({"symbol": symbol, "i": i, "reason": "CONTEXT_CAP"})
                continue
            if direct is None:
                if rolling is not None:
                    mismatches.append({"symbol": symbol, "i": i, "reason": "NONE_MISMATCH"})
                continue
            row_signals += 1
            total_signals += 1
            if rolling is None:
                mismatches.append({"symbol": symbol, "i": i, "reason": "SIGNAL_MISSING"})
                continue
            normalized = stripped_rolling_signal(rolling, direct["episode_key"])
            if not same_json(direct, normalized):
                mismatches.append({"symbol": symbol, "i": i, "reason": "SIGNAL_PAYLOAD"})
                continue
            if i + 1 < len(m15):
                side = direct["side"]
                ep = v22.b.adverse(m15[i + 1]["open"], side, True, v22.b.SLIPPAGE_BPS["base"])
                lf_direct = v22.level_features(h1, hx_full, int(direct["features"]["h1_index"]), ep, direct["stop_raw"], side)
                lf_roll = v22.level_features(rolling["_h1"], rolling["_hx"], rolling["_decision_idx_local"], ep, rolling["stop_raw"], side)
                row_structural += 1
                structural_cases += 1
                if not same_json(lf_direct, lf_roll):
                    mismatches.append({"symbol": symbol, "i": i, "reason": "STRUCTURAL_PAYLOAD"})
        result_rows.append({"symbol": symbol, "bars_checked": len(m15) - begin, "signals": row_signals, "structural_cases": row_structural})
    status = "PASS" if not mismatches and len(result_rows) == len(panel) else "FAIL"
    result = {
        "status": status,
        "snapshot": str(PROSPECTIVE_SNAPSHOT),
        "symbols_checked": len(result_rows),
        "bars_per_symbol_checked": PARITY_M15_BARS,
        "signal_cases": total_signals,
        "structural_cases": structural_cases,
        "m15_context_cap": M15_CONTEXT,
        "h1_context_cap": H1_CONTEXT,
        "rows": result_rows,
        "mismatches": mismatches,
    }
    if status != "PASS":
        raise SystemExit("PARITY_GATE_FAIL " + json.dumps(result, sort_keys=True))
    return result


def cohort_for(name):
    cohort = []
    for symbol in panel:
        row = rows.get(symbol)
        if not row or row.get("status") != "PASS":
            continue
        if name == "P25":
            ready = (
                int(row["depths"]["15m"]["actual"]) >= WINDOWS[name]["eval_m15"] + M15_CONTEXT
                and int(row["depths"]["1h"]["actual"]) >= 25 * 24 + H1_CONTEXT
            )
        else:
            ready = bool(row.get("window_readiness_pre_outcome", {}).get(name, {}).get("ready"))
        if ready:
            cohort.append(symbol)
    return sorted(cohort)


def precompute_signals(symbol, m15, h1, first_i, last_i):
    h1cts = [bar["close_dt"] for bar in h1]
    h1_cache = {}
    signal_map = {}
    audit = {"decision_bars": 0, "signals": 0, "m15_context_min": None, "m15_context_max": 0, "h1_context_min": None, "h1_context_max": 0}
    for i in range(first_i, last_i + 1):
        signal, row = rolling_signal_at(m15, h1, h1cts, i, h1_cache)
        audit["decision_bars"] += 1
        for prefix, value in (("m15_context", row["m15_count"]), ("h1_context", row["h1_count"])):
            mn, mx = prefix + "_min", prefix + "_max"
            audit[mn] = value if audit[mn] is None else min(audit[mn], value)
            audit[mx] = max(audit[mx], value)
        if row["m15_count"] > M15_CONTEXT or row["h1_count"] > H1_CONTEXT:
            raise SystemExit(f"{symbol} CONTEXT_CAP_VIOLATION {i}")
        if signal is not None:
            signal_map[i] = signal
            audit["signals"] += 1
    audit["h1_context_cache_entries"] = len(h1_cache)
    return signal_map, audit


def backtest_symbol(symbol, m15, funding, start, end, bps, signal_map):
    trades, pos, pending = [], None, None
    pending_exit = False
    last_episode = set()
    censored = 0
    for i in range(max(1, start - 1), end):
        bar = m15[i]
        if pos is not None and pending_exit:
            trades.append(v22.b.finish(symbol, pos, i, bar["open_dt"], bar["open"], "TIME_EXIT", bps, funding))
            pos = None
            pending_exit = False
        if pos is None and pending is not None and i >= start:
            side = pending["side"]
            ep = v22.b.adverse(bar["open"], side, True, bps)
            stop = pending["stop_raw"]
            dist = side * (ep - stop)
            risk_pct = dist / ep if ep > 0 else 0.0
            if dist > 0 and risk_pct >= v22.v.MIN_RISK_PCT and pending["episode_key"] not in last_episode:
                lf = v22.level_features(pending["_h1"], pending["_hx"], pending["_decision_idx_local"], ep, stop, side)
                if lf is not None and lf["structural_space_gate_pass"]:
                    features = dict(pending["features"])
                    features.update(lf)
                    pos = {
                        "side": side, "entry_i": i, "entry_time": bar["open_dt"], "entry": ep,
                        "stop": stop, "target": ep + side * v22.b.TARGET_R * dist, "risk_pct": risk_pct,
                        "episode_key": pending["episode_key"], "features": features,
                    }
                    last_episode.add(pending["episode_key"])
            pending = None
        if pos is not None:
            gap_stop = (pos["side"] == 1 and bar["open"] <= pos["stop"]) or (pos["side"] == -1 and bar["open"] >= pos["stop"])
            gap_target = (pos["side"] == 1 and bar["open"] >= pos["target"]) or (pos["side"] == -1 and bar["open"] <= pos["target"])
            if gap_stop:
                trades.append(v22.b.finish(symbol, pos, i, bar["open_dt"], bar["open"], "GAP_STOP", bps, funding)); pos = None
            elif gap_target:
                trades.append(v22.b.finish(symbol, pos, i, bar["open_dt"], bar["open"], "GAP_TARGET", bps, funding)); pos = None
            else:
                stop_hit = (pos["side"] == 1 and bar["low"] <= pos["stop"]) or (pos["side"] == -1 and bar["high"] >= pos["stop"])
                target_hit = (pos["side"] == 1 and bar["high"] >= pos["target"]) or (pos["side"] == -1 and bar["low"] <= pos["target"])
                if stop_hit:
                    trades.append(v22.b.finish(symbol, pos, i, bar["close_dt"], pos["stop"], "STOP", bps, funding)); pos = None
                elif target_hit:
                    trades.append(v22.b.finish(symbol, pos, i, bar["close_dt"], pos["target"], "TARGET", bps, funding)); pos = None
        if i >= end - 1:
            continue
        if pos is not None:
            if i - pos["entry_i"] + 1 >= v22.b.MAX_HOLD_BARS:
                pending_exit = True
        elif pending is None:
            candidate = signal_map.get(i)
            if candidate is not None and candidate["episode_key"] not in last_episode:
                pending = candidate
    if pos is not None:
        censored += 1
    return trades, censored


def extra_metrics(trades):
    exits = collections.Counter(t["exit_reason"] for t in trades)
    sides = collections.Counter(t["side"] for t in trades)
    symbols = collections.Counter(t["symbol"] for t in trades)
    rs = [t["net_R"] for t in trades]
    gp = sum(r for r in rs if r > 0); gl = -sum(r for r in rs if r < 0)
    return {
        "exit_reason_counts": dict(sorted(exits.items())),
        "side_counts": dict(sorted(sides.items())),
        "symbol_trade_counts": dict(sorted(symbols.items())),
        "top_symbol_trade_share": max(symbols.values()) / len(trades) if trades else None,
        "profit_factor_R": gp / gl if gl > 0 else (999.0 if gp > 0 else None),
        "avg_win_R": statistics.fmean([r for r in rs if r > 0]) if any(r > 0 for r in rs) else None,
        "avg_loss_R": statistics.fmean([r for r in rs if r < 0]) if any(r < 0 for r in rs) else None,
        "aggregate_fee_R": sum(t["fee_pct"] / t["risk_pct"] for t in trades) if trades else 0.0,
        "aggregate_funding_R": sum(t["funding_pct"] / t["risk_pct"] for t in trades) if trades else 0.0,
    }


def direction_metrics(trades):
    out = {}
    for side in ("LONG", "SHORT"):
        items = [t for t in trades if t["side"] == side]; rs = [t["net_R"] for t in items]
        out[side] = {"n": len(items), "wins": sum(r > 0 for r in rs), "losses": sum(r <= 0 for r in rs), "expectancy_R": sum(rs) / len(rs) if rs else None}
    return out


def time_blocks(trades, start, days, count=6):
    span = timedelta(days=days) / count
    parsed = [(datetime.fromisoformat(t["entry_time"].replace("Z", "+00:00")), t["net_R"]) for t in trades]
    out = []
    for idx in range(count):
        left, right = start + span * idx, start + span * (idx + 1)
        rs = [r for ts, r in parsed if left <= ts < right]
        out.append({"block": idx + 1, "start": z(left), "end": z(right), "n": len(rs), "wins": sum(r > 0 for r in rs), "losses": sum(r <= 0 for r in rs), "expectancy_R": sum(rs) / len(rs) if rs else None})
    return out


parity = parity_gate()
cohorts = {name: cohort_for(name) for name in WINDOWS}
loaded, context_audit = {}, {}
for symbol in panel:
    applicable = [name for name in WINDOWS if symbol in cohorts[name]]
    if not applicable:
        continue
    m15 = v22.b.load_bars(DATASET / "bundles" / symbol / "15m.jsonl")
    h1 = v22.b.load_bars(DATASET / "bundles" / symbol / "1h.jsonl")
    funding = v22.b.load_funding(DATASET / "funding" / f"{symbol}.json")
    min_start = min(len(m15) - WINDOWS[name]["eval_m15"] for name in applicable)
    signal_map, audit = precompute_signals(symbol, m15, h1, max(1, min_start - 1), len(m15) - 2)
    loaded[symbol] = (m15, funding, signal_map)
    context_audit[symbol] = audit

OUT.mkdir(parents=True, exist_ok=False)
parity_path = OUT / "parity_gate.json"; parity_path.write_text(json.dumps(parity, indent=2, sort_keys=True) + "\n")
audit_path = OUT / "context_audit.json"; audit_path.write_text(json.dumps(context_audit, indent=2, sort_keys=True) + "\n")

reports = {}
for name, spec in WINDOWS.items():
    cohort = cohorts[name]
    if not cohort:
        raise SystemExit(f"{name} EMPTY_COHORT")
    starts, ends, coverage = set(), set(), []
    for symbol in panel:
        included = symbol in cohort
        row = rows.get(symbol, {})
        coverage.append({"symbol": symbol, "included": included, "readiness": {"ready": included, "source": "P25_CAUSAL_DEPTH"} if name == "P25" else row.get("window_readiness_pre_outcome", {}).get(name)})
        if included:
            m15 = loaded[symbol][0]; start = len(m15) - spec["eval_m15"]
            starts.add(m15[start]["open_dt"]); ends.add(m15[-1]["close_dt"])
            if not m15[-1]["close_dt"] < CUTOFF:
                raise SystemExit(f"{name} {symbol} CUTOFF_VIOLATION")
            fr = fund_rows.get(symbol)
            if not fr or not fr.get("record_count"):
                raise SystemExit(f"{name} {symbol} FUNDING_MISSING")
            if datetime.fromtimestamp(fr["first_funding_time"] / 1000.0, tz=timezone.utc) > m15[start]["open_dt"]:
                raise SystemExit(f"{name} {symbol} FUNDING_COVERAGE_LATE")
    if len(starts) != 1 or len(ends) != 1:
        raise SystemExit(f"{name} NON_COMMON_CLOCK_WINDOW")
    common_start, common_end = next(iter(starts)), next(iter(ends))

    def run(bps):
        all_trades, censored, per_symbol = [], 0, {}
        for symbol in cohort:
            m15, funding, signal_map = loaded[symbol]
            start, end = len(m15) - spec["eval_m15"], len(m15)
            trades, cens = backtest_symbol(symbol, m15, funding, start, end, bps, signal_map)
            all_trades.extend(trades); censored += cens
            pm = v22.v.metrics(trades, [symbol], cens); pm.update(extra_metrics(trades)); per_symbol[symbol] = pm
        all_trades.sort(key=lambda t: (t["entry_time"], t["symbol"]))
        agg = v22.v.metrics(all_trades, cohort, censored); agg.update(extra_metrics(all_trades))
        return agg, per_symbol, all_trades

    base, per_base, base_trades = run(v22.b.SLIPPAGE_BPS["base"])
    stress, per_stress, stress_trades = run(v22.b.SLIPPAGE_BPS["stress"])
    window_dir = OUT / name; window_dir.mkdir()
    base_path, stress_path = window_dir / "base_trades.jsonl", window_dir / "stress_trades.jsonl"
    base_path.write_text("".join(json.dumps(t, sort_keys=True) + "\n" for t in base_trades))
    stress_path.write_text("".join(json.dumps(t, sort_keys=True) + "\n" for t in stress_trades))
    report = {
        "schema_version": "ktrader.frozen_v2_2.causal_rolling_context_window.v1",
        "window": name, "days": spec["days"], "eval_m15": spec["eval_m15"],
        "strategy_id": "candidate_rule_set_v2_2", "research_only": True, "corrected_methodology": True,
        "prospective_evidence": False, "holdout_opened": False, "production_action": False,
        "frozen_harness_sha256": harness_sha, "hard_external_cutoff": "2026-09-05T14:45:00Z",
        "rolling_context": {"m15_max_closed_bars": M15_CONTEXT, "h1_max_closed_bars": H1_CONTEXT},
        "parity_gate_sha256": sha(parity_path), "cohort_size": len(cohort), "cohort_symbols": cohort,
        "coverage": coverage, "window_start": z(common_start), "window_end": z(common_end),
        "base": base, "stress": stress, "direction_base": direction_metrics(base_trades),
        "time_blocks_base": time_blocks(base_trades, common_start, spec["days"], 6),
        "per_symbol_base": per_base, "per_symbol_stress": per_stress,
        "stress_delta_expectancy_R": None if base.get("expectancy_R") is None or stress.get("expectancy_R") is None else stress["expectancy_R"] - base["expectancy_R"],
        "base_trades_sha256": sha(base_path), "stress_trades_sha256": sha(stress_path),
        "interpretation_guardrail": "Corrected historical evidence only; do not merge with prospective family counts and do not retune frozen v2.2 in place.",
    }
    report_path = window_dir / "report.json"; report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    reports[name] = {"report": str(report_path), "report_sha256": sha(report_path), "cohort_size": len(cohort), "window_start": report["window_start"], "window_end": report["window_end"], "base": base, "stress": stress, "direction_base": report["direction_base"], "stress_delta_expectancy_R": report["stress_delta_expectancy_R"]}

index = {
    "schema_version": "ktrader.frozen_v2_2.causal_rolling_context_replay.v1",
    "status": "PASS", "frozen_harness_sha256": harness_sha,
    "dataset_summary_sha256": sha(dataset_summary_path), "funding_summary_sha256": sha(funding_summary_path),
    "parity_gate_sha256": sha(parity_path), "context_audit_sha256": sha(audit_path),
    "rolling_context": {"m15_max_closed_bars": M15_CONTEXT, "h1_max_closed_bars": H1_CONTEXT},
    "holdout_opened": False, "production_action": False,
    "supersedes_for_inference": ["historical_expansion_v1_20260905T144500Z/results_v1", "historical_robustness_v1_20260905T144500Z/results_v1"],
    "windows": reports,
}
index_path = OUT / "index.json"; index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n")
print(json.dumps({"status": "PASS", "index": str(index_path), "index_sha256": sha(index_path), "parity": parity, "windows": reports, "holdout_opened": False, "production_action": False}, indent=2, sort_keys=True))
