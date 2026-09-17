#!/usr/bin/env python3
"""Static safety regression guard for K-Trader Plugin/OpenAPI migration."""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

FORBIDDEN_METHODS=("post","put","patch","delete")
FORBIDDEN_TERMS=("orders","order","cancel","positions","account","withdraw","leverage")

def inspect(text: str) -> dict:
    methods=[]; paths=[]
    for line in text.splitlines():
        m=re.match(r"^  (/[^:]+):\s*$",line)
        if m: paths.append(m.group(1).lower())
        m=re.match(r"^    (get|post|put|patch|delete):\s*$",line,re.I)
        if m: methods.append(m.group(1).lower())
    bad_methods=sorted(set(methods).intersection(FORBIDDEN_METHODS))
    bad_paths=sorted(p for p in paths if any(t in p for t in FORBIDDEN_TERMS))
    required=["/health","/v1/scanner/status"]
    missing=[p for p in required if p not in paths]
    return {"schema_version":"ktrader.plugin_surface_guard.v1","status":"PASS" if not(bad_methods or bad_paths or missing) else "FAIL_CLOSED","read_only":not bad_methods,"methods":sorted(set(methods)),"forbidden_methods":bad_methods,"forbidden_paths":bad_paths,"missing_required_paths":missing}

def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("openapi",type=Path); ap.add_argument("--output",type=Path); a=ap.parse_args(); r=inspect(a.openapi.read_text()); text=json.dumps(r,indent=2,sort_keys=True)+"\n"; print(text,end="")
    if a.output: a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text)
    return 0 if r["status"]=="PASS" else 2
if __name__=="__main__": raise SystemExit(main())
