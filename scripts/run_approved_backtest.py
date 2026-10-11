#!/usr/bin/env python3
"""Run one approved model on verified MT4 series and external reviewed evidence.

No legacy strategy or benchmark inputs. Profiles and reviewed labels are required;
unknown monetary terms stay unknown while price-only scenario runs are explicit.
"""
import argparse
from bisect import bisect_right
from datetime import datetime,timezone
from decimal import Decimal
import hashlib
import json
from pathlib import Path
from ktrader.mt4_research import MT4ResearchCorpus
from ktrader.approved_models import Bar,Context,dec,luft,trend
from ktrader.approved_scheduler import run_model
from ktrader.level_admission import admit
from ktrader.s1_atr5 import filtered_atr5


def epoch(value):
    return int(datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp()*1000)


def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',required=True)
    parser.add_argument('--evidence',required=True,help='review panels with actual completed independent reviews')
    parser.add_argument('--profile',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--symbol',default='ACHC.us')
    parser.add_argument('--model',choices=['S1','S2A','S2B','S3','S4','S5A','S5B'],default='S1')
    parser.add_argument('--as-of',default='2026-10-07T00:00:00')
    args=parser.parse_args(argv)
    source=Path(args.root).resolve(strict=True);output=Path(args.output).resolve(strict=True)
    if source==output or source in output.parents or output in source.parents:
        raise ValueError('source/results overlap')
    profile=json.loads(Path(args.profile).read_text())
    panels=json.loads(Path(args.evidence).read_text())
    required=('point','tick_size','provenance','historical_price_geometry_verified','level_universe_reviewed')
    missing=[k for k in required if not profile.get(k)]
    if missing:
        print(json.dumps({'status':'BLOCKED_PROFILE','missing':missing,'market_trades':None}));return 2
    if profile.get('broker_symbol')!=args.symbol:
        raise ValueError('symbol profile mismatch')
    corpus=MT4ResearchCorpus(source,wall_clock_mode=True)
    candles={tf:list(corpus.iter_closed(args.symbol,tf,as_of=args.as_of)) for tf in ('D1','H1','M5')}
    hashes={tf:corpus.series[(args.symbol,tf)]['normalized_sha256'] for tf in candles}
    from ktrader.s1_equity_level_rows import completed_daily,completed_weekly
    rows={'D1':completed_daily(candles['D1']),'W1':completed_weekly(candles['D1'])}
    cutoff=epoch(args.as_of)
    accepted=[];blocked=[]
    for panel in panels:
        candidate=panel['candidate']
        review=panel.get('review')
        # Panels prepared by the audit have an incomplete template, not approval.
        if review and not review.get('evidence_id'):
            review={**review,'evidence_id':panel['evidence_id'],'source_sha256':panel['source_sha256']}
        decision=admit(candidate,review,rows[candidate['timeframe']],as_of_ms=cutoff,
                       tick=profile['tick_size'],source_hash=hashes['D1'])
        if decision.admitted:
            accepted.append((candidate,review,decision))
        else:
            blocked.append({'id':decision.evidence_id,'reasons':decision.reasons})
    if not accepted:
        result={'status':'BLOCKED_LEVEL_ADMISSION','market_trades':None,'blocked':blocked}
        (output/'backtest_gate.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
        print(json.dumps(result));return 2
    unique={}
    for c,r,a in sorted(accepted,key=lambda x:x[2].available_at_ms):
        unique.setdefault((c['price'],c['side']),(c,r,a))
    accepted=list(unique.values())
    times={tf:[epoch(b['close_time']) for b in values] for tf,values in candles.items()}
    records=[]
    for candidate,review,admission in accepted:
        first_index=next((i for i,b in enumerate(candles['M5']) if epoch(b['open_time'])>=admission.available_at_ms and i>=21),None)
        if first_index is None:
            continue
        level=dec(candidate['price'])
        side=1 if candidate['side']=='SUPPORT' else -1
        if args.model in ('S2A','S2B','S3'):
            side=-side
        cache={}
        def context_at(index,history):
            actual_index=first_index+index
            now=epoch(candles['M5'][actual_index]['open_time'])
            # S1 approach precedes BPU1. S3 initial approach is retained by scheduler.
            approach_time=epoch(candles['M5'][actual_index-1]['open_time']) if args.model=='S1' else now
            daily_n=bisect_right(times['D1'],now);hourly_n=bisect_right(times['H1'],approach_time)
            d1=candles['D1'][:daily_n]
            if daily_n<5 or len(history)<21:
                return None
            try:
                if daily_n not in cache:
                    cache[daily_n]=(dec(filtered_atr5(d1)),trend([Bar.from_row(b) for b in d1]))
                atr,daily_direction=cache[daily_n]
                approach_daily=trend([Bar.from_row(b) for b in candles['D1'][:bisect_right(times['D1'],approach_time)]])
            except ValueError:
                return None
            decision=admit(candidate,review,rows[candidate['timeframe']],as_of_ms=now,
                           tick=profile['tick_size'],source_hash=hashes['D1'])
            approach_m5=history[:-1] if args.model=='S1' else history
            approach=(approach_daily,trend([Bar.from_row(b) for b in candles['H1'][:hourly_n]]),trend(approach_m5))
            # Target space requires an independently reviewed universe. ATE is
            # never inferred from the maximum of a partial available sample.
            other=[dec(c['price']) for c,r,a in accepted if a.available_at_ms<=now and side*(dec(c['price'])-level)>0]
            breakout_other=[dec(c['price']) for c,r,a in accepted if a.available_at_ms<=now and side*(dec(c['price'])-level)<0]
            space=bool(other) or profile.get('all_time_coverage_verified') is True
            return Context(level,side,luft(level,profile['asset_class'],profile['point']),
                           dec(profile['tick_size']),dec(profile['point']),atr,profile['asset_class'],
                           decision.admitted,decision.admitted,approach,daily_direction,space,
                           forex_stop_points=profile.get('forex_stop_points'),
                           opposing_level=min(other,key=lambda p:abs(p-level)) if other else None,
                           breakout_next_level=min(breakout_other,key=lambda p:abs(p-level)) if breakout_other else None)
        for scenario in ('A','B'):
            replay=run_model([Bar.from_row(b) for b in candles['M5'][first_index:]],args.model,
                             context_at,scenario,seed_history=[Bar.from_row(b) for b in candles['M5'][:first_index]])
            for result in replay:
                records.append({'level_id':admission.evidence_id,'scenario':scenario,**result})
    report={'status':'ALGORITHMIC_SCENARIO_RUN','schema':'ktrader.approved_models.replay.v1',
            'symbol':args.symbol,'model':args.model,'clock':'ALGORITHMIC_WALL_CLOCK',
            'session_accuracy':'NOT_VERIFIED','source_content_sha256':hashes,
            'profile_sha256':hashlib.sha256(Path(args.profile).read_bytes()).hexdigest(),
            'evidence_sha256':hashlib.sha256(Path(args.evidence).read_bytes()).hexdigest(),
            'admitted_levels':len(accepted),'orders':records,'net_results':None,
            'legacy_strategy_used':False,'legacy_benchmarks_used':False,
            'validation_scope':'ENGINEERING_REPLAY_NOT_INDEPENDENT_HOLDOUT'}
    (output/'backtest.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'orders':len(records),'admitted_levels':len(accepted)}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
