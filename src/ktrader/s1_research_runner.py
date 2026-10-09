"""S1 research readiness runner: source-only, no trade execution."""
import argparse
import json
from ktrader.mt4_research import MT4ResearchCorpus, CorpusError
from ktrader.s1_setup import inspect_readiness

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--symbol",default="ACHC.us")
    p.add_argument("--as-of",default="2026-10-07T00:00:00")
    a=p.parse_args(argv)
    corpus=MT4ResearchCorpus(a.root,wall_clock_mode=True)
    candles={}
    unavailable=[]
    for tf in ("D1","H1","M5"):
        try:
            candles[tf]=list(corpus.iter_closed(a.symbol,tf,as_of=a.as_of))
        except CorpusError:
            candles[tf]=[]
            unavailable.append(tf)
    result=inspect_readiness(candles["M5"],candles["H1"],candles["D1"])
    if unavailable:
        result["reasons"].append("MISSING_OR_INVALID_SERIES:"+",".join(unavailable))
    result.update({"symbol":a.symbol,"clock":"BROKER_WALL_CLOCK_ARTIFICIAL",
                   "run_kind":"READ_ONLY_S1_READINESS_NOT_BACKTEST",
                   "trades":None,"returns":None,"source_unchanged":True})
    print(json.dumps(result,sort_keys=True))
    return 0 if result["eligible"] else 2

if __name__=="__main__":
    raise SystemExit(main())
