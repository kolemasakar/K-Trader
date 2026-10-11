"""Streaming, read-only inventory of a K-Trader Binance kline cohort.

Checks bytes, OHLC, chronology and coverage. No levels, outcomes or holdout
performance are examined. Partial source W1 bars cannot enter level replay.
"""
import argparse
import hashlib
import json
import math
from collections import defaultdict
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from pathlib import Path

INTERVAL_MS = {"5m": 300000, "15m": 900000, "30m": 1800000,
               "1h": 3600000, "4h": 14400000, "1d": 86400000,
               "1w": 604800000}


def inspect_file(path, row, *, end_exclusive_ms=None):
    interval = row["interval"]
    step = INTERVAL_MS[interval]
    digest = hashlib.sha256()
    count = gaps = invalid = partial = 0
    first = last = None
    daily_opens = []
    with path.open("rb") as source:
        for line in source:
            digest.update(line)
            if not line.strip():
                continue
            data = json.loads(line)
            if not isinstance(data, list) or len(data) < 7:
                raise ValueError("Expected raw Binance kline array")
            opened, closed = data[0], data[6]
            if isinstance(opened, bool) or isinstance(closed, bool) or not isinstance(opened, int) or not isinstance(closed, int):
                raise ValueError("Integer exchange timestamps required")
            op, hi, lo, close, vol = [float(data[k]) for k in (1, 2, 3, 4, 5)]
            if not all(math.isfinite(x) for x in (op, hi, lo, close, vol)) or not (0 < lo <= op <= hi and lo <= close <= hi and vol >= 0):
                invalid += 1
            boundary_partial = end_exclusive_ms is not None and closed >= end_exclusive_ms
            if closed < opened or closed + 1 > opened + step:
                invalid += 1
            elif closed + 1 != opened + step or boundary_partial:
                partial += 1
            if end_exclusive_ms is not None and opened >= end_exclusive_ms:
                invalid += 1
            if last is not None and opened - last != step:
                gaps += 1
            if interval == "1w":
                day = datetime.fromtimestamp(opened/1000, timezone.utc)
                if day.weekday() != 0 or day.hour or day.minute or day.second or day.microsecond:
                    invalid += 1
            elif opened % step:
                invalid += 1
            if first is None:
                first = opened
            last = opened
            count += 1
            if interval == "1d" and closed + 1 == opened + step and not boundary_partial:
                daily_opens.append(opened)
    sha = digest.hexdigest()
    matching = sha == row["sha256"] and count == row["bars"]
    matching = matching and first == row["first_open_ms"] and last == row["last_open_ms"]
    status = "FAIL" if not matching or gaps or invalid or (partial and interval != "1w") else (
        "PARTIAL_W1_REBUILD_REQUIRED" if partial else "PASS")
    return dict(symbol=row["symbol"], interval=interval, relative_path=row["relative_path"],
                status=status, sha256=sha, hash_match=sha == row["sha256"],
                bars=count, declared_bars=row["bars"], first_open_ms=first, last_open_ms=last,
                internal_gaps=gaps, invalid_rows=invalid, partial_bars=partial), daily_opens


def complete_week_count(daily_opens):
    days = {datetime.fromtimestamp(x/1000, timezone.utc).date() for x in daily_opens}
    return sum(1 for day in days if day.weekday() == 0 and all(
        day+timedelta(days=offset) in days for offset in range(7)))


def rebuild_closed_weeks(daily_rows, *, end_exclusive_ms):
    """Exact-price derived OHLCV, Monday-Sunday, available only on full close.

    Daily raw fields 0..6 become derived weekly fields 0..6. Remaining raw
    Binance exchange fields are deliberately omitted; this is a derived
    research series with source lineage, not a replacement exchange file.
    """
    groups = defaultdict(list)
    for row in daily_rows:
        opened = row[0]
        if opened % INTERVAL_MS["1d"] or row[6]+1 != opened+INTERVAL_MS["1d"]:
            raise ValueError("Complete UTC-aligned D1 required")
        day = datetime.fromtimestamp(opened/1000, timezone.utc).date()
        monday = day-timedelta(days=day.weekday())
        groups[monday].append(row)
    result = []
    for monday, rows in sorted(groups.items()):
        rows.sort(key=lambda row: row[0])
        start = int(datetime.combine(monday, datetime.min.time(), tzinfo=timezone.utc).timestamp()*1000)
        if [row[0] for row in rows] != [start+offset*INTERVAL_MS["1d"] for offset in range(7)]:
            continue
        if rows[-1][6] >= end_exclusive_ms:
            continue
        result.append([start, rows[0][1], str(max(Decimal(row[2]) for row in rows)),
                       str(min(Decimal(row[3]) for row in rows)), rows[-1][4],
                       str(sum((Decimal(row[5]) for row in rows), Decimal(0))), rows[-1][6]])
    return result


