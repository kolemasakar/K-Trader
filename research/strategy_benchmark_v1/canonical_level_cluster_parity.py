#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import json
import pathlib
import statistics
from collections import defaultdict
from datetime import datetime

ROOT=pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
PIVOTS_BLOB='2fd673027fa660fa20cacf7e566f6736e7baf86b'
LEVELS_BLOB='de25e3e764623c0361e334f89ffa0abbd5961e75'
ZONE_ATR_FRACTION=0.15
CONFIRM_TOUCHES=2


def ts(v): return datetime.fromisoformat(v.replace('Z','+00:00'))
def load_jsonl(path):
    with path.open() as f:return [json.loads(x) for x in f if x.strip()]
def load_bars(path):
    out=[]
    with path.open() as f:
        for line in f:
            d=json.loads(line)
            if d.get('record_type')!='candle':continue
            out.append({'open_time':d['open_time'],'close_time':d['close_time'],'open_dt':ts(d['open_time']),'close_dt':ts(d['close_time']),'open':float(d['open']),'high':float(d['high']),'low':float(d['low']),'close':float(d['close'])})
    return out

def atr_wilder(bars,n=14):
    tr=[];prev=None
    for b in bars:
        x=b['high']-b['low'] if prev is None else max(b['high']-b['low'],abs(b['high']-prev),abs(b['low']-prev));tr.append(x);prev=b['close']
    out=[None]*len(bars)
    if len(tr)<n:return out
    a=sum(tr[:n])/n;out[n-1]=a
    for i in range(n,len(tr)):a=(a*(n-1)+tr[i])/n;out[i]=a
    return out

def last_closed(bars,dt):return bisect.bisect_right([b['close_dt'] for b in bars],dt)-1

def causal_swings(bars,decision_idx,left=2,right=2):
    out=[]
    for i in range(left,decision_idx-right+1):
        b=bars[i]; L=bars[i-left:i];R=bars[i+1:i+right+1]
        if all(b['high']>x['high'] for x in L+R):out.append({'kind':'HIGH','index':i,'time':b['open_time'],'price':b['high']})
        if all(b['low']<x['low'] for x in L+R):out.append({'kind':'LOW','index':i,'time':b['open_time'],'price':b['low']})
    return out

def canonical_static_clusters(swings,atr):
    radius=atr*ZONE_ATR_FRACTION; grouped=[]
    for s in sorted(swings,key=lambda x:(x['kind'],x['price'],x['time'])):
        matched=None
        for c in grouped:
            if c[0]['kind']!=s['kind']:continue
            center=sum(x['price'] for x in c)/len(c)
            if abs(s['price']-center)<=radius:matched=c;break
        if matched is None:grouped.append([s])
        else:matched.append(s)
    levels=[]
    for c in grouped:
        if len(c)<CONFIRM_TOUCHES:continue
        center=sum(x['price'] for x in c)/len(c);side='RESISTANCE' if c[0]['kind']=='HIGH' else 'SUPPORT'
        levels.append({'side':side,'touches':len(c),'midpoint':center,'lower':min(x['price'] for x in c)-radius,'upper':max(x['price'] for x in c)+radius,'created_at':min(x['time'] for x in c),'last_test':max(x['time'] for x in c)})
    return levels

def features(t,bars,atrs):
    decision=ts(t['entry_time']);di=last_closed(bars,decision);risk=abs(float(t['entry_price'])-float(t['stop_price']));entry=float(t['entry_price']);side=1 if t['side']=='LONG' else -1
    if di<20 or risk<=0 or atrs[di] is None or atrs[di]<=0:return {'canonical_static_available':False}
    levels=canonical_static_clusters(causal_swings(bars,di),atrs[di])
    candidates=[l for l in levels if (side==1 and l['side']=='RESISTANCE' and l['midpoint']>=entry) or (side==-1 and l['side']=='SUPPORT' and l['midpoint']<=entry)]
    nxt=min(candidates,key=lambda l:abs(l['midpoint']-entry)) if candidates else None
    if nxt:
        edge=(nxt['lower'] if side==1 else nxt['upper']);edge_R=max(0.0,side*(edge-entry)/risk);mid_R=side*(nxt['midpoint']-entry)/risk
    else:edge_R=mid_R=None
    return {'canonical_static_available':True,'canonical_confirmed_level_count':len(levels),'canonical_static_open_space':nxt is None,'canonical_next_level_edge_R':edge_R,'canonical_next_level_mid_R':mid_R,'canonical_next_level_touches':nxt['touches'] if nxt else 0,'canonical_next_level_side':nxt['side'] if nxt else None}

