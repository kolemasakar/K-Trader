"""Read-only inventory of native K-Trader historical expansion bundles.

No external archive, live API, trading, or production mutation.
"""
import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

def millis(value):
    return int(datetime.fromisoformat(value.replace("Z","+00:00")).timestamp()*1000)

def inspect_daily(path):
    sha=hashlib.sha256()
    manifest=None
    count=0
    first=None
    last=None
    previous_close=None
    with path.open("rb") as stream:
        for line in stream:
            sha.update(line)
            if not line.strip():continue
            row=json.loads(line)
            if row.get("record_type")=="manifest":
                if manifest is not None or count:raise ValueError("duplicate/misplaced manifest")
                manifest=row
                if row.get("interval")!="1d":raise ValueError("not D1")
                continue
            if row.get("record_type")!="candle" or manifest is None:
                raise ValueError("unexpected record or missing manifest")
            if not row.get("closed"):raise ValueError("unclosed candle")
            start=millis(row["open_time"]);end=millis(row["close_time"])
            if end<start or (previous_close is not None and start<=previous_close):
                raise ValueError("unordered/overlapping candles")
            if float(row["high"])<float(row["low"]):
                raise ValueError("high below low")
            if first is None:first=start
            last=end;previous_close=end;count+=1
    if manifest is None:raise ValueError("missing manifest")
    if count!=manifest.get("candle_count"):
        raise ValueError("manifest candle count mismatch")
    if first!=millis(manifest["actual_start"]) or last!=millis(manifest["actual_end"]):
        raise ValueError("manifest time range mismatch")
    return {"status":"PASS" if count else "EMPTY","bars":count,
            "first_open_ms":first,"last_close_ms":last,
            "raw_sha256":sha.hexdigest(),"provider_id":manifest.get("provider_id"),
            "source_kind":manifest.get("source_kind")}

def inventory(root):
    root=Path(root)
    if not root.is_dir():raise FileNotFoundError(root)
    results=[]
    for symbol in sorted(x for x in root.iterdir() if x.is_dir()):
        p=symbol/"1d.jsonl"
        if not p.is_file():
            results.append({"symbol":symbol.name,"tf":"1d","status":"MISSING"})
            continue
        try:
            results.append({"symbol":symbol.name,"tf":"1d",
                            **inspect_daily(p)})
        except (ValueError,IndexError,TypeError,KeyError) as exc:
            results.append({"symbol":symbol.name,"tf":"1d",
                            "status":"INVALID","reason":str(exc)})
    return {"status":"INVENTORY_ONLY_NOT_MODEL_VALIDATION",
            "source_root":str(root),"results":results}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=inventory(args.root)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":result["status"],
                      "files":len(result["results"]),"output":str(out)}))
