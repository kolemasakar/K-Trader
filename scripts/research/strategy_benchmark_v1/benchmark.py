#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
import statistics
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/research/phase11g/strategy_benchmark_v1")
TFS = ("5m", "15m", "1h")
SLIPPAGE_BPS = {"low": 0.5, "base": 2.0, "stress": 5.0}
FEE_BPS = 5.0


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bars(path: Path) -> list[dict]:
    rows = []
    with path.open() as f:
        next(f)
        for line in f:
            d = json.loads(line)
            rows.append(
                {
                    "open_time": d["open_time"],
                    "close_time": d["close_time"],
                    "open_dt": parse_ts(d["open_time"]),
                    "close_dt": parse_ts(d["close_time"]),
                    "open": float(d["open"]),
                    "high": float(d["high"]),
                    "low": float(d["low"]),
                    "close": float(d["close"]),
                    "quote_volume": float(d.get("quote_volume") or 0.0),
                }
            )
    return rows


def load_funding(path: Path) -> list[dict]:
    d = json.loads(path.read_text())
    out = []
    for r in d["records"]:
        out.append(
            {
                "funding_ms": int(r["fundingTime"]),
                "rate": float(r["fundingRate"]),
                "mark": float(r["markPrice"]),
            }
        )
    return out


def sma(values: list[float], n: int) -> list[float | None]:
    out = [None] * len(values)
    s = 0.0
    for i, v in enumerate(values):
        s += v
        if i >= n:
            s -= values[i - n]
        if i >= n - 1:
            out[i] = s / n
    return out


def prior_sma(values: list[float], n: int) -> list[float | None]:
    out = [None] * len(values)
    s = 0.0
    for i, v in enumerate(values):
        if i > 0:
            s += values[i - 1]
        if i > n:
            s -= values[i - n - 1]
        if i >= n:
            out[i] = s / n
    return out


def rolling_std(values: list[float], n: int) -> list[float | None]:
    out = [None] * len(values)
    for i in range(n - 1, len(values)):
        w = values[i - n + 1 : i + 1]
        m = sum(w) / n
        out[i] = math.sqrt(sum((x - m) ** 2 for x in w) / n)
    return out


def prior_high(values: list[float], n: int) -> list[float | None]:
    out = [None] * len(values)
    for i in range(n, len(values)):
        out[i] = max(values[i - n : i])
    return out


def prior_low(values: list[float], n: int) -> list[float | None]:
    out = [None] * len(values)
    for i in range(n, len(values)):
        out[i] = min(values[i - n : i])
    return out


def atr_wilder(bars: list[dict], n: int = 14) -> list[float | None]:
    tr = []
    prev = None
    for b in bars:
        if prev is None:
            x = b["high"] - b["low"]
        else:
            x = max(b["high"] - b["low"], abs(b["high"] - prev), abs(b["low"] - prev))
        tr.append(x)
        prev = b["close"]
    out = [None] * len(bars)
    if len(tr) < n:
        return out
    a = sum(tr[:n]) / n
    out[n - 1] = a
    for i in range(n, len(tr)):
        a = (a * (n - 1) + tr[i]) / n
        out[i] = a
    return out


def rsi_wilder(closes: list[float], n: int = 14) -> list[float | None]:
    out = [None] * len(closes)
    if len(closes) <= n:
        return out
    gains = []
    losses = []
    for i in range(1, n + 1):
        d = closes[i] - closes[i - 1]
        gains.append(max(d, 0.0))
        losses.append(max(-d, 0.0))
    avg_gain = sum(gains) / n
    avg_loss = sum(losses) / n

    def calc(g: float, l: float) -> float:
        if l == 0:
            return 100.0 if g > 0 else 50.0
        rs = g / l
        return 100.0 - 100.0 / (1.0 + rs)

    out[n] = calc(avg_gain, avg_loss)
    for i in range(n + 1, len(closes)):
        d = closes[i] - closes[i - 1]
        gain = max(d, 0.0)
        loss = max(-d, 0.0)
        avg_gain = (avg_gain * (n - 1) + gain) / n
        avg_loss = (avg_loss * (n - 1) + loss) / n
        out[i] = calc(avg_gain, avg_loss)
    return out


