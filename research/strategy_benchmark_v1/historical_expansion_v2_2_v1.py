#!/usr/bin/env python3
from __future__ import annotations
import collections
import hashlib
import importlib.util
import json
import pathlib
import statistics
import sys
from datetime import datetime, timezone

DATASET = pathlib.Path("/data/research/phase11g/historical_expansion_v1_20260905T144500Z")
HARNESS = pathlib.Path("/data/research/phase11g/strategy_benchmark_v1/harness/candidate_v2_2_backtest.py")
EXPECTED_HARNESS_SHA = "b8471af989090375dec9e25daae184814674a776ab9b46b45e660e35b368be08"
CUTOFF = datetime.fromisoformat("2026-09-05T14:45:00+00:00")
EVAL_BARS = 2400
OUT = DATASET / "results_v1"

def sha(path: pathlib.Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def load_harness():
    actual=sha(HARNESS)
    if actual != EXPECTED_HARNESS_SHA:
        raise SystemExit(f"FROZEN_HARNESS_SHA_MISMATCH {actual}")
    sp=importlib.util.spec_from_file_location("frozen_v22", HARNESS)
    mod=importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    return mod, actual

def summary_extra(trades):
    exits=collections.Counter(t["exit_reason"] for t in trades)
    sides=collections.Counter(t["side"] for t in trades)
    syms=collections.Counter(t["symbol"] for t in trades)
    n=len(trades)
    fee_R=sum(t["fee_pct"]/t["risk_pct"] for t in trades) if trades else 0.0
    funding_R=sum(t["funding_pct"]/t["risk_pct"] for t in trades) if trades else 0.0
    return {
        "exit_reason_counts": dict(sorted(exits.items())),
        "side_counts": dict(sorted(sides.items())),
        "symbol_trade_counts": dict(sorted(syms.items())),
        "top_symbol_share": (max(syms.values())/n if n else None),
        "aggregate_fee_R": fee_R,
        "aggregate_funding_R": funding_R,
    }

v22, harness_sha = load_harness()
protocol=json.loads(pathlib.Path("/data/research/phase11g/strategy_benchmark_v1/protocol.json").read_text())
panel=list(protocol["primary_panel"]["symbols"])
dataset_summary=json.loads((DATASET/"dataset_summary.json").read_text())
rows={r["symbol"]:r for r in dataset_summary["rows"]}
funding_summary=json.loads((DATASET/"funding_summary.json").read_text())
fund_rows={r["symbol"]:r for r in funding_summary["rows"]}

eligible=[]
coverage=[]
loaded={}
for symbol in panel:
    r=rows.get(symbol)
    reasons=[]
    if not r or r.get("status")!="PASS":
        reasons.append("DATASET_STATUS_NOT_PASS")
    counts=(r or {}).get("candle_counts",{})
    if counts.get("15m",0) < 3000:
        reasons.append("M15_LT_3000")
    if counts.get("1h",0) < 1000:
        reasons.append("H1_LT_1000")
    fr=fund_rows.get(symbol)
    if not fr or fr.get("record_count",0) <= 0:
        reasons.append("NO_FUNDING")
    coverage.append({"symbol":symbol,"included":not reasons,"reasons":reasons,"candle_counts":counts,
                     "funding_records":None if not fr else fr.get("record_count")})
    if reasons:
        continue
    m15=v22.b.load_bars(DATASET/"bundles"/symbol/"15m.jsonl")
    h1=v22.b.load_bars(DATASET/"bundles"/symbol/"1h.jsonl")
    funding=v22.b.load_funding(DATASET/"funding"/f"{symbol}.json")
    if len(m15)<EVAL_BARS:
        raise SystemExit(f"{symbol} M15_SHORT_AFTER_LOAD")
    start=len(m15)-EVAL_BARS
    end=len(m15)
    eval_last_close=m15[end-1]["close_dt"]
    if not eval_last_close < CUTOFF:
        raise SystemExit(f"{symbol} CUTOFF_VIOLATION {eval_last_close.isoformat()}")
    eval_first_open=m15[start]["open_dt"]
    loaded[symbol]=(m15,h1,funding,start,end,eval_first_open,eval_last_close)
    eligible.append(symbol)

if not eligible:
    raise SystemExit("NO_PRIMARY_COHORT")

def run(bps):
    alltr=[]
    cens=0
    per={}
    for symbol in eligible:
        m15,h1,funding,start,end,_,_=loaded[symbol]
        tr,c=v22.backtest_symbol(symbol,m15,h1,funding,start,end,bps)
        alltr.extend(tr); cens+=c
        pm=v22.v.metrics(tr,[symbol],c)
        pm.update(summary_extra(tr))
        per[symbol]=pm
    alltr.sort(key=lambda t:(t["entry_time"],t["symbol"]))
    agg=v22.v.metrics(alltr,eligible,cens)
    agg.update(summary_extra(alltr))
    return agg,per,alltr,cens

base,per_base,trades_base,cens_base=run(v22.b.SLIPPAGE_BPS["base"])
stress,per_stress,trades_stress,cens_stress=run(v22.b.SLIPPAGE_BPS["stress"])

eval_windows={
    s:{
        "first_scored_m15_open": loaded[s][5].isoformat().replace("+00:00","Z"),
        "last_scored_m15_close": loaded[s][6].isoformat().replace("+00:00","Z"),
        "scored_m15_bars": EVAL_BARS,
    } for s in eligible
}
window_starts=sorted({v["first_scored_m15_open"] for v in eval_windows.values()})
window_ends=sorted({v["last_scored_m15_close"] for v in eval_windows.values()})

OUT.mkdir(parents=True, exist_ok=False)
base_path=OUT/"base_trades.jsonl"
stress_path=OUT/"stress_trades.jsonl"
with base_path.open("w") as f:
    for t in trades_base:
        f.write(json.dumps(t,sort_keys=True)+"\n")
with stress_path.open("w") as f:
    for t in trades_stress:
        f.write(json.dumps(t,sort_keys=True)+"\n")

report={
    "schema_version":"ktrader.frozen_v2_2.historical_expansion_v1",
    "strategy_id":"candidate_rule_set_v2_2",
    "research_only":True,
    "confirmatory_historical":True,
    "prospective_evidence":False,
    "holdout_opened":False,
    "production_action":False,
    "frozen_harness_path":str(HARNESS),
    "frozen_harness_sha256":harness_sha,
    "hard_external_cutoff":"2026-09-05T14:45:00Z",
    "evaluation_bars_m15_per_symbol":EVAL_BARS,
    "primary_panel_size":len(panel),
    "primary_cohort_size":len(eligible),
    "primary_cohort_symbols":eligible,
    "coverage":coverage,
    "evaluation_window_start_values":window_starts,
    "evaluation_window_end_values":window_ends,
    "evaluation_windows":eval_windows,
    "economics":{
        "target_R":v22.b.TARGET_R,
        "max_hold_bars_m15":v22.b.MAX_HOLD_BARS,
        "fee_bps_per_side":v22.b.FEE_BPS,
        "base_slippage_bps_per_execution_side":v22.b.SLIPPAGE_BPS["base"],
        "stress_slippage_bps_per_execution_side":v22.b.SLIPPAGE_BPS["stress"],
        "funding_source":"Binance official fapi /fapi/v1/fundingRate",
    },
    "base":base,
    "stress":stress,
    "per_symbol_base":per_base,
    "per_symbol_stress":per_stress,
    "stress_delta_expectancy_R":(
        None if base.get("expectancy_R") is None or stress.get("expectancy_R") is None
        else stress["expectancy_R"]-base["expectancy_R"]
    ),
    "dataset_summary_sha256":sha(DATASET/"dataset_summary.json"),
    "funding_summary_sha256":sha(DATASET/"funding_summary.json"),
    "base_trades_sha256":sha(base_path),
    "stress_trades_sha256":sha(stress_path),
    "interpretation_guardrail":"Historical confirmatory evidence only; do not merge with prospective family-count thresholds and do not retune frozen v2.2 in place.",
}
report_path=OUT/"report.json"
report_path.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
print(json.dumps({
    "status":"PASS",
    "report":str(report_path),
    "report_sha256":sha(report_path),
    "frozen_harness_sha256":harness_sha,
    "primary_cohort_size":len(eligible),
    "window_starts":window_starts,
    "window_ends":window_ends,
    "base":base,
    "stress":stress,
    "stress_delta_expectancy_R":report["stress_delta_expectancy_R"],
    "holdout_opened":False,
    "production_action":False,
},indent=2,sort_keys=True))
