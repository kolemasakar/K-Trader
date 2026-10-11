"""Read native K-Trader D1 candles and derive complete UTC W1 candles.

Read-only conversion in memory. Reject incomplete source and partial weeks.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

DAY_MS=86400000

def ms(s):
    return int(datetime.fromisoformat(s.replace("Z","+00:00")).timestamp()*1000)

def native_d1(path):
    bars=[];manifest=None
    for line in Path(path).read_text().splitlines():
        if not line.strip():continue
        r=json.loads(line)
        if r.get("record_type")=="manifest":
            if manifest is not None or bars:raise ValueError("misplaced manifest")
            manifest=r
            if r.get("interval")!="1d":raise ValueError("D1 required")
            continue
        if manifest is None or r.get("record_type")!="candle" or not r.get("closed"):
            raise ValueError("unexpected or unclosed candle")
        b={"t":ms(r["open_time"]),"close_t":ms(r["close_time"]),
           "o":float(r["open"]),"h":float(r["high"]),"l":float(r["low"]),
           "c":float(r["close"]),"v":float(r["volume"])}
        if b["close_t"]!=b["t"]+DAY_MS-1:
            raise ValueError("D1 must be fully closed UTC day")
        if bars and b["t"]!=bars[-1]["t"]+DAY_MS:
            raise ValueError("missing, duplicate or unordered daily bar")
        if b["h"]<max(b["o"],b["c"],b["l"]) or b["l"]>min(b["o"],b["c"]):
            raise ValueError("invalid OHLC")
        bars.append(b)
    if not manifest or len(bars)!=manifest.get("candle_count"):
        raise ValueError("missing manifest or candle count mismatch")
    if bars and (bars[0]["t"]!=ms(manifest["actual_start"])
                 or bars[-1]["close_t"]!=ms(manifest["actual_end"])):
        raise ValueError("manifest time range mismatch")
    return bars

def complete_w1(daily):
    groups={}
    for b in daily:
        dt=datetime.fromtimestamp(b["t"]/1000,timezone.utc)
        monday=(dt-timedelta(days=dt.weekday())).date()
        groups.setdefault(monday,[]).append(b)
    weekly=[]
    for monday,items in sorted(groups.items()):
        if len(items)!=7:continue
        expected=int(datetime(monday.year,monday.month,monday.day,tzinfo=timezone.utc).timestamp()*1000)
        if [x["t"] for x in items]!=[expected+i*DAY_MS for i in range(7)]:
            continue
        weekly.append({"t":items[0]["t"],"close_t":items[-1]["close_t"],
                       "o":items[0]["o"],"h":max(x["h"] for x in items),
                       "l":min(x["l"] for x in items),"c":items[-1]["c"],
                       "v":sum(x["v"] for x in items)})
    return weekly