def build_indicators(bars: list[dict]) -> dict:
    c = [b["close"] for b in bars]
    h = [b["high"] for b in bars]
    l = [b["low"] for b in bars]
    q = [b["quote_volume"] for b in bars]
    s20 = sma(c, 20)
    sd20 = rolling_std(c, 20)
    upper = [None if s20[i] is None else s20[i] + 2.0 * sd20[i] for i in range(len(c))]
    lower = [None if s20[i] is None else s20[i] - 2.0 * sd20[i] for i in range(len(c))]
    roc20 = [None] * len(c)
    for i in range(20, len(c)):
        roc20[i] = c[i] / c[i - 20] - 1.0 if c[i - 20] != 0 else None
    return {
        "sma10": sma(c, 10),
        "sma20": s20,
        "sma30": sma(c, 30),
        "sma50": sma(c, 50),
        "atr14": atr_wilder(bars, 14),
        "rsi14": rsi_wilder(c, 14),
        "roc20": roc20,
        "hi20": prior_high(h, 20),
        "lo20": prior_low(l, 20),
        "hi10": prior_high(h, 10),
        "lo10": prior_low(l, 10),
        "qv20prev": prior_sma(q, 20),
        "bb_upper": upper,
        "bb_lower": lower,
    }


def cross_up(a0, b0, a1, b1) -> bool:
    return None not in (a0, b0, a1, b1) and a0 <= b0 and a1 > b1


def cross_down(a0, b0, a1, b1) -> bool:
    return None not in (a0, b0, a1, b1) and a0 >= b0 and a1 < b1


def entry_signal(strategy: str, i: int, bars: list[dict], x: dict) -> int:
    if i < 1:
        return 0
    c0 = bars[i - 1]["close"]
    c1 = bars[i]["close"]
    if strategy == "vma20_cross_v1":
        if cross_up(c0, x["sma20"][i - 1], c1, x["sma20"][i]):
            return 1
        if cross_down(c0, x["sma20"][i - 1], c1, x["sma20"][i]):
            return -1
    elif strategy == "sma10_30_cross_v1":
        if cross_up(x["sma10"][i - 1], x["sma30"][i - 1], x["sma10"][i], x["sma30"][i]):
            return 1
        if cross_down(x["sma10"][i - 1], x["sma30"][i - 1], x["sma10"][i], x["sma30"][i]):
            return -1
    elif strategy == "roc20_zero_cross_v1":
        if x["roc20"][i - 1] is not None and x["roc20"][i] is not None:
            if x["roc20"][i - 1] <= 0 < x["roc20"][i]:
                return 1
            if x["roc20"][i - 1] >= 0 > x["roc20"][i]:
                return -1
    elif strategy in ("donchian20_10_v1", "donchian20_10_volume_v1"):
        if x["hi20"][i] is not None and c1 > x["hi20"][i]:
            if strategy == "donchian20_10_volume_v1":
                qv = x["qv20prev"][i]
                if qv is None or bars[i]["quote_volume"] <= 1.2 * qv:
                    return 0
            return 1
        if x["lo20"][i] is not None and c1 < x["lo20"][i]:
            if strategy == "donchian20_10_volume_v1":
                qv = x["qv20prev"][i]
                if qv is None or bars[i]["quote_volume"] <= 1.2 * qv:
                    return 0
            return -1
    elif strategy == "bb20_2_reentry_v1":
        if None not in (x["bb_lower"][i - 1], x["bb_lower"][i]) and c0 < x["bb_lower"][i - 1] and c1 >= x["bb_lower"][i]:
            return 1
        if None not in (x["bb_upper"][i - 1], x["bb_upper"][i]) and c0 > x["bb_upper"][i - 1] and c1 <= x["bb_upper"][i]:
            return -1
    elif strategy in ("rsi14_reentry_v1", "rsi14_reentry_sma50_v1"):
        r0, r1 = x["rsi14"][i - 1], x["rsi14"][i]
        if r0 is not None and r1 is not None:
            if r0 < 30 <= r1:
                if strategy == "rsi14_reentry_sma50_v1" and (x["sma50"][i] is None or c1 <= x["sma50"][i]):
                    return 0
                return 1
            if r0 > 70 >= r1:
                if strategy == "rsi14_reentry_sma50_v1" and (x["sma50"][i] is None or c1 >= x["sma50"][i]):
                    return 0
                return -1
    elif strategy == "sma20_50_pullback_v1":
        if None not in (x["sma20"][i - 1], x["sma20"][i], x["sma50"][i]):
            if x["sma20"][i] > x["sma50"][i] and c0 > x["sma20"][i - 1] and bars[i]["low"] <= x["sma20"][i] and c1 > x["sma20"][i]:
                return 1
            if x["sma20"][i] < x["sma50"][i] and c0 < x["sma20"][i - 1] and bars[i]["high"] >= x["sma20"][i] and c1 < x["sma20"][i]:
                return -1
    return 0


