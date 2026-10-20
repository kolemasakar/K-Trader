#!/usr/bin/env python3
"""Prepare reproducible admission evidence. Not a strategy performance backtest."""
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from ktrader.mt4_research import MT4ResearchCorpus
from ktrader.s1_atr5 import filtered_atr5_audit
from ktrader.s1_equity_levels_replay import candidate_levels
from ktrader.s1_equity_level_rows import completed_daily,completed_weekly
from ktrader.level_admission import admit,fingerprint


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--root',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--symbol',default='ACHC.us')
    p.add_argument('--as-of',default='2026-10-07T00:00:00')
    args=p.parse_args(argv)
    root=Path(args.root).resolve(strict=True)
    output=Path(args.output).resolve(strict=True)
    if root==output or root in output.parents or output in root.parents:
        raise ValueError('source/output overlap')
    corpus=MT4ResearchCorpus(root,wall_clock_mode=True)
    data={tf:list(corpus.iter_closed(args.symbol,tf,as_of=args.as_of)) for tf in ('D1','H1','M5')}
    hashes={}
    for tf in data:
        path=corpus.paths[(args.symbol,tf)]
        lines=path.read_text(encoding='utf-8-sig').splitlines()
        actual=hashlib.sha256(('\n'.join(lines[1:])+'\n').encode()).hexdigest()
        expected=corpus.series[(args.symbol,tf)]['normalized_sha256']
        if actual!=expected:
            raise ValueError('source content hash mismatch '+tf)
        hashes[tf]=actual
    levels=candidate_levels(data['D1'])
    rows={'D1':completed_daily(data['D1']),'W1':completed_weekly(data['D1'])}
    cutoff=int(datetime.fromisoformat(args.as_of).replace(tzinfo=timezone.utc).timestamp()*1000)
    decisions=[]
    panels=[]
    for tf in ('D1','W1'):
        for candidate in levels[tf]:
            decision=admit(candidate,None,rows[tf],as_of_ms=cutoff,tick=None,source_hash=hashes['D1'])
            decisions.append({'candidate':candidate,'admission':decision.__dict__})
            indices=candidate['witness_indices']
            panels.append({'evidence_id':fingerprint(candidate),'candidate':candidate,
                           'source_sha256':hashes['D1'],'witness_rows':[rows[tf][i] for i in indices],
                           'review':{'decision':None,'reviewer':None,'method':'INDEPENDENT_LABEL',
                                     'known_at_ms':None,'strengthening':[]}})
    # Prefix parity tests witness availability on the real selected instrument.
    parity=[]
    for tf in ('D1','W1'):
        selected=levels[tf][:3]
        for candidate in selected:
            if tf=='D1':
                subset=[x for x in data['D1'] if datetime.fromisoformat(x['close_time']).replace(tzinfo=timezone.utc).timestamp()*1000<=candidate['known_at_ms']]
            else:
                # W1 availability includes the subsequent-week closed D1 observation.
                subset=[x for x in data['D1'] if datetime.fromisoformat(x['close_time']).replace(tzinfo=timezone.utc).timestamp()*1000<=candidate['known_at_ms']]
            found=candidate_levels(subset)[tf]
            parity.append({'evidence_id':fingerprint(candidate),'timeframe':tf,
                           'pass':any(x['price']==candidate['price'] and x['primary_type']==candidate['primary_type'] and x['known_at_ms']==candidate['known_at_ms'] for x in found)})
    report={'schema':'ktrader.approved_backtest_preparation.v1',
            'generated_at_utc':datetime.now(timezone.utc).isoformat(),'symbol':args.symbol,
            'status':'PREPARED_WITH_ADMISSION_BLOCKERS','run_kind':'PREPARATION_NOT_STRATEGY_BACKTEST',
            'clock':'ALGORITHMIC_WALL_CLOCK','session_accuracy':'NOT_VERIFIED_ALLOWED_FOR_ALGORITHMIC_WORK',
            'series_counts':{tf:len(bars) for tf,bars in data.items()},'source_content_sha256':hashes,
            'atr5_v2':filtered_atr5_audit(data['D1']),
            'candidate_counts':{tf:len(levels[tf]) for tf in ('D1','W1')},
            'admitted_levels':sum(x['admission']['admitted'] for x in decisions),
            'admission_blockers':dict(Counter(r for x in decisions for r in x['admission']['reasons'])),
            'prefix_parity':parity,'legacy_strategy_used':False,'legacy_benchmarks_used':False,
            'market_trades':None,'net_results':None,
            'remaining':['INDEPENDENT_REAL_LEVEL_LABELS','VERIFIED_SYMBOL_POINT_TICK',
                         'BROKER_CONTRACT_COST_PROFILE','INTEGRATED_MODEL_LIFECYCLE_ACCEPTANCE']}
    for name,value in [('preparation.json',report),('level_admission.json',decisions),('level_review_panels.json',panels)]:
        (output/name).write_text(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))
    return 0 if all(x['pass'] for x in parity) else 2


if __name__=='__main__':
    raise SystemExit(main())
