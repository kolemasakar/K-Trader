#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import pathlib
import statistics
from datetime import datetime

DEFAULT_ROOT=pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
DEFAULT_HARNESS=DEFAULT_ROOT/'harness/candidate_v2_2_backtest.py'
DEFAULT_BOUNDARY='2026-09-11T20:00:00Z'


def ts(v):return datetime.fromisoformat(v.replace('Z','+00:00'))
def load_module(path):
    sp=importlib.util.spec_from_file_location('candidate_v2_2_cross_provider',path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def pearson(xs,ys):
    if len(xs)<3:return None
    mx=statistics.fmean(xs);my=statistics.fmean(ys);vx=sum((x-mx)**2 for x in xs);vy=sum((y-my)**2 for y in ys)
    return sum((x-mx)*(y-my) for x,y in zip(xs,ys))/math.sqrt(vx*vy) if vx>0 and vy>0 else None

def price_compare(primary,secondary):
    a={x['open_time']:x for x in primary};b={x['open_time']:x for x in secondary};keys=sorted(set(a)&set(b))
    basis=[];ra=[];rb=[]
    prev=None
    for k in keys:
        p=float(a[k]['close']);q=float(b[k]['close'])
        if p>0:basis.append((q/p-1.0)*10000.0)
        if prev is not None:
            pa=float(a[prev]['close']);pb=float(b[prev]['close'])
            if pa>0 and pb>0 and p>0 and q>0:
                ra.append(math.log(p/pa));rb.append(math.log(q/pb))
        prev=k
    return {'common_m15_bars':len(keys),'return_correlation':pearson(ra,rb),'median_abs_close_basis_bps':statistics.median(abs(x) for x in basis) if basis else None,'max_abs_close_basis_bps':max((abs(x) for x in basis),default=None)}

def decisions(frozen,m15,h1,boundary):
    b=frozen.b;v21=frozen.v;mx=b.indicators(m15);hx=b.indicators(h1);h1cts=[x['close_dt'] for x in h1];out=[]
    for i in range(max(53,b.PULLBACK_WINDOW),len(m15)-1):
        bar=m15[i]
        if bar['open_dt']<boundary:continue
        sig=v21.signal_at(i,m15,mx,h1,hx,h1cts)
        if sig is None:continue
        side=sig['side'];nxt=m15[i+1];entry=b.adverse(nxt['open'],side,True,b.SLIPPAGE_BPS['base']);stop=sig['stop_raw'];dist=side*(entry-stop);risk=dist/entry if entry>0 else 0.0
        if dist<=0 or risk<v21.MIN_RISK_PCT:status='REJECT_MIN_RISK_DISTANCE'
        else:
            lf=frozen.level_features(h1,hx,int(sig['features']['h1_index']),entry,stop,side)
            if lf is None:status='REJECT_LEVEL_CONTEXT_UNAVAILABLE'
            elif not lf['structural_space_gate_pass']:status='REJECT_STRUCTURAL_SPACE'
            else:status='ELIGIBLE_SHADOW_SETUP'
        out.append({'signal_bar_open_time':bar['open_time'],'side':'LONG' if side==1 else 'SHORT','status':status,'risk_pct':risk})
    return out

def event_key(symbol,e):return (symbol,e['signal_bar_open_time'],e['side'],e['status'])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--primary-root',required=True);ap.add_argument('--secondary-root',required=True);ap.add_argument('--output',required=True);ap.add_argument('--harness',default=str(DEFAULT_HARNESS));ap.add_argument('--boundary',default=DEFAULT_BOUNDARY);args=ap.parse_args()
    pr=pathlib.Path(args.primary_root);sr=pathlib.Path(args.secondary_root);outp=pathlib.Path(args.output);outp.mkdir(parents=True,exist_ok=True);frozen=load_module(pathlib.Path(args.harness));boundary=ts(args.boundary)
    symbols=sorted({p.name for p in pr.iterdir() if p.is_dir()} & {p.name for p in sr.iterdir() if p.is_dir()});per={};p_events=[];s_events=[]
    for symbol in symbols:
        pm15=frozen.b.load_bars(pr/symbol/'15m.jsonl');ph1=frozen.b.load_bars(pr/symbol/'1h.jsonl');sm15=frozen.b.load_bars(sr/symbol/'15m.jsonl');sh1=frozen.b.load_bars(sr/symbol/'1h.jsonl')
        pd=decisions(frozen,pm15,ph1,boundary);sd=decisions(frozen,sm15,sh1,boundary)
        p_events.extend((symbol,x) for x in pd);s_events.extend((symbol,x) for x in sd)
        per[symbol]={**price_compare(pm15,sm15),'primary_decisions':pd,'secondary_decisions':sd}
    pk={event_key(s,e) for s,e in p_events};sk={event_key(s,e) for s,e in s_events}
    report={'schema_version':'ktrader.cross_provider_portability.v2_2.v1','strategy_id':'candidate_rule_set_v2_2','diagnostic_only':True,'holdout_opened':False,'production_action':False,'boundary':args.boundary,'common_symbol_count':len(symbols),'symbols':symbols,'primary_root':str(pr),'secondary_root':str(sr),'primary_event_count':len(p_events),'secondary_event_count':len(s_events),'exact_decision_key_matches':len(pk&sk),'primary_only_decision_keys':[list(x) for x in sorted(pk-sk)],'secondary_only_decision_keys':[list(x) for x in sorted(sk-pk)],'median_symbol_return_correlation':statistics.median([x['return_correlation'] for x in per.values() if x['return_correlation'] is not None]) if per else None,'median_symbol_abs_basis_bps':statistics.median([x['median_abs_close_basis_bps'] for x in per.values() if x['median_abs_close_basis_bps'] is not None]) if per else None,'per_symbol':per,'interpretation_boundary':'data/signal portability only; no outcome or profitability claim'}
    p=outp/'report.json';p.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');print(json.dumps({k:report[k] for k in ('common_symbol_count','primary_event_count','secondary_event_count','exact_decision_key_matches','primary_only_decision_keys','secondary_only_decision_keys','median_symbol_return_correlation','median_symbol_abs_basis_bps')},indent=2,sort_keys=True));print('REPORT',p)
if __name__=='__main__':main()