def exit_signal(strategy: str, side: int, i: int, bars: list[dict], x: dict) -> tuple[bool, int]:
    sig = entry_signal(strategy, i, bars, x)
    if strategy in ("vma20_cross_v1", "sma10_30_cross_v1", "roc20_zero_cross_v1"):
        if sig == -side:
            return True, sig
        return False, 0
    if strategy in ("donchian20_10_v1", "donchian20_10_volume_v1"):
        if side == 1 and x["lo10"][i] is not None and bars[i]["close"] < x["lo10"][i]:
            return True, 0
        if side == -1 and x["hi10"][i] is not None and bars[i]["close"] > x["hi10"][i]:
            return True, 0
    elif strategy == "bb20_2_reentry_v1":
        if x["sma20"][i] is not None:
            if side == 1 and bars[i]["close"] >= x["sma20"][i]:
                return True, 0
            if side == -1 and bars[i]["close"] <= x["sma20"][i]:
                return True, 0
    elif strategy in ("rsi14_reentry_v1", "rsi14_reentry_sma50_v1"):
        r = x["rsi14"][i]
        if r is not None and ((side == 1 and r >= 50) or (side == -1 and r <= 50)):
            return True, 0
        if strategy == "rsi14_reentry_sma50_v1" and x["sma50"][i] is not None:
            if side == 1 and bars[i]["close"] <= x["sma50"][i]:
                return True, 0
            if side == -1 and bars[i]["close"] >= x["sma50"][i]:
                return True, 0
    elif strategy == "sma20_50_pullback_v1":
        if None not in (x["sma20"][i], x["sma50"][i]):
            if side == 1 and x["sma20"][i] <= x["sma50"][i]:
                return True, 0
            if side == -1 and x["sma20"][i] >= x["sma50"][i]:
                return True, 0
    return False, 0


def adverse_price(raw: float, side: int, is_entry: bool, slip_bps: float) -> float:
    s = slip_bps / 10000.0
    if is_entry:
        return raw * (1.0 + s) if side == 1 else raw * (1.0 - s)
    return raw * (1.0 - s) if side == 1 else raw * (1.0 + s)


@dataclass
class Position:
    side: int
    entry_idx: int
    entry_time: datetime
    entry_price: float
    stop: float
    target: float | None
    risk_pct: float


def funding_cost_pct(side: int, entry_price: float, entry_time: datetime, exit_time: datetime, funding: list[dict]) -> float:
    start_ms = int(entry_time.timestamp() * 1000)
    end_ms = int(exit_time.timestamp() * 1000)
    cost = 0.0
    for r in funding:
        ft = r["funding_ms"]
        if start_ms <= ft <= end_ms:
            signed = r["rate"] * r["mark"] / entry_price
            cost += signed if side == 1 else -signed
    return cost


