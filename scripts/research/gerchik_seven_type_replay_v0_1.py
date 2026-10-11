"""Read-only full research replay. Run as python -m scripts.research.<module>."""
import argparse
import hashlib
import json
from collections import Counter
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

from .gerchik_cohort_readiness_v0_1 import rebuild_closed_weeks
from .gerchik_methodology_audit_v0_1 import witness_check
from .gerchik_seven_types_v0_1 import ResearchPolicy, detect_all, provisional_rating


def verify_previous(rows, candidate):
    p = Decimal(candidate['price'])
    field = 2 if candidate['side'] == 'RESISTANCE' else 3
    source = next((j for j,r in enumerate(rows) if r[0] == candidate['source_open_ms']), None)
    end = candidate['confirmation_index']
    if source is None or not source < end < len(rows):
        return dict(status='REJECTED', reason='MISSING_OR_INVALID_SOURCE')
    checks = dict(exact_origin=Decimal(rows[source][field]) == p,
                  exact_confirmation=Decimal(rows[end][field]) == p,
                  causal_availability=rows[end][6]+1 == candidate['known_at_ms'],
                  at_least_three_inside_bars=end-source-1 >= 3,
                  strictly_one_sided=all(Decimal(r[field]) < p if field == 2
                                        else Decimal(r[field]) > p for r in rows[source+1:end]),
                  saved_witness_matches=rows[source:end+1] == candidate['formation_bars'],
                  confirmation_close_defends=Decimal(rows[end][4]) < p if field == 2
                                            else Decimal(rows[end][4]) > p)
    return dict(status='AUTOMATED_PATTERN_PASS' if all(checks.values()) else 'REJECTED',
                checks=checks, historical_tick='PENDING', independent_review='PENDING')


