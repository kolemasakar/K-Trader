"""Research-only D1/W1 price-structure pivots; no ATR or trade execution."""
import argparse
import hashlib
import json
from pathlib import Path

TF={"1w":5,"1d":4}

def read_bars(path):
    rows=[json.loads(s) for s in path.read_text().splitlines() if s.strip()]
    bars=[{"open_ms":int(x[0]),"high":float(x[2]),"low":float(x[3]),
           "close_ms":int(x[6])} for x in rows]
    if any(a["open_ms"]>=b["open_ms"] or a["close_ms"]>=b["open_ms"]
           for a,b in zip(bars,bars[1:])):
        raise ValueError("unordered, duplicate or overlapping candles")
    if any(b["close_ms"]<b["open_ms"] or b["low"]>b["high"] for b in bars):
        raise ValueError("invalid candle")
    return bars

def confirmed_pivots(bars,tf,left=3,right=3):
    if tf not in TF:
        raise ValueError("initial level discovery supports only D1 and W1")
    result=[]
    for i in range(left,len(bars)-right):
        for kind,key in (("resistance","high"),("support","low")):
            price=bars[i][key]
            neighbors=[b[key] for b in bars[i-left:i]+bars[i+1:i+right+1]]
            confirmed=price>max(neighbors) if kind=="resistance" else price<min(neighbors)
            if confirmed:
                result.append({"kind":kind,"price":price,"tf":tf,
                               "structural_weight":TF[tf],
                               "pivot_open_ms":bars[i]["open_ms"],
                               "confirmed_close_ms":bars[i+right]["close_ms"]})
    return result

def build(root,market,symbol):
    levels=[];coverage=[]
    for tf in TF:
        path=Path(root)/symbol/(tf+".jsonl")
        if not path.exists():continue
        raw=path.read_bytes()
        bars=read_bars(path)
        if not bars:continue
        levels+=confirmed_pivots(bars,tf)
        coverage.append({"tf":tf,"bars":len(bars),"first":bars[0]["open_ms"],
                         "last":bars[-1]["close_ms"],"sha256":hashlib.sha256(raw).hexdigest()})
    return {"schema":"ktrader.level_pivots.research.v2","market":market,"symbol":symbol,
            "status":"D1_W1_PIVOTS_ONLY_UNMERGED_NO_ATR",
            "levels":levels,"coverage":coverage}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--market",choices=["CRYPTO","EQUITIES","FOREX"],required=True)
    p.add_argument("--symbols",nargs="+",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    for sym in a.symbols:
        result=build(a.root,a.market,sym)
        (out/(sym+".json")).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
        print(sym,len(result["levels"]),result["status"])
