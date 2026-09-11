#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ENDPOINT='https://fapi.binance.com/fapi/v1/fundingRate'
SCHEMA='ktrader.strategy_benchmark_funding.v1'
SOURCE='Binance official fapi /fapi/v1/fundingRate'

def utc(v:str)->datetime:
    d=datetime.fromisoformat(v[:-1]+'+00:00' if v.endswith('Z') else v)
    if d.tzinfo is None or d.utcoffset() is None or d.utcoffset().total_seconds()!=0:raise argparse.ArgumentTypeError('UTC required')
    return d.astimezone(timezone.utc)
def ms(d):return int(d.timestamp()*1000)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def bundle_start(symbol_root:pathlib.Path)->datetime:
    with (symbol_root/'1d.jsonl').open() as f:
        first=json.loads(next(f))
    if first.get('record_type')!='manifest':raise ValueError(f'missing 1d manifest: {symbol_root}')
    return utc(first['actual_start'])

def request_page(symbol,start_ms,end_ms,limit=1000):
    q=urllib.parse.urlencode({'symbol':symbol,'startTime':start_ms,'endTime':end_ms,'limit':limit})
    req=urllib.request.Request(ENDPOINT+'?'+q,headers={'User-Agent':'K-Trader-Research/1.0'})
    last=None
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
        except Exception as exc:
            last=exc
            if attempt==3:raise
            time.sleep(0.5*(2**attempt))
    raise last

def collect(symbol,start_ms,end_ms):
    by_time={};cursor=start_ms
    while cursor<=end_ms:
        page=request_page(symbol,cursor,end_ms,1000)
        if not isinstance(page,list):raise RuntimeError(f'unexpected Binance funding response for {symbol}: {type(page)}')
        if not page:break
        for r in page:
            t=int(r['fundingTime'])
            if start_ms<=t<=end_ms:by_time[t]=r
        last=max(int(r['fundingTime']) for r in page)
        if last<cursor:raise RuntimeError('funding pagination moved backward')
        nxt=last+1
        if nxt<=cursor:raise RuntimeError('funding pagination stalled')
        cursor=nxt
        if len(page)<1000:break
        time.sleep(0.05)
    return [by_time[k] for k in sorted(by_time)]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--dataset-root',required=True);ap.add_argument('--as-of',required=True,type=utc);args=ap.parse_args();root=pathlib.Path(args.dataset_root);bundles=root/'bundles';out=root/'funding';out.mkdir(parents=True,exist_ok=True);rows=[];end_ms=ms(args.as_of)
    for sdir in sorted(p for p in bundles.iterdir() if p.is_dir()):
        symbol=sdir.name;start_dt=bundle_start(sdir);start_ms=ms(start_dt);records=collect(symbol,start_ms,end_ms);payload={'query_end_ms':end_ms,'query_start_ms':start_ms,'record_count':len(records),'records':records,'schema_version':SCHEMA,'source':SOURCE,'symbol':symbol};p=out/f'{symbol}.json';p.write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n');row={'symbol':symbol,'query_start_ms':start_ms,'query_end_ms':end_ms,'record_count':len(records),'first_funding_time':int(records[0]['fundingTime']) if records else None,'last_funding_time':int(records[-1]['fundingTime']) if records else None,'raw_sha256':sha(p),'path':str(p)};rows.append(row);print(json.dumps(row,sort_keys=True),flush=True)
    summary={'schema_version':'ktrader.profile_research_funding.v1','research_only':True,'provider_id':'binance_usdm','source':SOURCE,'as_of':args.as_of.isoformat().replace('+00:00','Z'),'symbol_count':len(rows),'rows':rows};sp=root/'funding_summary.json';sp.write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print('SUMMARY',sp,sha(sp))
if __name__=='__main__':main()
