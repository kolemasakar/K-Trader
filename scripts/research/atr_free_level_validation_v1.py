"""ATR-free, read-only level validation. Research diagnostics, NOT trade backtesting."""
import argparse, hashlib, json, random, statistics
from pathlib import Path

def load(path):
    raw=path.read_bytes()
    rows=[json.loads(s) for s in raw.decode().splitlines() if s.strip()]
    b=[dict(t=int(r[0]),h=float(r[2]),l=float(r[3]),c=float(r[4]),v=float(r[5]),close_t=int(r[6])) for r in rows]
    if any(x["t"]>=y["t"] or x["close_t"]>=y["t"] for x,y in zip(b,b[1:])):
        raise ValueError("overlapping, duplicate or unordered candles")
    return b,hashlib.sha256(raw).hexdigest()

def pivots(b,left=3,right=3):
    result=[]
    for i in range(max(left,20),len(b)-right):
        med=statistics.median(x["h"]-x["l"] for x in b[i-20:i])
        for side,field in (("R","h"),("S","l")):
            price=b[i][field]
            if not all((x[field]<price if side=="R" else x[field]>price)
                       for x in b[i-left:i]+b[i+1:i+right+1]):continue
            result.append(dict(i=i,known=i+right,known_close_t=b[i+right]["close_t"],
                               side=side,price=price,anomaly=(b[i]["h"]-b[i]["l"])>2*med))
    return result

def measure(b,events,tf,tolerance=.003,horizon=30,reaction=.01,post=3):
    """First return after confirmation; OHLC extremes do not imply intrabar event order."""
    result=[]
    for e in events:
        start=e["known"]+1
        if start+horizon+post>len(b):continue
        first=next((j for j in range(start,start+horizon)
                    if b[j]["l"]<=e["price"]*(1+tolerance)
                    and b[j]["h"]>=e["price"]*(1-tolerance)),None)
        outcome=None
        if first is not None:
            following=b[first:min(first+post,len(b))]
            p=e["price"]
            favorable=(min(x["l"] for x in following)<=p*(1-reaction) if e["side"]=="R"
                       else max(x["h"] for x in following)>=p*(1+reaction))
            adverse=(max(x["h"] for x in following)>=p*(1+reaction) if e["side"]=="R"
                     else min(x["l"] for x in following)<=p*(1-reaction))
            outcome=bool(favorable and not adverse)
        result.append(dict(tf=tf,known_close_t=e["known_close_t"],anomaly=e["anomaly"],
                           touched=first is not None,reaction=outcome))
    return result

def random_controls(b,events,seed=20260928):
    """Matched as-of-date null: random price uniformly inside PRIOR 20-bar price range.
    Does not preserve local price density; baseline sensitivity must be assessed."""
    rng=random.Random(seed)
    controls=[]
    for e in events:
        prior=b[e["known"]-19:e["known"]+1]
        if len(prior)<20:continue
        lo=min(x["l"] for x in prior);hi=max(x["h"] for x in prior)
        if hi<=lo:continue
        controls.append({**e,"price":rng.uniform(lo,hi),"anomaly":False})
    return controls

def summarize(events):
    n=len(events);t=sum(x["touched"] for x in events)
    r=sum(x["reaction"] is True for x in events)
    return {"eligible":n,"returned":t,"reaction_proxy":r,
            "return_rate":round(t/n,4) if n else None,
            "reaction_given_return":round(r/t,4) if t else None}

def run(root,symbols,timeframes):
    output={"schema":"ktrader.atr_free_level_diagnostics.v1",
            "status":"EXPLORATORY_NOT_OOS_VALIDATED",
            "definitions":{"pivot_left_right":3,"anomaly":"range > 2 * median(prior 20 ranges)",
                           "touch_tolerance_price_fraction":.003,
                           "reaction_price_fraction":.01,
                           "reaction_window_bars":3,
                           "future_observation_bars":30,
                           "random_seed":20260928},
            "results":[]}
    for symbol in symbols:
        for tf in timeframes:
            path=Path(root)/symbol/(tf+".jsonl")
            if not path.exists():
                output["results"].append({"symbol":symbol,"tf":tf,"status":"MISSING_SOURCE"})
                continue
            b,digest=load(path)
            ev=pivots(b)
            # Split on confirmation time; 60%/40% chronology. Exclude events whose
            # observation horizon crosses split, avoiding contamination.
            split=int(.6*len(b))
            subsets={"early":[x for x in ev if x["known"]+34<split],
                     "late":[x for x in ev if x["known"]>=split and x["known"]+34<len(b)]}
            for period,subset in subsets.items():
                actual=measure(b,subset,tf)
                null=measure(b,random_controls(b,subset),tf)
                output["results"].append({"symbol":symbol,"tf":tf,"period":period,
                    "source_sha256":digest,"candles":len(b),
                    "confirmed_pivots":len(subset),
                    "anomalous":summarize([x for x in actual if x["anomaly"]]),
                    "ordinary":summarize([x for x in actual if not x["anomaly"]]),
                    "all_pivots":summarize(actual),"matched_random_price":summarize(null)})
    return output

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--symbols",nargs="+",required=True)
    p.add_argument("--timeframes",nargs="+",default=["1d","4h","1h"])
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=run(a.root,a.symbols,a.timeframes)
    path=Path(a.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"status":result["status"],"results":len(result["results"]),
                      "output":str(path)}))