def replay(root, policy, previous, *, start_ms, end_ms):
    root = Path(root)
    manifest_bytes = (root/'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    report = dict(schema='ktrader.gerchik_seven_type_replay.v0.1',
                  source_manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
                  interval_start_ms=start_ms, interval_end_exclusive_ms=end_ms,
                  policy=asdict(policy), policy_status='ENGINEERING_CANDIDATE_NOT_APPROVED',
                  series=[], levels=[], previous_candidates=[],
                  prefix_checks=0, prefix_failures=0, independently_confirmed_levels=0,
                  strategies='AWAITING_OWNER_AGREEMENT_AND_APPROVAL_NO_TESTS_RUN',
                  production_changed=False, orders_executed=False)
    expected_hash = {(r['symbol'],r['interval']):r['sha256'] for r in manifest['rows']}
    for symbol in manifest['symbols']:
        raw = (root/'bundles'/symbol/'1d.jsonl').read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        if digest != expected_hash[(symbol,'1d')]:
            raise ValueError('D1 source hash mismatch: '+symbol)
        daily = [json.loads(line) for line in raw.splitlines() if line.strip()]
        if not daily or daily[0][0] != start_ms or daily[-1][6]+1 != end_ms:
            raise ValueError('unexpected coverage: '+symbol)
        weekly = rebuild_closed_weeks(daily, end_exclusive_ms=end_ms)
        data = {'D1':daily, 'W1':weekly}
        all_levels = []
        for tf, rows in data.items():
            levels = detect_all(rows, tf, policy)
            for n in range(1,len(rows)+1):
                cutoff = rows[n-1][6]+1
                expected = []
                for x in levels:
                    if x['known_at_ms'] <= cutoff:
                        y = dict(x)
                        y['additional_patterns'] = [e for e in x['additional_patterns']
                                                    if e['known_at_ms'] <= cutoff]
                        expected.append(y)
                if detect_all(rows[:n], tf, policy) != expected:
                    report['prefix_failures'] += 1
                report['prefix_checks'] += 1
            serialized = '\n'.join(json.dumps(r, separators=(',',':')) for r in rows)+'\n'
            report['series'].append(dict(symbol=symbol,timeframe=tf,bars=len(rows),
                                         d1_sha256=digest, series_sha256=hashlib.sha256(serialized.encode()).hexdigest(),
                                         counts=dict(Counter(x['primary_type'] for x in levels))))
            for x in levels:
                x = dict(x, symbol=symbol)
                x['source_bar_id'] = tf+':'+str(x['source_open_ms'])
                x['witness_bars'] = [rows[j] for j in x['witness_indices']]
                x['secondary_witness_audit'] = witness_check(rows, x, asdict(policy))
                x['first_close_beyond_ms'] = next((r[6]+1 for r in rows
                    if r[0] >= x['known_at_ms'] and
                    (Decimal(r[4]) > Decimal(x['price']) if x['side'] == 'RESISTANCE'
                     else Decimal(r[4]) < Decimal(x['price']))), None)
                x['first_limit_penetration_ms'] = next((r[6]+1 for r in rows
                    if x['primary_type']=='LIMIT' and r[0]>=x['known_at_ms'] and
                    (Decimal(r[2])>Decimal(x['price']) if x['side']=='RESISTANCE'
                     else Decimal(r[3])<Decimal(x['price']))), None)
                all_levels.append(x)
        for x in all_levels:
            x['rating_at_birth'] = provisional_rating(data[x['timeframe']], x, all_levels,
                                                      as_of_ms=x['known_at_ms'])
            x['rating_at_end'] = provisional_rating(data[x['timeframe']], x, all_levels,
                                                    as_of_ms=end_ms)
            moments = {x['known_at_ms'], end_ms}
            moments.update(e['known_at_ms'] for e in x['rating_at_end'].get('events',[]))
            moments.update(y['known_at_ms'] for y in all_levels
                           if y['timeframe'] != x['timeframe']
                           and Decimal(y['price']) == Decimal(x['price'])
                           and x['known_at_ms'] <= y['known_at_ms'] <= end_ms)
            if x['first_close_beyond_ms'] is not None:
                moments.add(x['first_close_beyond_ms'])
            x['rating_history'] = []
            for moment in sorted(moments):
                score = provisional_rating(data[x['timeframe']],x,all_levels,as_of_ms=moment)
                x['rating_history'].append(dict(as_of_ms=moment,
                    provisional_score=score['provisional_score'],
                    diagnostic_score_before_close_beyond=score.get('diagnostic_score_before_close_beyond'),
                    counts=score.get('counts',{})))
            report['levels'].append(x)
        for old in previous.get('candidates',[]):
            if old['symbol'] != symbol:
                continue
            checked = verify_previous(data[old['timeframe']], old)
            proposal = dict(old, source_index=next(j for j,r in enumerate(data[old['timeframe']])
                                                   if r[0] == old['source_open_ms']))
            report['previous_candidates'].append(dict(symbol=symbol,timeframe=old['timeframe'],
                price=old['price'],known_at_ms=old['known_at_ms'],verification=checked,
                immutable_original_primary_type=old['primary_type'],
                original_rating_at_birth=provisional_rating(data[old['timeframe']],proposal,all_levels,
                                                            as_of_ms=old['known_at_ms']),
                original_rating_at_end=provisional_rating(data[old['timeframe']],proposal,all_levels,
                                                          as_of_ms=end_ms),
                new_model_primary=[dict(primary_type=x['primary_type'],known_at_ms=x['known_at_ms'])
                                   for x in all_levels if x['timeframe']==old['timeframe']
                                   and Decimal(x['price'])==Decimal(old['price'])]))
    if report['prefix_failures']:
        raise ValueError('causality regression: '+str(report['prefix_failures']))
    report['counts'] = dict(Counter(x['primary_type'] for x in report['levels']))
    report['previous_automated_pass'] = sum(x['verification']['status']=='AUTOMATED_PATTERN_PASS'
                                          for x in report['previous_candidates'])
    report['secondary_witness_counts'] = dict(Counter(x['secondary_witness_audit']['status'] for x in report['levels']))
    report['methodology_acceptance'] = 'ENGINEERING_CHECKS_COMPLETE_FOR_STRATEGY_DESIGN_ONLY' if all(x['secondary_witness_audit']['status']=='SECOND_IMPLEMENTATION_PASS' for x in report['levels']) else 'AUDIT_FAILED'
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-root',required=True)
    parser.add_argument('--policy',required=True)
    parser.add_argument('--previous-report',required=True)
    parser.add_argument('--start-ms',required=True,type=int)
    parser.add_argument('--end-ms',required=True,type=int)
    args = parser.parse_args()
    policy = ResearchPolicy(**json.loads(Path(args.policy).read_text()))
    previous = json.loads(Path(args.previous_report).read_text())
    result = replay(args.data_root,policy,previous,start_ms=args.start_ms,end_ms=args.end_ms)
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
