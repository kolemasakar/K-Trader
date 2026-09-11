#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
import statistics
from datetime import datetime

ROOT=pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
INTERVAL_MINUTES={'5m':5,'15m':15,'1h':60,'4h':240,'1d':1440,'1w':10080}
PROFILE_REQUIREMENTS={
    'FAST': ['5m','15m','1h'],
    'INTRADAY_FROZEN_V2_2': ['15m','1h'],
    'INTRADAY_ARCHITECTURE': ['15m','1h','4h'],
    'SWING': ['1h','4h','1d'],
    'POSITION': ['4h','1d','1w'],
}

def ts(v): return datetime.fromisoformat(v.replace('Z','+00:00'))
def stats(xs):
    return {'min':min(xs),'median':statistics.median(xs),'max':max(xs)} if xs else None

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(ROOT));args=ap.parse_args();root=pathlib.Path(args.root)
    m=json.loads((root/'sources/sources_manifest.json').read_text());hist=m['merged_histories'];symbols=sorted(hist)
    intervals=sorted({tf for s in symbols for tf in hist[s]},key=lambda x:INTERVAL_MINUTES.get(x,999999))
    interval_summary={}
    for tf in intervals:
        rows=[]
        for s in symbols:
            x=hist[s].get(tf)
            if not x:continue
            start,end=ts(x['actual_start']),ts(x['actual_end']);rows.append({'symbol':s,'bar_count':x['bar_count'],'duration_days':(end-start).total_seconds()/86400.0,'actual_start':x['actual_start'],'actual_end':x['actual_end']})
        interval_summary[tf]={'symbols_with_interval':len(rows),'coverage_fraction':len(rows)/len(symbols) if symbols else 0,'bar_count':stats([r['bar_count'] for r in rows]),'duration_days':stats([r['duration_days'] for r in rows]),'earliest_start':min((r['actual_start'] for r in rows),default=None),'latest_end':max((r['actual_end'] for r in rows),default=None)}
    profiles={}
    for name,req in PROFILE_REQUIREMENTS.items():
        missing={tf:[s for s in symbols if tf not in hist[s]] for tf in req}
        ready=all(not v for v in missing.values())
        profiles[name]={'required_intervals':req,'all_symbols_have_required_intervals':ready,'missing_by_interval':{k:v for k,v in missing.items() if v},'status':'STRUCTURALLY_AVAILABLE_NOT_STATISTICALLY_VALIDATED' if ready else 'DATA_CONTRACT_NOT_READY'}
    report={'schema_version':'ktrader.profile_data_readiness.v1','diagnostic_only':True,'holdout_outcomes_read':False,'source':'sources_manifest metadata only','symbol_count':len(symbols),'symbols':symbols,'merged_intervals':intervals,'interval_summary':interval_summary,'profiles':profiles,'interpretation':{'FAST':'implementation/prototype work possible if all required intervals are present; current short M5/M15 history is not enough for promotion evidence','INTRADAY_FROZEN_V2_2':'current exact v2.2 source contract is available','SWING':'requires causal merged H4 and D1 histories before executable candidate testing','POSITION':'requires H4/D1 plus a new W1 history contract before executable candidate testing'}}
    out=root/'combined_rules/profile_data_readiness_v0';out.mkdir(parents=True,exist_ok=True);p=out/'report.json';p.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2,sort_keys=True));print('REPORT',p)
if __name__=='__main__':main()
