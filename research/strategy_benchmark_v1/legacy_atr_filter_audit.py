#!/usr/bin/env python3
import json, pathlib, datetime
ROOT=pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
BROOT=pathlib.Path('/data/research/phase11g/prospective_control_20260911_incremental_2/bundles')
def ts(s): return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def load_jsonl(p):
    out=[]
    with p.open() as f:
        next(f)
        for line in f:
            d=json.loads(line)
            if d.get('record_type')=='candle': out.append(d)
    return out
def atr_wilder(rows,n=14):
    tr=[]; prev=None
    for d in rows:
        h=float(d['high']); l=float(d['low']); c=float(d['close'])
        x=h-l if prev is None else max(h-l,abs(h-prev),abs(l-prev))
        tr.append(x); prev=c
    out=[None]*len(rows)
    if len(rows)<n:return out
    a=sum(tr[:n])/n; out[n-1]=a
    for i in range(n,len(rows)):
        a=(a*(n-1)+tr[i])/n; out[i]=a
    return out
def clean_atr5_before(symbol, entry_dt):
    rows=daily[symbol]; ats=daily_atr14[symbol]; valid=[]
    for i,d in enumerate(rows):
        if ts(d['close_time']) >= entry_dt: break
        a=ats[i]
        if a is None or a<=0: continue
        r=float(d['high'])-float(d['low'])
        if r >= 2*a or r <= a/3: continue
        valid.append(r)
    return sum(valid[-5:])/5 if len(valid)>=5 else None
def day_open(symbol, entry_dt):
    day=entry_dt.date()
    vals=[b for b in m15[symbol] if ts(b['open_time']).date()==day and ts(b['open_time'])<=entry_dt]
    if not vals:return None
    vals.sort(key=lambda x:x['open_time'])
    return float(vals[0]['open'])
def metrics(arr):
    n=len(arr)
    if not n:return {'n':0,'wr':None,'expectancy_R':None,'pf_R':None}
    rs=[x['net_R'] for x in arr]; w=sum(x['net_return_pct']>0 for x in arr)
    p=sum(max(0,r) for r in rs); q=-sum(min(0,r) for r in rs)
    return {'n':n,'wr':w/n,'expectancy_R':sum(rs)/n,'pf_R':p/q if q else None}
trades=[]; symbols=set()
for seg in ['development','validation']:
    p=ROOT/f'combined_rules/v2_1_trades/{seg}.jsonl'
    for line in p.read_text().splitlines():
        if line.strip():
            t=json.loads(line); t['segment']=seg; trades.append(t); symbols.add(t['symbol'])
man=json.loads((ROOT/'sources/sources_manifest.json').read_text())
daily={}; daily_atr14={}; m15={}
for s in symbols:
    daily[s]=load_jsonl(BROOT/s/'1d.jsonl'); daily_atr14[s]=atr_wilder(daily[s],14)
    m15[s]=load_jsonl(pathlib.Path(man['merged_histories'][s]['15m']['path']))
usable=[]
for t in trades:
    dt=ts(t['entry_time']); a=clean_atr5_before(t['symbol'],dt); op=day_open(t['symbol'],dt)
    if a is None or op is None or a<=0: continue
    side=1 if t['side']=='LONG' else -1
    directional=max(0.0, side*(t['entry_price']-op)); used=directional/a
    x=dict(t); x['directional_atr_used_pct']=used; usable.append(x)
out={'usable':len(usable),'total':len(trades),'segments':{}}
for seg in ['development','validation','ALL']:
    arr=usable if seg=='ALL' else [x for x in usable if x['segment']==seg]
    s={'base':metrics(arr),'buckets':{},'thresholds':{}}
    for name,lo,hi in [('0_40',0,.4),('40_60',.4,.6),('60_80',.6,.8),('80_100',.8,1.0),('gt100',1.0,99)]:
        s['buckets'][name]=metrics([x for x in arr if lo<=x['directional_atr_used_pct']<hi])
    for th in [.4,.6,.8,1.0]:
        s['thresholds'][f'lt_{int(th*100)}']=metrics([x for x in arr if x['directional_atr_used_pct']<th])
    out['segments'][seg]=s
print(json.dumps(out,indent=2,sort_keys=True))