def finish_trade(symbol: str, tf: str, strategy: str, pos: Position, exit_idx: int, exit_time: datetime, raw_exit: float, reason: str, slip_bps: float, funding: list[dict]) -> dict:
    exit_price = adverse_price(raw_exit, pos.side, False, slip_bps)
    if pos.side == 1:
        gross = (exit_price - pos.entry_price) / pos.entry_price
    else:
        gross = (pos.entry_price - exit_price) / pos.entry_price
    fee = FEE_BPS / 10000.0
    fee_pct = fee * (1.0 + exit_price / pos.entry_price)
    fund_pct = funding_cost_pct(pos.side, pos.entry_price, pos.entry_time, exit_time, funding)
    net = gross - fee_pct - fund_pct
    r_net = net / pos.risk_pct if pos.risk_pct > 0 else 0.0
    return {
        "symbol": symbol,
        "timeframe": tf,
        "strategy_id": strategy,
        "side": "LONG" if pos.side == 1 else "SHORT",
        "entry_idx": pos.entry_idx,
        "exit_idx": exit_idx,
        "entry_time": pos.entry_time.isoformat().replace("+00:00", "Z"),
        "exit_time": exit_time.isoformat().replace("+00:00", "Z"),
        "entry_price": pos.entry_price,
        "exit_price": exit_price,
        "stop_price": pos.stop,
        "target_price": pos.target,
        "gross_return_pct": gross,
        "fee_pct": fee_pct,
        "funding_pct": fund_pct,
        "net_return_pct": net,
        "net_R": r_net,
        "hold_bars": max(0, exit_idx - pos.entry_idx + 1),
        "exit_reason": reason,
    }


def backtest_symbol(symbol: str, tf: str, strategy_cfg: dict, bars: list[dict], funding: list[dict], entry_start: int, end: int, slip_bps: float) -> tuple[list[dict], int]:
    strategy = strategy_cfg["id"]
    if end <= 2 or entry_start >= end:
        return [], 0
    view = bars[:end]
    x = build_indicators(view)
    trades = []
    pos = None
    pending_entry = 0
    pending_exit = False
    pending_reverse = 0
    censored = 0
    signal_start = max(1, entry_start - 1)

    for i in range(signal_start, end):
        b = view[i]

        if pos is not None and pending_exit:
            trades.append(finish_trade(symbol, tf, strategy, pos, i, b["open_dt"], b["open"], "SIGNAL_EXIT", slip_bps, funding))
            pos = None
            pending_exit = False
            if pending_reverse:
                pending_entry = pending_reverse
                pending_reverse = 0

        if pos is None and pending_entry and i >= entry_start:
            atr = x["atr14"][i - 1] if i > 0 else None
            if atr is not None and atr > 0:
                side = pending_entry
                ep = adverse_price(b["open"], side, True, slip_bps)
                dist = float(strategy_cfg["stop_atr"]) * atr
                stop = ep - side * dist
                target = None
                if strategy_cfg.get("target_r") is not None:
                    target = ep + side * float(strategy_cfg["target_r"]) * dist
                pos = Position(side=side, entry_idx=i, entry_time=b["open_dt"], entry_price=ep, stop=stop, target=target, risk_pct=dist / ep)
            pending_entry = 0

        if pos is not None:
            gap_stop = (pos.side == 1 and b["open"] <= pos.stop) or (pos.side == -1 and b["open"] >= pos.stop)
            if gap_stop:
                trades.append(finish_trade(symbol, tf, strategy, pos, i, b["open_dt"], b["open"], "GAP_STOP", slip_bps, funding))
                pos = None
            else:
                stop_hit = (pos.side == 1 and b["low"] <= pos.stop) or (pos.side == -1 and b["high"] >= pos.stop)
                target_hit = False
                if pos.target is not None:
                    target_hit = (pos.side == 1 and b["high"] >= pos.target) or (pos.side == -1 and b["low"] <= pos.target)
                if stop_hit:
                    trades.append(finish_trade(symbol, tf, strategy, pos, i, b["close_dt"], pos.stop, "STOP", slip_bps, funding))
                    pos = None
                elif target_hit:
                    trades.append(finish_trade(symbol, tf, strategy, pos, i, b["close_dt"], pos.target, "TARGET", slip_bps, funding))
                    pos = None

        if i >= end - 1:
            continue

        if pos is not None:
            should_exit, reverse = exit_signal(strategy, pos.side, i, view, x)
            held = i - pos.entry_idx + 1
            if held >= int(strategy_cfg["max_hold_bars"]):
                should_exit = True
                reverse = 0
            if should_exit:
                pending_exit = True
                pending_reverse = reverse
        else:
            sig = entry_signal(strategy, i, view, x)
            if sig:
                pending_entry = sig

    if pos is not None:
        censored += 1
    return trades, censored


