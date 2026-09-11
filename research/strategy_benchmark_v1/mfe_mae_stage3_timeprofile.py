#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import json
import pathlib
import statistics
from collections import defaultdict
from datetime import datetime

DEFAULT_ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
EARLY_WINDOWS = (1, 2, 4, 8)
FINAL_WINDOWS = (4, 8, 12)


def ts(v):
    return datetime.fromisoformat(v.replace('Z', '+00:00'))


def load_jsonl(path):
    with path.open() as f:
        return [json.loads(x) for x in f if x.strip()]


def load_bars(path):
    out=[]
    with path.open() as f:
        for line in f:
            d=json.loads(line)
            if d.get('record_type')!='candle':
                continue
            out.append({'open_dt':ts(d['open_time']),'close_dt':ts(d['close_time']),
                        'high':float(d['high']),'low':float(d['low']),'close':float(d['close'])})
    return out


def entry_index(bars, dt):
    arr=[b['open_dt'] for b in bars]; i=bisect.bisect_left(arr,dt)
    return i if i<len(arr) and arr[i]==dt else max(0,i-1)


def exit_index(bars, dt, reason):
    if reason in {'TIME_EXIT','GAP_STOP','GAP_TARGET'}:
        arr=[b['open_dt'] for b in bars]
    else:
        arr=[b['close_dt'] for b in bars]
    i=bisect.bisect_left(arr,dt)
    return i if i<len(arr) and arr[i]==dt else max(0,i-1)


def favorable(side, entry, bar):
    return max(0.0, (bar['high']-entry) if side==1 else (entry-bar['low']))


def dir_close_R(side, entry, close, risk):
    return side*(close-entry)/risk


def median(vs):
    vs=[v for v in vs if v is not None]
    return statistics.median(vs) if vs else None


def mean(vs):
    vs=[v for v in vs if v is not None]
    return statistics.fmean(vs) if vs else None


def metrics(rows):
    if not rows:return {'n':0}
    out={'n':len(rows),'mean_realized_R':mean([r['realized_R'] for r in rows]),
         'median_peak_MFE_R':median([r['peak_MFE_R'] for r in rows]),
         'median_peak_age_to_exit_bars':median([r['peak_age_to_exit_bars'] for r in rows]),
         'median_peak_to_terminal_giveback_R':median([r['peak_to_terminal_giveback_R'] for r in rows])}
    for w in EARLY_WINDOWS:
        out[f'median_MFE_first_{w}_bars_R']=median([r.get(f'MFE_first_{w}_bars_R') for r in rows])
        out[f'reached_0_5R_by_{w}_bars_fraction']=sum(bool(r.get(f'reached_0_5R_by_{w}_bars')) for r in rows)/len(rows)
        out[f'reached_1R_by_{w}_bars_fraction']=sum(bool(r.get(f'reached_1R_by_{w}_bars')) for r in rows)/len(rows)
    for w in FINAL_WINDOWS:
        out[f'median_terminal_change_from_tminus_{w}_R']=median([r.get(f'terminal_change_from_tminus_{w}_R') for r in rows])
    return out


def grouped(rows, field):
    d=defaultdict(list)
    for r in rows:d[str(r.get(field))].append(r)
    return {k:metrics(v) for k,v in sorted(d.items())}


def profile(trade,bars):
    entry=float(trade['entry_price']); stop=float(trade['stop_price']); risk=abs(entry-stop)
    side=1 if trade['side']=='LONG' else -1
    ei=entry_index(bars,ts(trade['entry_time'])); xi=exit_index(bars,ts(trade['exit_time']),trade['exit_reason'])
    full_end=xi
    favs=[]
    peak=0.0; peak_i=ei
    for j in range(ei,full_end):
        r=favorable(side,entry,bars[j])/risk
        favs.append((j,r))
        if r>peak:
            peak=r; peak_i=j
    if trade['exit_reason'] in {'TARGET','GAP_TARGET'}:
        terminal_price=float(trade['target_price']) if trade['exit_reason']=='TARGET' else float(trade['exit_price'])
    elif trade['exit_reason'] in {'STOP','GAP_STOP'}:
        terminal_price=float(trade['stop_price']) if trade['exit_reason']=='STOP' else float(trade['exit_price'])
    else:
        terminal_price=float(trade['exit_price'])
    terminal_dir=side*(terminal_price-entry)/risk
    if terminal_dir>peak:
        peak=terminal_dir; peak_i=xi
    gross_terminal_R=float(trade['net_R']) + float(trade.get('fee_pct') or 0)/float(trade['risk_pct']) + float(trade.get('funding_pct') or 0)/float(trade['risk_pct'])
    out={'symbol':trade['symbol'],'side':trade['side'],'entry_time':trade['entry_time'],'exit_time':trade['exit_time'],
         'episode_key':trade.get('episode_key'),'exit_reason':trade['exit_reason'],'realized_R':trade['net_R'],
         'peak_MFE_R':peak,'peak_bar_from_entry':peak_i-ei,'peak_age_to_exit_bars':xi-peak_i,
         'gross_terminal_R':gross_terminal_R,'peak_to_terminal_giveback_R':peak-gross_terminal_R}
    for w in EARLY_WINDOWS:
        vals=[r for j,r in favs if j<ei+w]
        m=max(vals) if vals else 0.0
        out[f'MFE_first_{w}_bars_R']=m
        out[f'reached_0_5R_by_{w}_bars']=m>=0.5
        out[f'reached_1R_by_{w}_bars']=m>=1.0
    for w in FINAL_WINDOWS:
        j=xi-w
        if j>=ei and j<len(bars):
            start_r=dir_close_R(side,entry,bars[j]['close'],risk)
            out[f'directional_close_tminus_{w}_R']=start_r
            out[f'terminal_change_from_tminus_{w}_R']=gross_terminal_R-start_r
        else:
            out[f'directional_close_tminus_{w}_R']=None
            out[f'terminal_change_from_tminus_{w}_R']=None
    return out


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default=str(DEFAULT_ROOT)); args=ap.parse_args()
    root=pathlib.Path(args.root); manifest=json.loads((root/'sources/sources_manifest.json').read_text())
    outdir=root/'combined_rules/mfe_mae_v2_2_stage3'; outdir.mkdir(parents=True,exist_ok=True)
    histories={}; report={'schema_version':'ktrader.mfe_mae.v2_2.stage3.v1','strategy_id':'candidate_rule_set_v2_2',
                          'diagnostic_only':True,'actual_path_only':True,'holdout_opened':False,'segments':{}}
    for seg in ('development','validation','non_holdout'):
        trades=load_jsonl(root/'combined_rules/v2_2_trades'/f'{seg}.jsonl'); rows=[]
        for t in trades:
            s=t['symbol']
            if s not in histories:histories[s]=load_bars(pathlib.Path(manifest['merged_histories'][s]['15m']['path']))
            rows.append(profile(t,histories[s]))
        with (outdir/f'{seg}.jsonl').open('w') as f:
            for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
        report['segments'][seg]={'overall':metrics(rows),'by_exit_reason':grouped(rows,'exit_reason')}
    p=outdir/'report.json'; p.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps(report,indent=2,sort_keys=True)); print('REPORT',p)

if __name__=='__main__':main()