def audit(cohort):
    root = Path(cohort).resolve(strict=True)
    manifest_path = root/"manifest.json"
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    if manifest.get("research_only") is not True or manifest.get("not_first_seen") is not True:
        raise ValueError("Explicit retrospective research-only provenance required")
    rows = manifest["rows"]
    end = datetime.fromisoformat(manifest["requested_end_exclusive_utc"].replace("Z", "+00:00"))
    if end.tzinfo is None:
        raise ValueError("Timezone-aware end boundary required")
    end_ms = int(end.timestamp()*1000)
    expected = {(symbol, interval) for symbol in manifest["symbols"] for interval in manifest["intervals"]}
    identities = [(row["symbol"], row["interval"]) for row in rows]
    if not expected or len(identities) != len(set(identities)) or set(identities) != expected:
        raise ValueError("Complete unique symbol/interval manifest required")
    reports = []
    weeks = {}
    derived = {}
    paths = set()
    for row in rows:
        relative = Path(row["relative_path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe manifest path")
        path = (root/relative).resolve(strict=True)
        if not path.is_relative_to(root) or path in paths:
            raise ValueError("Escaping or duplicate manifest path")
        paths.add(path)
        report, daily = inspect_file(path, row, end_exclusive_ms=end_ms)
        reports.append(report)
        if row["interval"] == "1d" and report["status"] == "PASS":
            weeks[row["symbol"]] = complete_week_count(daily)
            with path.open() as source:
                daily_rows = [json.loads(line) for line in source if line.strip()]
            weekly = rebuild_closed_weeks(daily_rows, end_exclusive_ms=end_ms)
            serialized = "".join(json.dumps(bar, separators=(",", ":"))+"\n" for bar in weekly)
            derived[row["symbol"]] = dict(bars=len(weekly),
                sha256=hashlib.sha256(serialized.encode()).hexdigest(), source_d1_sha256=report["sha256"],
                first_open_ms=weekly[0][0] if weekly else None,
                last_close_ms=weekly[-1][6] if weekly else None,
                schema="DERIVED_OHLCV_7_FIELDS", serialization="compact-json-array-jsonl-utf8")
    partial_w1 = sum(x["partial_bars"] for x in reports if x["interval"] == "1w")
    status = "FAIL" if any(x["status"] == "FAIL" for x in reports) else (
        "PASS_WITH_W1_REBUILD" if partial_w1 else "PASS")
    return dict(schema_version="ktrader.gerchik_cohort_readiness.v0.1", status=status,
                checked_at_utc=datetime.now(timezone.utc).isoformat(),
                source_root=str(root), manifest_sha256=hashlib.sha256(raw).hexdigest(),
                requested_start_utc=manifest["requested_start_utc"],
                requested_end_exclusive_utc=manifest["requested_end_exclusive_utc"],
                symbols=manifest["symbols"], intervals=manifest["intervals"], files=reports,
                total_bars=sum(x["bars"] for x in reports), complete_utc_weeks_from_d1=weeks,
                derived_closed_w1=derived,
                m5_available="5m" in manifest["intervals"],
                scope="INTEGRITY_ONLY_NOT_STRATEGY_OR_LEVEL_VALIDATION",
                holdout_outcomes_accessed=False,
                independent_holdout_status="UNVERIFIED_DO_NOT_ASSUME_UNTOUCHED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cohort", required=True)
    args = parser.parse_args()
    report = audit(args.cohort)
    print(json.dumps(report, sort_keys=True, allow_nan=False))
    raise SystemExit(1 if report["status"] == "FAIL" else 0)
