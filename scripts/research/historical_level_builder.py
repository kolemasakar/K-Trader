"""Research-only historical pivot extraction; no trades or backtests."""
import argparse, hashlib, json
from pathlib import Path
TF={"1w":5,"1d":4,"4h":3,"1h":2,"30m":1,"15m":1}
def read_bars(path):
    rows=[json.loads(s) for s in path.read_text().splitlines() if s.strip()]
    bars=[{"open_ms":int(x[0]),"high":float(x[2]),"low":float(x[3])} for x in rows]
    if any(a["open_ms"]>=b["open_ms"] for a,b in zip(bars,bars[1:])):
        raise ValueError("unordered/duplicate timestamps")
    return bars
def confirmed_pivots(bars,tf,left=2,right=2):
    result=[]
    for i in range(left,len(bars)-right):
        for kind,key in (("resistance","high"),("support","low")):
            price=bars[i][key]
            neighbors=[b[key] for b in bars[i-left:i]+bars[i+1:i+right+1]]
            confirmed=price>max(neighbors) if kind=="resistance" else price<min(neighbors)
            if confirmed:
                result.append({"kind":kind,"price":price,"tf":tf,"structural_weight":TF[tf],
                               "pivot_open_ms":bars[i]["open_ms"],
                               "confirmed_open_ms":bars[i+right]["open_ms"]})
    return result
def build(root,market,symbol):
    result=[];coverage=[]
    for tf in TF:
        path=Path(root)/symbol/(tf+".jsonl")
        if not path.exists():continue
        bars=read_bars(path)
        if not bars:continue
        result+=confirmed_pivots(bars,tf)
        coverage.append({"tf":tf,"bars":len(bars),"first":bars[0]["open_ms"],"last":bars[-1]["open_ms"],
                         "sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    return {"schema":"ktrader.level_pivots.research.v1","market":market,"symbol":symbol,
            "status":"PIVOTS_ONLY_UNMERGED_ATR_REGIME_GATE",
            "levels":result,"coverage":coverage}
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True);p.add_argument("--market",choices=["CRYPTO","EQUITIES","FOREX"],required=True)
    p.add_argument("--symbols",nargs="+",required=True);p.add_argument("--output",required=True)
    a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    for sym in a.symbols:
        result=build(a.root,a.market,sym)
        (out/(sym+".json")).write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
        print(sym,len(result["levels"]),result["status"])
