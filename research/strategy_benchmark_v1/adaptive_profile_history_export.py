#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import pathlib
import re
from datetime import datetime, timezone

from ktrader.history import write_mtf_bundle
from ktrader.history.bundle import build_mtf_bundle
from ktrader.history.collector import collect_deep_provider_history
from ktrader.providers.base import ProviderError
from ktrader.providers.registry import create_provider

CAPS={'1d':500,'4h':1000,'1h':2000,'15m':3000,'5m':3000}
ORDER=('1d','4h','1h','15m','5m')
INSUFFICIENT=re.compile(r'insufficient deep history: requested (\d+), collected (\d+) within (\d+) pages')

def utc(v:str)->datetime:
    d=datetime.fromisoformat(v[:-1]+'+00:00' if v.endswith('Z') else v)
    if d.tzinfo is None or d.utcoffset() is None or d.utcoffset().total_seconds()!=0:raise argparse.ArgumentTypeError('UTC timestamp required')
    return d.astimezone(timezone.utc)
def z(d):return d.astimezone(timezone.utc).isoformat().replace('+00:00','Z')

async def collect_interval(provider,instrument,interval,cap,cutoff,max_pages):
    try:
        ds=await collect_deep_provider_history(provider,instrument,interval,max_bars=cap,fetched_at=cutoff,max_pages=max_pages)
        return ds,{'requested_cap':cap,'actual_bars':cap,'shortfall':0,'age_limited':False}
    except ProviderError as exc:
        m=INSUFFICIENT.search(str(exc))
        if not m:raise
        collected=int(m.group(2))
        if collected<=0:raise
        ds=await collect_deep_provider_history(provider,instrument,interval,max_bars=collected,fetched_at=cutoff,max_pages=max_pages)
        return ds,{'requested_cap':cap,'actual_bars':collected,'shortfall':cap-collected,'age_limited':True}

async def run(args):
    protocol=json.loads(pathlib.Path(args.protocol).read_text());panel=list(protocol['primary_panel']['symbols']);out=pathlib.Path(args.output);out.mkdir(parents=True,exist_ok=False)
    provider=create_provider(args.provider)
    rows=[]
    try:
        ins={x.symbol:x for x in await provider.list_instruments()}
        for symbol in panel:
            instrument=ins.get(symbol)
            if instrument is None:
                rows.append({'symbol':symbol,'status':'MISSING_INSTRUMENT'});continue
            datasets={};depths={}
            for tf in ORDER:
                ds,meta=await collect_interval(provider,instrument,tf,CAPS[tf],args.as_of,args.max_pages)
                datasets[tf]=ds;depths[tf]=meta
            bundle=build_mtf_bundle(datasets,as_of=args.as_of)
            root=write_mtf_bundle(out/'bundles'/symbol,bundle)
            row={'symbol':symbol,'status':'PASS','provider_id':provider.provider_id,'as_of':z(args.as_of),'bundle_sha256':bundle.manifest.bundle_sha256,'candle_counts':dict(bundle.manifest.candle_counts),'depths':depths,'output':str(root)};rows.append(row);print(json.dumps(row,sort_keys=True),flush=True)
    finally:
        await provider.close()
    summary={'schema_version':'ktrader.profile_research_dataset.v0','research_only':True,'not_for_v2_2_retuning':True,'provider_id':args.provider,'as_of':z(args.as_of),'caps':CAPS,'panel_size':len(panel),'pass_count':sum(r.get('status')=='PASS' for r in rows),'rows':rows}
    (out/'dataset_summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n');print('SUMMARY',out/'dataset_summary.json')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--provider',default='binance_usdm');ap.add_argument('--protocol',default='/data/research/phase11g/strategy_benchmark_v1/protocol.json');ap.add_argument('--as-of',type=utc,required=True);ap.add_argument('--output',required=True);ap.add_argument('--max-pages',type=int,default=100);args=ap.parse_args();asyncio.run(run(args))
if __name__=='__main__':main()
