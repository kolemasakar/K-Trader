"""Read-only K_AI MT4 JSONL research adapter. No trading interfaces."""
import csv
import json
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

TF = {"D1": "1d", "H1": "1h", "M5": "5m"}

class CorpusError(ValueError):
    pass

def ts(value, broker_timezone=None, *, wall_clock_mode=False):
    d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if d.tzinfo is None:
        if broker_timezone is None and not wall_clock_mode:
            raise CorpusError("opaque broker wall clock requires verified timezone mapping")
        d = d.replace(tzinfo=broker_timezone or timezone.utc)
    return d.astimezone(timezone.utc)

class MT4ResearchCorpus:
    def __init__(self, root, *, verified_broker_timezone=None, wall_clock_mode=False):
        if wall_clock_mode and verified_broker_timezone:
            raise CorpusError("choose either wall-clock or verified timezone mode")
        self.wall_clock_mode = wall_clock_mode
        self.broker_timezone = ZoneInfo(verified_broker_timezone) if verified_broker_timezone else None
        self.root = Path(root).resolve(strict=True)
        manifest = self.root / "full_corpus_series_validation_20261009.csv"
        with manifest.open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        self.series = {}
        for r in rows:
            key = (r["broker_symbol"], r["timeframe"])
            if key in self.series or r["status"] != "PASS":
                raise CorpusError("duplicate/unverified " + str(key))
            self.series[key] = r
        self.paths = {}
        for p in (self.root / "research_max_available" / "normalized").glob("*/*/*.jsonl"):
            with p.open(encoding="utf-8-sig") as f:
                header = json.loads(next(f))
            key = (header.get("broker_symbol"), header.get("mt4_timeframe"))
            if key not in self.series:
                continue
            if p.name != TF[key[1]] + ".jsonl" or key in self.paths:
                raise CorpusError("ambiguous file " + str(key))
            if header.get("provider_id") != "mt4" or header.get("closed_bars_only") is not True:
                raise CorpusError("invalid provenance " + str(key))
            if int(header.get("candle_count", -1)) != int(self.series[key]["candles"]):
                raise CorpusError("header count mismatch " + str(key))
            self.paths[key] = p
        if set(self.paths) != set(self.series):
            raise CorpusError("mapping incomplete")

    def iter_closed(self, symbol, timeframe, *, as_of):
        """Only emit closed candles at/before as_of. In wall_clock_mode, naive MT4 and naive as_of are compared in an artificial common clock, never interpreted as actual UTC."""
        key = (symbol, timeframe)
        if key not in self.paths:
            raise CorpusError("unknown series " + str(key))
        cutoff = ts(as_of, wall_clock_mode=self.wall_clock_mode)
        if self.broker_timezone is None and not self.wall_clock_mode:
            raise CorpusError("broker timezone unknown: cannot safely replay series")
        prev = None
        count = 0
        with self.paths[key].open(encoding="utf-8-sig") as f:
            next(f)  # provenance
            for line in f:
                r = json.loads(line)
                if r.get("record_type") != "candle" or r.get("closed") is not True:
                    raise CorpusError("not a closed candle")
                opened, closed = ts(r["open_time"], self.broker_timezone, wall_clock_mode=self.wall_clock_mode), ts(r["close_time"], self.broker_timezone, wall_clock_mode=self.wall_clock_mode)
                if closed <= opened or (prev is not None and opened <= prev):
                    raise CorpusError("invalid time ordering")
                prev = opened
                if any(not isinstance(r.get(k), (float, int)) for k in ("open","high","low","close")):
                    raise CorpusError("invalid OHLC")
                if r["low"] > min(r["open"],r["close"]) or r["high"] < max(r["open"],r["close"]) or r["low"] > r["high"]:
                    raise CorpusError("invalid OHLC geometry")
                count += 1
                if closed <= cutoff:
                    yield r
        if count != int(self.series[key]["candles"]):
            raise CorpusError("row count mismatch")

    def inventory(self):
        from collections import Counter
        return {"provider_id": "mt4", "series": len(self.series),
                "assets": len({s for s, _ in self.series}),
                "candles": sum(int(r["candles"]) for r in self.series.values()),
                "classes": dict(Counter(r["asset_class"] for r in self.series.values() if r["timeframe"] == "D1"))}