def wilson(wins: int, n: int, z: float = 1.959963984540054) -> list[float | None]:
    if n == 0:
        return [None, None]
    p = wins / n
    den = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / den
    half = z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n) / den
    return [max(0.0, center - half), min(1.0, center + half)]


def portfolio_stats(trades: list[dict], symbols: list[str]) -> tuple[float, float]:
    equities = {s: 1.0 for s in symbols}
    peak = 1.0
    max_dd = 0.0
    for t in sorted(trades, key=lambda r: (r["exit_time"], r["symbol"], r["entry_time"])):
        s = t["symbol"]
        equities[s] *= max(0.0, 1.0 + t["net_return_pct"])
        eq = sum(equities.values()) / len(symbols)
        peak = max(peak, eq)
        if peak > 0:
            max_dd = max(max_dd, (peak - eq) / peak)
    final_eq = sum(equities.values()) / len(symbols)
    return final_eq - 1.0, max_dd


def metrics(trades: list[dict], symbols: list[str], censored: int = 0) -> dict:
    n = len(trades)
    wins = sum(1 for t in trades if t["net_return_pct"] > 0)
    losses = n - wins
    positives = sum(t["net_return_pct"] for t in trades if t["net_return_pct"] > 0)
    negatives = -sum(t["net_return_pct"] for t in trades if t["net_return_pct"] < 0)
    pf = positives / negatives if negatives > 0 else (float("inf") if positives > 0 else None)
    rets = [t["net_return_pct"] for t in trades]
    rs = [t["net_R"] for t in trades]
    comp, dd = portfolio_stats(trades, symbols)
    running = 0.0
    peak_r = 0.0
    dd_r = 0.0
    for t in sorted(trades, key=lambda r: (r["exit_time"], r["symbol"], r["entry_time"])):
        running += t["net_R"]
        peak_r = max(peak_r, running)
        dd_r = max(dd_r, peak_r - running)
    by_symbol = collections.Counter(t["symbol"] for t in trades)
    episodes = {(t["timeframe"], t["entry_time"]) for t in trades}
    long_count = sum(1 for t in trades if t["side"] == "LONG")
    fee_total = sum(t["fee_pct"] for t in trades)
    funding_total = sum(t["funding_pct"] for t in trades)
    return {
        "completed_trades": n,
        "censored_open_positions": censored,
        "wins": wins,
        "losses": losses,
        "win_rate": wins / n if n else None,
        "wilson_95_ci": wilson(wins, n),
        "net_expectancy_pct_per_trade": statistics.fmean(rets) if rets else None,
        "expectancy_R": statistics.fmean(rs) if rs else None,
        "profit_factor": pf,
        "net_return_equal_weight_symbols": comp,
        "max_drawdown_pct_equal_weight_symbols": dd,
        "max_drawdown_R_trade_stream": dd_r,
        "largest_win_R": max(rs) if rs else None,
        "largest_loss_R": min(rs) if rs else None,
        "long_short_counts": {"LONG": long_count, "SHORT": n - long_count},
        "median_hold_bars": statistics.median(t["hold_bars"] for t in trades) if trades else None,
        "fee_pct_sum_trade_normalized": fee_total,
        "funding_pct_sum_trade_normalized": funding_total,
        "entry_episode_count": len(episodes),
        "top_symbol_trade_share": max(by_symbol.values()) / n if n and by_symbol else None,
        "per_symbol_trade_count": dict(sorted(by_symbol.items())),
    }


def split_points(n: int) -> tuple[int, int]:
    return int(math.floor(n * 0.60)), int(math.floor(n * 0.80))


