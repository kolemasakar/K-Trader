"""Read-only inventory of K-Trader-owned research data; never contacts external systems.

Inventory only. A dataset is not approved for level testing until its provenance
is classified as INTERNAL, with no external-holdout overlap.
"""
import argparse
import hashlib
import json
from pathlib import Path

TIMEFRAMES=("1d","1w")
def inventory(root):
    root=Path(root)
    if not root.is_dir():
        raise FileNotFoundError(root)
    results=[]
    for symbol in sorted(x for x in root.iterdir() if x.is_dir()):
        for tf in TIMEFRAMES:
            p=symbol/(tf+".jsonl")
            if not p.is_file():
                results.append({"symbol":symbol.name,"tf":tf,"status":"MISSING"})
                continue
            sha=hashlib.sha256()
            count=0;first=None;last=None;previous_close=None
            try:
                with p.open("rb") as stream:
                    for line in stream:
                        sha.update(line)
                        if not line.strip():continue
                        x=json.loads(line)
                        start=int(x[0]);end=int(x[6])
                        if end<start or (previous_close is not None and start<=previous_close):
                            raise ValueError("duplicate, overlapping or unordered candles")
                        if float(x[2])<float(x[3]):
                            raise ValueError("high below low")
                        if first is None:first=start
                        last=end;previous_close=end;count+=1
                status="PASS" if count else "EMPTY"
                results.append({"symbol":symbol.name,"tf":tf,"status":status,
                                "bars":count,"first_open_ms":first,
                                "last_close_ms":last,"sha256":sha.hexdigest(),
                                "provenance":"UNVERIFIED_REQUIRES_INTERNAL_CLASSIFICATION"})
            except (ValueError,IndexError,TypeError,json.JSONDecodeError) as exc:
                results.append({"symbol":symbol.name,"tf":tf,
                                "status":"INVALID","reason":str(exc)})
    return {"status":"INVENTORY_ONLY_NOT_MODEL_VALIDATION",
            "source_root":str(root),"results":results}

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--root",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=inventory(args.root)
    out=Path(args.output)
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"status":result["status"],
                      "files":len(result["results"]),"output":str(out)}))
