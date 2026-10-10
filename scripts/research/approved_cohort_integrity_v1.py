"""Read-only archive integrity audit and causal complete-week reconstruction.

Run in an approved K-Trader research environment. No AI_Trading_System access.
"""
import argparse
import hashlib
import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

DAY_MS=86400000

def verify_manifest(cohort):
    cohort=Path(cohort)
    manifest=json.loads((cohort/"manifest.json").read_text())
    result=[]
    for row in manifest["rows"]:
        rel=Path(row["relative_path"])
        if rel.is_absolute() or ".." in rel.parts:
            raise ValueError("unsafe manifest path")
        path=cohort/rel
        if not path.is_file():
            result.append({"file":str(rel),"status":"MISSING"})
            continue
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        result.append({"file":str(rel),"status":"PASS" if digest==row["sha256"] else "HASH_MISMATCH",
                       "actual_sha256":digest,"expected_sha256":row["sha256"]})
    return result

def full_weeks_from_daily(rows):
    """Aggregate only 7 consecutive UTC daily bars Monday-Sunday.

    Weekly bar is available only after the Sunday daily close.
    """
    by_week=defaultdict(list)
    for x in rows:
        day=datetime.fromtimestamp(int(x[0])/1000,tz=timezone.utc)
        if day.hour or day.minute or day.second or day.microsecond:
            raise ValueError("daily bar not aligned to UTC midnight")
        monday=(day-timedelta(days=day.weekday())).date()
        by_week[monday].append(x)
    result=[]
    for monday,items in sorted(by_week.items()):
        items.sort(key=lambda x:int(x[0]))
        dates=[datetime.fromtimestamp(int(x[0])/1000,tz=timezone.utc).date() for x in items]
        expected=[monday+timedelta(days=i) for i in range(7)]
        if dates!=expected:continue
        result.append([int(items[0][0]),str(items[0][1]),
                       str(max(float(x[2]) for x in items)),
                       str(min(float(x[3]) for x in items)),
                       str(items[-1][4]),str(sum(float(x[5]) for x in items)),
                       int(items[-1][6])])
    return result

def audit(cohort):
    checks=verify_manifest(cohort)
    manifest=json.loads((Path(cohort)/"manifest.json").read_text())
    symbols=manifest["symbols"]
    weekly={}
    for sym in symbols:
        path=Path(cohort)/"bundles"/sym/"1d.jsonl"
        if not path.exists():
            weekly[sym]={"status":"MISSING_DAILY"};continue
        rows=[json.loads(s) for s in path.read_text().splitlines() if s.strip()]
        if any(int(a[0])>=int(b[0]) or int(a[6])>=int(b[0]) for a,b in zip(rows,rows[1:])):
            weekly[sym]={"status":"INVALID_DAILY_ORDER"};continue
        w=full_weeks_from_daily(rows)
        weekly[sym]={"status":"PASS","full_week_count":len(w),
                     "first_week_open_ms":w[0][0] if w else None,
                     "last_week_close_ms":w[-1][6] if w else None}
    return {"status":"PASS" if checks and all(x["status"]=="PASS" for x in checks)
            and all(x["status"]=="PASS" for x in weekly.values()) else "FAIL",
            "file_checks":checks,"causal_weekly":weekly,
            "note":"Only integrity and weekly construction, not a level or trade backtest"}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--cohort",required=True)
    p.add_argument("--output",required=True)
    a=p.parse_args()
    result=audit(a.cohort)
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"files":len(result["file_checks"]),
                      "weekly":result["causal_weekly"],"output":str(out)}))
    if result["status"]!="PASS":raise SystemExit(1)