def run_segment(strategy_cfg: dict, tf: str, bars_by_symbol: dict, funding_by_symbol: dict, segment: str, slip: str) -> tuple[dict, list[dict]]:
    all_trades = []
    censored = 0
    symbols = sorted(bars_by_symbol)
    for symbol in symbols:
        bars = bars_by_symbol[symbol]
        d, v = split_points(len(bars))
        if segment == "development":
            start, end = 0, d
        elif segment == "validation":
            start, end = d, v
        elif segment == "non_holdout":
            start, end = 0, v
        elif segment.startswith("wf"):
            fold = int(segment[-1])
            start = int(math.floor(len(bars) * (0.20 * fold)))
            end = int(math.floor(len(bars) * (0.20 * (fold + 1))))
        elif segment == "holdout":
            start, end = v, len(bars)
        else:
            raise ValueError(segment)
        tr, c = backtest_symbol(symbol, tf, strategy_cfg, bars, funding_by_symbol[symbol], start, end, SLIPPAGE_BPS[slip])
        all_trades.extend(tr)
        censored += c
    return metrics(all_trades, symbols, censored), all_trades


def survivor(dev: dict, val: dict, combined: dict) -> tuple[bool, list[str]]:
    reasons = []
    if combined["completed_trades"] < 100:
        reasons.append("non_holdout:INSUFFICIENT_SAMPLE")
    if combined["win_rate"] is None or combined["win_rate"] <= 0.60:
        reasons.append("non_holdout:WIN_RATE_LE_60")
    if combined["net_expectancy_pct_per_trade"] is None or combined["net_expectancy_pct_per_trade"] <= 0:
        reasons.append("non_holdout:NONPOSITIVE_EXPECTANCY")
    pf = combined["profit_factor"]
    if pf is None or pf <= 1.0:
        reasons.append("non_holdout:PF_LE_1")
    for label, m in (("development", dev), ("validation", val)):
        if m["win_rate"] is None or m["win_rate"] <= 0.60:
            reasons.append(f"{label}:WIN_RATE_LE_60")
        if m["net_expectancy_pct_per_trade"] is None or m["net_expectancy_pct_per_trade"] <= 0:
            reasons.append(f"{label}:NONPOSITIVE_EXPECTANCY")
        pf = m["profit_factor"]
        if pf is None or pf <= 1.0:
            reasons.append(f"{label}:PF_LE_1")
    return not reasons, reasons


def load_all():
    protocol = json.loads((ROOT / "protocol.json").read_text())
    catalogue = json.loads((ROOT / "strategy_catalogue.json").read_text())
    manifest = json.loads((ROOT / "sources" / "sources_manifest.json").read_text())
    symbols = protocol["primary_panel"]["symbols"]
    bars = {tf: {} for tf in TFS}
    funding = {}
    for symbol in symbols:
        for tf in TFS:
            path = Path(manifest["merged_histories"][symbol][tf]["path"])
            bars[tf][symbol] = load_bars(path)
        funding[symbol] = load_funding(Path(manifest["funding"][symbol]["path"]))
    return protocol, catalogue, manifest, bars, funding


def write_json(path: Path, obj: dict) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, allow_nan=False) + "\n")
    return sha_file(path)


