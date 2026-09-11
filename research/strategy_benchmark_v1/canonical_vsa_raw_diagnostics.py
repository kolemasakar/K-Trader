#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import json
import pathlib
import statistics
from collections import defaultdict
from datetime import datetime
from decimal import Decimal

ROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1')
CANONICAL_VSA_SOURCE_BLOB = '26f90b3a1ca5523970ccbe7dabebdd84d9dc8d4d'
BASELINE_WINDOW = 20


def ts(v): return datetime.fromisoformat(v.replace('Z', '+00:00'))

def load_jsonl(path):
    with path.open() as f: return [json.loads(x) for x in f if x.strip()]


def load_bars(path):
    out = []
    with path.open() as f:
        for line in f:
            d = json.loads(line)
            if d.get('record_type') != 'candle': continue
            out.append({
                'open_time': d['open_time'], 'close_time': d['close_time'],
                'open_dt': ts(d['open_time']),
                'open': Decimal(d['open']), 'high': Decimal(d['high']), 'low': Decimal(d['low']), 'close': Decimal(d['close']),
                'volume': Decimal(d['volume']),
            })
    return out


def signal_index(bars, entry_time):
    opens = [x['open_dt'] for x in bars]
    i = bisect.bisect_left(opens, ts(entry_time))
    return i - 1 if i > 0 else None


def detect_at(bars, i):
    if i is None or i < BASELINE_WINDOW or i < 2 or i >= len(bars): return []
    bar = bars[i]; prior = bars[i-BASELINE_WINDOW:i]
    avg_volume = sum((x['volume'] for x in prior), Decimal('0')) / Decimal(BASELINE_WINDOW)
    avg_spread = sum((x['high'] - x['low'] for x in prior), Decimal('0')) / Decimal(BASELINE_WINDOW)
    spread = bar['high'] - bar['low']
    if avg_volume <= 0 or avg_spread <= 0 or spread <= 0: return []
    rel_volume = bar['volume'] / avg_volume
    rel_spread = spread / avg_spread
    close_loc = (bar['close'] - bar['low']) / spread
    p1, p2 = bars[i-1], bars[i-2]
    lower_than_prior_two = bar['volume'] < p1['volume'] and bar['volume'] < p2['volume']
    out = []
    def add(t, direction):
        out.append({'event_type': t, 'direction': direction, 'relative_volume': float(rel_volume), 'relative_spread': float(rel_spread), 'close_location': float(close_loc)})
    if bar['close'] < bar['open'] and rel_spread <= Decimal('0.8') and rel_volume <= Decimal('0.8') and lower_than_prior_two and close_loc >= Decimal('0.5'): add('NS','LONG')
    if bar['close'] > bar['open'] and rel_spread <= Decimal('0.8') and rel_volume <= Decimal('0.8') and lower_than_prior_two and close_loc <= Decimal('0.5'): add('ND','SHORT')
    if bar['low'] < min(p1['low'],p2['low']) and close_loc >= Decimal('0.6') and rel_spread <= Decimal('1.0') and rel_volume <= Decimal('1.0'): add('T','LONG')
    if bar['high'] > max(p1['high'],p2['high']) and close_loc <= Decimal('0.35') and rel_spread >= Decimal('1.2') and rel_volume >= Decimal('1.2'): add('UT','SHORT')
    if bar['close'] >= bar['open'] and rel_spread >= Decimal('1.5') and rel_volume >= Decimal('1.8') and close_loc <= Decimal('0.75'): add('BC','SHORT')
    if bar['close'] <= bar['open'] and rel_spread >= Decimal('1.5') and rel_volume >= Decimal('1.8') and close_loc >= Decimal('0.25'): add('SC','LONG')
    if bar['close'] <= bar['open'] and rel_volume >= Decimal('1.5') and rel_spread <= Decimal('1.0') and close_loc >= Decimal('0.5'): add('SV','LONG')
    return out


def perf(rows):
    if not rows: return {'n':0}
    rs=[float(r['net_R']) for r in rows]; gp=sum(max(0,x) for x in rs); gl=-sum(min(0,x) for x in rs)
    return {'n':len(rows),'win_rate':sum(x>0 for x in rs)/len(rs),'expectancy_R':statistics.fmean(rs),'profit_factor_R':gp/gl if gl>0 else (999.0 if gp>0 else None)}


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default=str(ROOT)); args=ap.parse_args(); root=pathlib.Path(args.root)
    manifest=json.loads((root/'sources/sources_manifest.json').read_text()); cache={}
    report={'schema_version':'ktrader.canonical_vsa_raw.v2_2.diagnostic.v1','strategy_id':'candidate_rule_set_v2_2','diagnostic_only':True,'holdout_opened':False,'canonical_vsa_source_blob_sha':CANONICAL_VSA_SOURCE_BLOB,'scope':'raw detect_vsa_events parity on frozen trade signal bars; contextual level/regime validation intentionally not applied','segments':{}}
    for seg in ('development','validation','non_holdout'):
        trades=load_jsonl(root/'combined_rules/v2_2_trades'/f'{seg}.jsonl'); rows=[]
        for t in trades:
            s=t['symbol']
            if s not in cache: cache[s]=load_bars(pathlib.Path(manifest['merged_histories'][s]['15m']['path']))
            events=detect_at(cache[s],signal_index(cache[s],t['entry_time']))
            x=dict(t); x['canonical_raw_vsa_events']=events
            aligned=[e['event_type'] for e in events if e['direction']==t['side']]
            opposing=[e['event_type'] for e in events if e['direction']!=t['side']]
            x['canonical_raw_vsa_aligned']=aligned; x['canonical_raw_vsa_opposing']=opposing; rows.append(x)
        by_label=defaultdict(list); state=defaultdict(list)
        for r in rows:
            ev=r['canonical_raw_vsa_events']
            labels=sorted({e['event_type'] for e in ev})
            for lab in labels: by_label[lab].append(r)
            if r['canonical_raw_vsa_aligned'] and r['canonical_raw_vsa_opposing']: st='MIXED'
            elif r['canonical_raw_vsa_aligned']: st='ALIGNED'
            elif r['canonical_raw_vsa_opposing']: st='OPPOSING'
            else: st='NONE'
            state[st].append(r)
        report['segments'][seg]={'overall':perf(rows),'signal_bar_any_raw_vsa_n':sum(bool(r['canonical_raw_vsa_events']) for r in rows),'by_event_type':{k:perf(v) for k,v in sorted(by_label.items())},'by_alignment_state':{k:perf(v) for k,v in sorted(state.items())}}
        out=root/'combined_rules/canonical_vsa_raw_v2_2'; out.mkdir(parents=True,exist_ok=True)
        with (out/f'{seg}.jsonl').open('w') as f:
            for r in rows: f.write(json.dumps(r,sort_keys=True)+'\n')
    p=root/'combined_rules/canonical_vsa_raw_v2_2/report.json'; p.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n'); print(json.dumps(report,indent=2,sort_keys=True)); print('REPORT',p)

if __name__=='__main__': main()
