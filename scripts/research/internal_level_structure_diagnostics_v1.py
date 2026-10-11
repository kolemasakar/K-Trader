"""Internal-only structural diagnostics, not trade backtesting.

Native historical-expansion D1 inputs only. Complete UTC W1 derived from D1.
Never opens the reserved external holdout.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
def module(name):
    spec=importlib.util.spec_from_file_location(name,HERE/(name+".py"))
    obj=importlib.util.module_from_spec(spec);spec.loader.exec_module(obj)
    return obj

native=module("native_internal_d1_w1_v1")
clusters=module("structural_level_clusters_v1")

def pivots(bars,tf,left=3,right=3):
    out=[]
    for i in range(left,len(bars)-right):
        for kind,key in (("resistance","h"),("support","l")):
            p=bars[i][key]
            near=bars[i-left:i]+bars[i+1:i+right+1]
            ok=all(x[key]<p for x in near) if kind=="resistance" else all(x[key]>p for x in near)
            if ok:
                out.append({"tf":tf,"kind":kind,"price":p,
                            "pivot_open_ms":bars[i]["t"],
                            "confirmed_close_ms":bars[i+right]["close_t"]})
    return out

def evaluate_symbol(path):
    daily=native.native_d1(path)
    weekly=native.complete_w1(daily)
    levels=pivots(daily,"1d")+pivots(weekly,"1w")
    as_of=daily[-1]["close_t"] if daily else 0
    zones=clusters.cluster_confirmed(levels,as_of)
    return {"d1_bars":len(daily),"complete_w1_bars":len(weekly),
            "d1_pivots":sum(x["tf"]=="1d" for x in levels),
            "w1_pivots":sum(x["tf"]=="1w" for x in levels),
            "zones":len(zones),"mixed_d1_w1_zones":sum(len(x["timeframes"])==2 for x in zones),
            "first_d1_open_ms":daily[0]["t"] if daily else None,
            "last_d1_close_ms":as_of if daily else None,
            "raw_sha256":hashlib.sha256(Path(path).read_bytes()).hexdigest(),
            "status":"EXPLORATORY_STRUCTURE_ONLY_NOT_BACKTEST"}

def run(root):
    root=Path(root)
    if not root.is_dir():raise FileNotFoundError(root)
    results=[]
    for folder in sorted(x for x in root.iterdir() if x.is_dir()):
        path=folder/"1d.jsonl"
        if not path.exists():continue
        try:
            results.append({"symbol":folder.name,**evaluate_symbol(path)})
        except (ValueError,KeyError,TypeError,IndexError) as exc:
            results.append({"symbol":folder.name,"status":"INVALID_SOURCE","reason":str(exc)})
    return {"schema":"ktrader.internal_level_structure_diagnostics.v1",
            "status":"EXPLORATORY_NOT_OOS_VALIDATED","results":results}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    report=run(a.root)
    output=Path(a.output);output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":report["status"],"symbols":len(report["results"]),
                      "output":str(output)}))
