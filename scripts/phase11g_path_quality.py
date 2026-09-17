#!/usr/bin/env python3
"""Descriptive MFE/MAE and terminal failure-mode report for Phase 11G."""
from __future__ import annotations
import argparse, hashlib, json, statistics
from pathlib import Path

def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("families",type=Path); ap.add_argument("--as-of",required=True); ap.add_argument("--output",type=Path)
    a=ap.parse_args(); rows=[json.loads(x) for x in a.families.read_text().splitlines() if x.strip()]; res=[r for r in rows if r.get("resolved")]
    mfe=[float(r["mfe_R"]) for r in res if r.get("mfe_R") is not None]; mae=[float(r["mae_R"]) for r in res if r.get("mae_R") is not None]
    terminal={}
    for r in res: terminal[r.get("terminal_state","UNKNOWN")]=terminal.get(r.get("terminal_state","UNKNOWN"),0)+1
    report={"schema_version":"ktrader.path_quality_failure_modes.v1","as_of":a.as_of,"diagnostic_only":True,"production_action":False,"holdout_opened":False,"family_count":len(rows),"resolved_count":len(res),"terminal_state_counts":terminal,
      "mfe_R":{"n":len(mfe),"mean":sum(mfe)/len(mfe) if mfe else None,"median":statistics.median(mfe) if mfe else None,"ge_1R":sum(x>=1 for x in mfe),"ge_2R":sum(x>=2 for x in mfe),"ge_3R":sum(x>=3 for x in mfe)},
      "mae_R":{"n":len(mae),"mean":sum(mae)/len(mae) if mae else None,"median":statistics.median(mae) if mae else None,"ge_1R":sum(x>=1 for x in mae)},
      "failure_modes":{"stop_before_1R_mfe":sum(r.get("terminal_state")=="STOP" and float(r.get("mfe_R",0))<1 for r in res),"stop_after_1R_mfe":sum(r.get("terminal_state")=="STOP" and float(r.get("mfe_R",0))>=1 for r in res),"non_stop_non_target":sum(r.get("terminal_state") not in ("STOP","TARGET") for r in res)},
      "interpretation_guard":"Descriptive path-quality only; no frozen-v2.2 retuning or production selection."}
    text=json.dumps(report,indent=2,sort_keys=True)+"\n"; print(text,end="")
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text); print("sha256",hashlib.sha256(text.encode()).hexdigest())
    return 0
if __name__=="__main__": raise SystemExit(main())
