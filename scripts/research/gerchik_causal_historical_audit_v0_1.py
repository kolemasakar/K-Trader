"""Research-only as-of audit of exploratory D1/W1 pivots and filtered ATR5.

Pivot counts are NOT independently reviewed Gerchik levels. Never emit signals.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from .native_internal_d1_w1_v1 import native_d1, complete_w1
from .internal_level_structure_diagnostics_v1 import pivots
from .gerchik_filtered_atr5_v1 import DailyBar, filtered_atr5, InsufficientHistory


def audit_symbol(path):
    raw = Path(path).read_bytes()
    daily = native_d1(path)
    weekly = complete_w1(daily)
    if not daily:
        raise ValueError('Empty source')
    events = pivots(daily, '1d') + pivots(weekly, '1w')
    events.sort(key=lambda x: (x['confirmed_close_ms'], x['tf'], x['kind'], x['price']))
    first, last = daily[0]['close_t'], daily[-1]['close_t']
    # Reconstruct every cutoff using ONLY bars available by that cutoff.
    atr_ok = atr_insufficient = 0
    atr_rejections = 0
    for index, bar in enumerate(daily):
        prefix = daily[:index + 1]
        assert all(x['close_t'] <= bar['close_t'] for x in prefix)
        closed = [DailyBar(datetime.fromtimestamp(x['close_t']/1000, timezone.utc).isoformat(),
                           x['h'], x['l']) for x in reversed(prefix)]
        try:
            result = filtered_atr5(closed)
        except InsufficientHistory:
            atr_insufficient += 1
        else:
            atr_ok += 1
            atr_rejections += len(result['rejected'])
            if any(x['timestamp'] > closed[0].timestamp for x in result['accepted']):
                raise ValueError('Future ATR input')
    if atr_ok + atr_insufficient != len(daily):
        raise AssertionError('Missing ATR cutoff')
    if any(e['confirmed_close_ms'] < first or e['confirmed_close_ms'] > last for e in events):
        raise ValueError('Pivot confirmation outside available history')
    # Audit as-of visibility at EVERY D1 close. Weekly events only enter after
    # their complete confirming W1 candle has closed.
    visible = 0
    for bar in daily:
        cutoff = bar['close_t']
        current = [e for e in events if e['confirmed_close_ms'] <= cutoff]
        if len(current) < visible:
            raise AssertionError('As-of pivot visibility decreased')
        visible = len(current)
        if any(e['confirmed_close_ms'] > cutoff for e in current):
            raise AssertionError('Future pivot leak')
    return dict(source_sha256=hashlib.sha256(raw).hexdigest(), d1_bars=len(daily),
                complete_w1_bars=len(weekly), exploratory_d1_pivots=sum(e['tf']=='1d' for e in events),
                exploratory_w1_pivots=sum(e['tf']=='1w' for e in events),
                atr5_valid_cutoffs=atr_ok, atr5_insufficient_cutoffs=atr_insufficient,
                atr5_rejected_bar_occurrences=atr_rejections,
                first_close_ms=first, last_close_ms=last,
                status='CAUSAL_DIAGNOSTIC_NOT_LEVEL_QUALITY_VALIDATION')


def audit_root(root):
    root = Path(root)
    if not root.is_dir():
        raise FileNotFoundError(root)
    results = []
    for path in sorted(root.glob('*/1d.jsonl')):
        try:
            results.append(dict(symbol=path.parent.name, **audit_symbol(path)))
        except (ValueError, KeyError, TypeError, IndexError) as exc:
            results.append(dict(symbol=path.parent.name, status='INVALID_SOURCE', reason=str(exc)))
    if not results:
        raise ValueError('No internal D1 source files')
    return dict(schema='ktrader.gerchik_causal_historical_audit.v0_1',
                status='RESEARCH_ONLY_NOT_STRATEGY_VALIDATED', results=results)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', required=True)
    p.add_argument('--output', required=True)
    a = p.parse_args()
    report = audit_root(a.root)
    dest = Path(a.output)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps(dict(output=str(dest), symbols=len(report['results']),
                          invalid=sum(x['status']=='INVALID_SOURCE' for x in report['results']))))
