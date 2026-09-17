#!/usr/bin/env python3
"""Validate Phase 11G bundle continuity and closed-bar causality."""
from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from pathlib import Path

def ts(v):
    if isinstance(v,(int,float)): return float(v)/1000 if v>1e12 else float(v)
    return datetime.fromisoformat(str(v).replace("Z","+00:00")).timestamp()

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("bundle_root",type=Path); ap.add_argument("--as-of",required=True); ap.add_argument("--output",type=Path); a=ap.parse_args(); asof=ts(a.as_of)
    errors=[]; checked=0; tf_seconds={"5m":300,"15m":900,"1h":3600,"4h":14400,"1d":86400}
    for sym in sorted(p for p in a.bundle_root.iterdir() if p.is_dir()):
        for tf,step in tf_seconds.items():
            f=sym/f"{tf}.jsonl"
            if not f.exists(): errors.append({"symbol":sym.name,"tf":tf,"error":"MISSING_FILE"}); continue
            rows=[json.loads(x) for x in f.read_text().splitlines() if x.strip()]; checked+=1
            vals=[]
            for r in rows:
                v=next((r.get(k) for k in ("open_time","open_time_ms","timestamp","ts","time") if r.get(k) is not None),None)
                if v is not None: vals.append(ts(v))
            if vals:
                if vals!=sorted(vals): errors.append({"symbol":sym.name,"tf":tf,"error":"NON_MONOTONIC"})
                if len(vals)!=len(set(vals)): errors.append({"symbol":sym.name,"tf":tf,"error":"DUPLICATE_TIMESTAMP"})
                if any(v>=asof for v in vals): errors.append({"symbol":sym.name,"tf":tf,"error":"FUTURE_OR_EQUAL_BAR"})
                gaps=sum(1 for x,y in zip(vals,vals[1:]) if y-x>step*1.5)
                if gaps: errors.append({"symbol":sym.name,"tf":tf,"error":"GAPS","count":gaps})
    report={"schema_version":"ktrader.phase11g_data_quality_watchdog.v1","as_of":a.as_of,"status":"PASS" if not errors else "FAIL_CLOSED","files_checked":checked,"error_count":len(errors),"errors":errors,"production_action":False,"holdout_opened":False}
    text=json.dumps(report,indent=2,sort_keys=True)+"\n"; print(text,end="")
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text)
    return 0 if not errors else 2
if __name__=="__main__": raise SystemExit(main())