def perf(rows):
    if not rows:return {'n':0}
    rs=[float(x['net_R']) for x in rows];gp=sum(max(0,x) for x in rs);gl=-sum(min(0,x) for x in rs)
    return {'n':len(rows),'win_rate':sum(x>0 for x in rs)/len(rs),'expectancy_R':statistics.fmean(rs),'profit_factor_R':gp/gl if gl>0 else (999.0 if gp>0 else None)}
def grouped(rows,field):
    g=defaultdict(list)
    for r in rows:g[str(r.get(field))].append(r)
    return {k:perf(v) for k,v in sorted(g.items())}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(ROOT));args=ap.parse_args();root=pathlib.Path(args.root)
    manifest=json.loads((root/'sources/sources_manifest.json').read_text());cache={};report={'schema_version':'ktrader.canonical_level_cluster.parity.v1','strategy_id':'candidate_rule_set_v2_2','diagnostic_only':True,'holdout_opened':False,'canonical_source_blobs':{'pivots.py':PIVOTS_BLOB,'levels.py':LEVELS_BLOB},'scope':'causal static swing clustering parity only; canonical BROKEN/MIRROR lifecycle is not reconstructed','parameters':{'left':2,'right':2,'zone_atr_fraction':ZONE_ATR_FRACTION,'confirm_touches':CONFIRM_TOUCHES},'segments':{}}
    for seg in ('development','validation','non_holdout'):
        trades=load_jsonl(root/'combined_rules/v2_2_trades'/f'{seg}.jsonl');custom_path=root/'combined_rules/level_context_v2'/f'{seg}.jsonl';custom=load_jsonl(custom_path) if custom_path.exists() else [];ci={(x['symbol'],x['entry_time'],x.get('episode_key')):x for x in custom};rows=[]
        for t in trades:
            s=t['symbol']
            if s not in cache:
                bars=load_bars(pathlib.Path(manifest['merged_histories'][s]['1h']['path']));cache[s]=(bars,atr_wilder(bars,14))
            bars,atrs=cache[s];x=dict(t);x.update(features(t,bars,atrs));c=ci.get((t['symbol'],t['entry_time'],t.get('episode_key')));x['level_context_v2_h1_open_space']=c.get('h1_open_space') if c else None
            a=x.get('canonical_static_open_space');b=x.get('level_context_v2_h1_open_space');x['open_space_agreement']='N/A' if a is None or b is None else ('AGREE' if bool(a)==bool(b) else 'DISAGREE');rows.append(x)
        confusion=defaultdict(int)
        for r in rows:confusion[f"canonical={r.get('canonical_static_open_space')}|level_v2={r.get('level_context_v2_h1_open_space')}"]+=1
        report['segments'][seg]={'overall':perf(rows),'by_canonical_static_open_space':grouped(rows,'canonical_static_open_space'),'by_level_context_v2_open_space':grouped(rows,'level_context_v2_h1_open_space'),'agreement_counts':dict(sorted(confusion.items()))}
        out=root/'combined_rules/canonical_level_parity_v2_2';out.mkdir(parents=True,exist_ok=True)
        with (out/f'{seg}.jsonl').open('w') as f:
            for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
    p=root/'combined_rules/canonical_level_parity_v2_2/report.json';p.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps(report,indent=2,sort_keys=True));print('REPORT',p)
if __name__=='__main__':main()