def sanitize_inf(obj):
    if isinstance(obj, dict):
        return {k: sanitize_inf(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize_inf(v) for v in obj]
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    return obj


def discovery():
    protocol, catalogue, manifest, bars, funding = load_all()
    results = []
    trade_root = ROOT / "runs" / "discovery_validation" / "trades"
    for cfg in catalogue["strategies"]:
        for tf in TFS:
            dev_base, dev_trades = run_segment(cfg, tf, bars[tf], funding, "development", "base")
            val_base, val_trades = run_segment(cfg, tf, bars[tf], funding, "validation", "base")
            non_base, _ = run_segment(cfg, tf, bars[tf], funding, "non_holdout", "base")
            low, _ = run_segment(cfg, tf, bars[tf], funding, "non_holdout", "low")
            stress, _ = run_segment(cfg, tf, bars[tf], funding, "non_holdout", "stress")
            folds = []
            for f in (1, 2, 3):
                m, _ = run_segment(cfg, tf, bars[tf], funding, f"wf{f}", "base")
                folds.append({"fold": f, "metrics": m})
            ok, reasons = survivor(dev_base, val_base, non_base)
            trade_file = trade_root / f"{cfg['id']}__{tf}.jsonl"
            trade_file.parent.mkdir(parents=True, exist_ok=True)
            with trade_file.open("w") as out:
                for t in sorted(dev_trades + val_trades, key=lambda r: (r["entry_time"], r["symbol"])):
                    out.write(json.dumps(t, sort_keys=True) + "\n")
            results.append(
                {
                    "strategy_id": cfg["id"],
                    "family": cfg["family"],
                    "components": cfg["components"],
                    "timeframe": tf,
                    "development": dev_base,
                    "validation": val_base,
                    "non_holdout_base": non_base,
                    "non_holdout_low_slippage": low,
                    "non_holdout_stress_slippage": stress,
                    "walk_forward": folds,
                    "survivor": ok,
                    "rejection_reasons": reasons,
                    "trade_ledger_path": str(trade_file),
                    "trade_ledger_sha256": sha_file(trade_file),
                }
            )
    results.sort(
        key=lambda r: (
            not r["survivor"],
            -(r["validation"]["win_rate"] or -1),
            -(r["validation"]["profit_factor"] or -1),
            -(r["validation"]["completed_trades"] or 0),
        )
    )
    survivors = [r for r in results if r["survivor"]]
    report = {
        "schema_version": "ktrader.strategy_benchmark_discovery_validation.v1",
        "holdout_accessed": False,
        "protocol_sha256": sha_file(ROOT / "protocol.json"),
        "strategy_catalogue_sha256": sha_file(ROOT / "strategy_catalogue.json"),
        "sources_manifest_sha256": sha_file(ROOT / "sources" / "sources_manifest.json"),
        "result_count": len(results),
        "survivor_count": len(survivors),
        "results": results,
    }
    report = sanitize_inf(report)
    report_path = ROOT / "runs" / "discovery_validation" / "report.json"
    report_sha = write_json(report_path, report)
    summary = {
        "schema_version": "ktrader.strategy_benchmark_leaderboard.v1",
        "holdout_accessed": False,
        "report_path": str(report_path),
        "report_sha256": report_sha,
        "rows": [
            {
                "strategy_id": r["strategy_id"],
                "timeframe": r["timeframe"],
                "family": r["family"],
                "components": r["components"],
                "survivor": r["survivor"],
                "rejection_reasons": r["rejection_reasons"],
                "development": r["development"],
                "validation": r["validation"],
                "non_holdout_base": r["non_holdout_base"],
                "non_holdout_stress_slippage": r["non_holdout_stress_slippage"],
                "walk_forward": r["walk_forward"],
            }
            for r in results
        ],
    }
    leaderboard_path = ROOT / "summary" / "leaderboard.json"
    leaderboard_sha = write_json(leaderboard_path, sanitize_inf(summary))
    survivor_path = ROOT / "summary" / "survivors_gt60.json"
    survivor_sha = write_json(
        survivor_path,
        {
            "schema_version": "ktrader.strategy_benchmark_survivors.v1",
            "holdout_accessed": False,
            "survivors": [
                {
                    "strategy_id": r["strategy_id"],
                    "timeframe": r["timeframe"],
                    "components": r["components"],
                    "development": r["development"],
                    "validation": r["validation"],
                    "non_holdout_base": r["non_holdout_base"],
                    "non_holdout_stress_slippage": r["non_holdout_stress_slippage"],
                }
                for r in survivors
            ],
        },
    )
    print("DISCOVERY_REPORT", report_path, report_sha)
    print("LEADERBOARD", leaderboard_path, leaderboard_sha)
    print("SURVIVORS", survivor_path, survivor_sha, len(survivors))
    for r in results[:12]:
        v = r["validation"]
        d = r["development"]
        print(
            r["strategy_id"],
            r["timeframe"],
            "SURVIVOR" if r["survivor"] else "REJECT",
            "dev_n", d["completed_trades"],
            "dev_wr", d["win_rate"],
            "val_n", v["completed_trades"],
            "val_wr", v["win_rate"],
            "val_pf", v["profit_factor"],
            "val_exp", v["net_expectancy_pct_per_trade"],
            "reasons", ",".join(r["rejection_reasons"]),
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["discovery"])
    args = parser.parse_args()
    if args.mode == "discovery":
        discovery()


if __name__ == "__main__":
    main()
