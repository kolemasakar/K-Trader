#!/usr/bin/env python3
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import math
import pathlib
import statistics
from collections import Counter
from datetime import datetime

DATASET = pathlib.Path('/data/research/phase11g/profile_research_dataset_v0_20260911T204500Z_adaptive')
OUTROOT = pathlib.Path('/data/research/phase11g/profile_baselines_v0')
FEE_BPS = 5.0
SLIPPAGE_BASE_BPS = 2.0
SLIPPAGE_STRESS_BPS = 5.0
TARGET_R = 3.0
BUFFER_ATR = 0.15


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def z(d: datetime) -> str:
    return d.isoformat().replace('+00:00', 'Z')


def sha(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_bars(path: pathlib.Path) -> list[dict]:
    rows = []
    with path.open() as f:
        manifest = json.loads(next(f))
        if manifest.get('record_type') != 'manifest':
            raise RuntimeError(f'missing manifest: {path}')
        for line in f:
            d = json.loads(line)
            rows.append({
                'open_time': d['open_time'],
                'close_time': d['close_time'],
                'open_dt': ts(d['open_time']),
                'close_dt': ts(d['close_time']),
                'open': float(d['open']),
                'high': float(d['high']),
                'low': float(d['low']),
                'close': float(d['close']),
                'quote_volume': float(d.get('quote_volume') or 0.0),
            })
    return rows


def load_funding(path: pathlib.Path) -> list[dict]:
    d = json.loads(path.read_text())
    return [
        {'funding_ms': int(r['fundingTime']), 'rate': float(r['fundingRate']), 'mark': float(r['markPrice'])}
        for r in d.get('records', [])
    ]


def ema(values: list[float], n: int) -> list[float | None]:
    out = [None] * len(values)
    if len(values) < n:
        return out
    alpha = 2.0 / (n + 1.0)
    value = sum(values[:n]) / n
    out[n - 1] = value
    for i in range(n, len(values)):
        value = alpha * values[i] + (1.0 - alpha) * value
        out[i] = value
    return out


def atr_wilder(bars: list[dict], n: int = 14) -> list[float | None]:
    tr = []
    prev = None
    for b in bars:
        x = b['high'] - b['low'] if prev is None else max(
            b['high'] - b['low'], abs(b['high'] - prev), abs(b['low'] - prev)
        )
        tr.append(x)
        prev = b['close']
    out = [None] * len(bars)
    if len(tr) < n:
        return out
    value = sum(tr[:n]) / n
    out[n - 1] = value
    for i in range(n, len(tr)):
        value = (value * (n - 1) + tr[i]) / n
        out[i] = value
    return out


def rsi_wilder(values: list[float], n: int = 14) -> list[float | None]:
    out = [None] * len(values)
    if len(values) <= n:
        return out
    gains, losses = [], []
    for i in range(1, n + 1):
        diff = values[i] - values[i - 1]
        gains.append(max(diff, 0.0)); losses.append(max(-diff, 0.0))
    ag = sum(gains) / n; al = sum(losses) / n
    def calc(g: float, l: float) -> float:
        if l == 0:
            return 100.0 if g > 0 else 50.0
        rs = g / l
        return 100.0 - 100.0 / (1.0 + rs)
    out[n] = calc(ag, al)
    for i in range(n + 1, len(values)):
        diff = values[i] - values[i - 1]
        ag = (ag * (n - 1) + max(diff, 0.0)) / n
        al = (al * (n - 1) + max(-diff, 0.0)) / n
        out[i] = calc(ag, al)
    return out


def indicators(bars: list[dict]) -> dict[str, list]:
    closes = [b['close'] for b in bars]
    return {
        'ema20': ema(closes, 20),
        'ema50': ema(closes, 50),
        'atr14': atr_wilder(bars, 14),
        'rsi14': rsi_wilder(closes, 14),
    }


def latest_closed(close_times: list[datetime], decision_dt: datetime) -> int:
    return bisect.bisect_right(close_times, decision_dt) - 1


def trend_side(bars: list[dict], ind: dict[str, list], k: int) -> int:
    if k < 52 or k - 3 < 0:
        return 0
    e20 = ind['ema20'][k]; e50 = ind['ema50'][k]; old = ind['ema20'][k - 3]
    if None in (e20, e50, old):
        return 0
    if e20 > e50 and e20 > old:
        return 1
    if e20 < e50 and e20 < old:
        return -1
    return 0


def aligned_side(ind: dict[str, list], k: int, side: int) -> bool:
    if k < 49:
        return False
    e20 = ind['ema20'][k]; e50 = ind['ema50'][k]
    if e20 is None or e50 is None:
        return False
    return (side == 1 and e20 > e50) or (side == -1 and e20 < e50)


def adverse(raw: float, side: int, entry: bool, bps: float) -> float:
    s = bps / 10000.0
    if entry:
        return raw * (1 + s) if side == 1 else raw * (1 - s)
    return raw * (1 - s) if side == 1 else raw * (1 + s)


def funding_pct(side: int, entry: float, entry_time: datetime, exit_time: datetime, funding: list[dict]) -> float:
    start = int(entry_time.timestamp() * 1000); end = int(exit_time.timestamp() * 1000)
    total = 0.0
    for row in funding:
        if start <= row['funding_ms'] <= end:
            signed = row['rate'] * row['mark'] / entry
            total += signed if side == 1 else -signed
    return total


def finish(symbol: str, profile: str, pos: dict, exit_i: int, exit_time: datetime, raw_exit: float, reason: str, bps: float, funding: list[dict]) -> dict:
    xp = adverse(raw_exit, pos['side'], False, bps)
    gross = (xp - pos['entry']) / pos['entry'] if pos['side'] == 1 else (pos['entry'] - xp) / pos['entry']
    fee = (FEE_BPS / 10000.0) * (1.0 + xp / pos['entry'])
    fund = funding_pct(pos['side'], pos['entry'], pos['entry_time'], exit_time, funding)
    net = gross - fee - fund
    return {
        'profile': profile,
        'symbol': symbol,
        'side': 'LONG' if pos['side'] == 1 else 'SHORT',
        'entry_time': z(pos['entry_time']), 'exit_time': z(exit_time),
        'entry_price': pos['entry'], 'exit_price': xp,
        'stop_price': pos['stop'], 'target_price': pos['target'],
        'risk_pct': pos['risk_pct'],
        'net_return_pct': net, 'net_R': net / pos['risk_pct'],
        'fee_pct': fee, 'funding_pct': fund,
        'hold_bars': exit_i - pos['entry_i'] + 1,
        'exit_reason': reason,
        'episode_key': pos['episode_key'],
        'features': pos['features'],
    }


def fast_signal(i: int, m5, x5, m15, x15, c15, h1, xh1, ch1, segment_start: datetime):
    if i < 52:
        return None
    dt = m5[i]['close_dt']
    k1 = latest_closed(ch1, dt); k15 = latest_closed(c15, dt)
    if k1 < 52 or k15 < 52:
        return None
    side = trend_side(h1, xh1, k1)
    if side == 0 or not aligned_side(x15, k15, side):
        return None
    pulls = []
    for j in range(max(0, k15 - 2), k15 + 1):
        e = x15['ema20'][j]; r = x15['rsi14'][j]
        if e is None or r is None:
            continue
        if side == 1 and (m15[j]['low'] <= e or r < 45): pulls.append(j)
        if side == -1 and (m15[j]['high'] >= e or r > 55): pulls.append(j)
    if not pulls:
        return None
    episode_j = max(pulls)
    if m15[episode_j]['open_dt'] < segment_start:
        return None
    e20 = x5['ema20'][i]; rsi = x5['rsi14'][i]; atr = x5['atr14'][i]
    if None in (e20, rsi, atr) or atr <= 0:
        return None
    b = m5[i]
    if side == 1:
        trigger = b['close'] > e20 and rsi >= 50 and b['close'] > m5[i-1]['high'] and b['close'] > b['open']
        if not trigger: return None
        stop = min(m5[j]['low'] for j in range(max(0, i - 5), i + 1)) - BUFFER_ATR * atr
    else:
        trigger = b['close'] < e20 and rsi <= 50 and b['close'] < m5[i-1]['low'] and b['close'] < b['open']
        if not trigger: return None
        stop = max(m5[j]['high'] for j in range(max(0, i - 5), i + 1)) + BUFFER_ATR * atr
    return {
        'side': side, 'stop_raw': stop,
        'episode_key': f"{side}:{m15[episode_j]['open_time']}",
        'features': {'h1_index': k1, 'm15_index': k15, 'pullback_open_time': m15[episode_j]['open_time'], 'trigger_atr14': atr, 'trigger_rsi14': rsi},
    }


def swing_signal(i: int, h1, x1, h4, x4, c4, d1, xd1, cd1, segment_start: datetime):
    if i < 52:
        return None
    dt = h1[i]['close_dt']
    kd = latest_closed(cd1, dt); k4 = latest_closed(c4, dt)
    if kd < 52 or k4 < 52:
        return None
    side = trend_side(d1, xd1, kd)
    if side == 0 or not aligned_side(x4, k4, side):
        return None
    pulls = []
    for j in range(max(0, k4 - 3), k4 + 1):
        e = x4['ema20'][j]; r = x4['rsi14'][j]
        if e is None or r is None:
            continue
        if side == 1 and (h4[j]['low'] <= e or r < 45): pulls.append(j)
        if side == -1 and (h4[j]['high'] >= e or r > 55): pulls.append(j)
    if not pulls:
        return None
    episode_j = max(pulls)
    if h4[episode_j]['open_dt'] < segment_start:
        return None
    e20 = x1['ema20'][i]; rsi = x1['rsi14'][i]; atr = x1['atr14'][i]
    if None in (e20, rsi, atr) or atr <= 0:
        return None
    b = h1[i]
    if side == 1:
        trigger = b['close'] > e20 and rsi >= 50 and b['close'] > h1[i-1]['high'] and b['close'] > b['open']
        if not trigger: return None
        stop = min(h1[j]['low'] for j in range(max(0, i - 4), i + 1)) - BUFFER_ATR * atr
    else:
        trigger = b['close'] < e20 and rsi <= 50 and b['close'] < h1[i-1]['low'] and b['close'] < b['open']
        if not trigger: return None
        stop = max(h1[j]['high'] for j in range(max(0, i - 4), i + 1)) + BUFFER_ATR * atr
    return {
        'side': side, 'stop_raw': stop,
        'episode_key': f"{side}:{h4[episode_j]['open_time']}",
        'features': {'d1_index': kd, 'h4_index': k4, 'pullback_open_time': h4[episode_j]['open_time'], 'trigger_atr14': atr, 'trigger_rsi14': rsi},
    }


def backtest_profile(symbol: str, profile: str, bars: dict, funding: list[dict], start: int, end: int, bps: float):
    trigger = bars['5m'] if profile == 'FAST' else bars['1h']
    xtr = indicators(trigger)
    m15 = bars.get('15m'); h1 = bars['1h']; h4 = bars.get('4h'); d1 = bars.get('1d')
    x15 = indicators(m15) if m15 is not None else None
    xh1 = indicators(h1); xh4 = indicators(h4) if h4 is not None else None; xd1 = indicators(d1) if d1 is not None else None
    c15 = [b['close_dt'] for b in m15] if m15 is not None else None
    ch1 = [b['close_dt'] for b in h1]
    ch4 = [b['close_dt'] for b in h4] if h4 is not None else None
    cd1 = [b['close_dt'] for b in d1] if d1 is not None else None
    max_hold = 48 if profile == 'FAST' else 96
    segment_start = trigger[start]['open_dt']
    trades = []; pos = None; pending = None; pending_exit = False; seen = set(); censored = 0
    for i in range(max(1, start - 1), end):
        bar = trigger[i]
        if pos is not None and pending_exit:
            trades.append(finish(symbol, profile, pos, i, bar['open_dt'], bar['open'], 'TIME_EXIT', bps, funding)); pos = None; pending_exit = False
        if pos is None and pending is not None and i >= start:
            side = pending['side']; ep = adverse(bar['open'], side, True, bps); stop = pending['stop_raw']; dist = side * (ep - stop)
            if dist > 0 and pending['episode_key'] not in seen:
                pos = {'side': side, 'entry_i': i, 'entry_time': bar['open_dt'], 'entry': ep, 'stop': stop,
                       'target': ep + side * TARGET_R * dist, 'risk_pct': dist / ep,
                       'episode_key': pending['episode_key'], 'features': pending['features']}
                seen.add(pending['episode_key'])
            pending = None
        if pos is not None:
            side = pos['side']
            gap_stop = (side == 1 and bar['open'] <= pos['stop']) or (side == -1 and bar['open'] >= pos['stop'])
            gap_target = (side == 1 and bar['open'] >= pos['target']) or (side == -1 and bar['open'] <= pos['target'])
            if gap_stop:
                trades.append(finish(symbol, profile, pos, i, bar['open_dt'], bar['open'], 'GAP_STOP', bps, funding)); pos = None
            elif gap_target:
                trades.append(finish(symbol, profile, pos, i, bar['open_dt'], bar['open'], 'GAP_TARGET', bps, funding)); pos = None
            else:
                stop_hit = (side == 1 and bar['low'] <= pos['stop']) or (side == -1 and bar['high'] >= pos['stop'])
                target_hit = (side == 1 and bar['high'] >= pos['target']) or (side == -1 and bar['low'] <= pos['target'])
                if stop_hit:
                    trades.append(finish(symbol, profile, pos, i, bar['close_dt'], pos['stop'], 'STOP', bps, funding)); pos = None
                elif target_hit:
                    trades.append(finish(symbol, profile, pos, i, bar['close_dt'], pos['target'], 'TARGET', bps, funding)); pos = None
        if i >= end - 1:
            continue
        if pos is not None:
            if i - pos['entry_i'] + 1 >= max_hold:
                pending_exit = True
        elif pending is None:
            if profile == 'FAST':
                s = fast_signal(i, trigger, xtr, m15, x15, c15, h1, xh1, ch1, segment_start)
            else:
                s = swing_signal(i, trigger, xtr, h4, xh4, ch4, d1, xd1, cd1, segment_start)
            if s is not None and s['episode_key'] not in seen:
                pending = s
    if pos is not None:
        censored += 1
    return trades, censored


def metrics(trades: list[dict], censored: int) -> dict:
    n = len(trades); rs = [t['net_R'] for t in trades]; wins = [r for r in rs if r > 0]; losses = [r for r in rs if r <= 0]
    gp = sum(wins); gl = -sum(losses)
    running = peak = dd = 0.0
    for t in sorted(trades, key=lambda x: (x['exit_time'], x['symbol'])):
        running += t['net_R']; peak = max(peak, running); dd = max(dd, peak - running)
    by_symbol = Counter(t['symbol'] for t in trades)
    return {
        'completed_trades': n, 'censored_open_positions': censored,
        'wins': len(wins), 'losses': len(losses), 'win_rate': len(wins) / n if n else None,
        'expectancy_R': statistics.fmean(rs) if rs else None,
        'profit_factor_R': gp / gl if gl > 0 else (999.0 if gp > 0 else None),
        'avg_win_R': statistics.fmean(wins) if wins else None,
        'avg_loss_R': statistics.fmean(losses) if losses else None,
        'max_drawdown_R_trade_stream': dd,
        'median_hold_bars': statistics.median([t['hold_bars'] for t in trades]) if trades else None,
        'median_risk_pct': statistics.median([t['risk_pct'] for t in trades]) if trades else None,
        'fee_pct_sum': sum(t['fee_pct'] for t in trades),
        'funding_pct_sum': sum(t['funding_pct'] for t in trades),
        'long_count': sum(t['side'] == 'LONG' for t in trades),
        'short_count': sum(t['side'] == 'SHORT' for t in trades),
        'top_symbol_trade_share': max(by_symbol.values()) / n if n else None,
        'per_symbol_trade_count': dict(sorted(by_symbol.items())),
    }


def segment_bounds(n: int, segment: str) -> tuple[int, int]:
    d = int(math.floor(n * 0.60)); v = int(math.floor(n * 0.80))
    if segment == 'development': return 0, d
    if segment == 'validation': return d, v
    if segment == 'non_holdout': return 0, v
    raise ValueError(segment)


def run_profile(profile: str, dataset: pathlib.Path, bps: float, segment: str):
    bundle_root = dataset / 'bundles'; funding_root = dataset / 'funding'
    all_trades = []; censored = 0
    symbols = sorted(p.name for p in bundle_root.iterdir() if p.is_dir())
    required = ('5m','15m','1h') if profile == 'FAST' else ('1h','4h','1d')
    for symbol in symbols:
        bars = {tf: load_bars(bundle_root / symbol / f'{tf}.jsonl') for tf in required}
        funding = load_funding(funding_root / f'{symbol}.json')
        trigger = bars['5m'] if profile == 'FAST' else bars['1h']
        a, zed = segment_bounds(len(trigger), segment)
        trades, c = backtest_profile(symbol, profile, bars, funding, a, zed, bps)
        all_trades.extend(trades); censored += c
    return metrics(all_trades, censored), all_trades


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dataset', default=str(DATASET))
    ap.add_argument('--output', default=str(OUTROOT))
    args = ap.parse_args()
    dataset = pathlib.Path(args.dataset); outroot = pathlib.Path(args.output); outroot.mkdir(parents=True, exist_ok=True)
    report = {
        'schema_version': 'ktrader.profile_baselines_fast_swing_v0',
        'research_only': True, 'production_approved': False, 'holdout_opened': False,
        'dataset_root': str(dataset), 'dataset_summary_sha256': sha(dataset / 'dataset_summary.json'),
        'funding_summary_sha256': sha(dataset / 'funding_summary.json'),
        'parameters': {'target_R': TARGET_R, 'fee_bps_per_side': FEE_BPS, 'slippage_base_bps': SLIPPAGE_BASE_BPS, 'slippage_stress_bps': SLIPPAGE_STRESS_BPS,
                       'FAST_max_hold_bars_M5': 48, 'SWING_max_hold_bars_H1': 96, 'buffer_atr': BUFFER_ATR},
        'profiles': {},
    }
    for profile in ('FAST','SWING'):
        pdir = outroot / profile.lower(); pdir.mkdir(parents=True, exist_ok=True)
        profile_report = {'segments': {}}
        for segment in ('development','validation','non_holdout'):
            m, trades = run_profile(profile, dataset, SLIPPAGE_BASE_BPS, segment)
            profile_report['segments'][segment] = m
            with (pdir / f'{segment}_trades.jsonl').open('w') as f:
                for row in sorted(trades, key=lambda r: (r['entry_time'], r['symbol'])):
                    f.write(json.dumps(row, sort_keys=True) + '\n')
        stress, _ = run_profile(profile, dataset, SLIPPAGE_STRESS_BPS, 'non_holdout')
        profile_report['stress_non_holdout'] = stress
        profile_report['interpretation_status'] = 'BASELINE_ONLY_NOT_PROMOTION_EVIDENCE'
        report['profiles'][profile] = profile_report
    path = outroot / 'report.json'; path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report, indent=2, sort_keys=True))
    print('REPORT', path, sha(path))


if __name__ == '__main__':
    main()
