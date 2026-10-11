import importlib.util
import json
from datetime import datetime,timedelta,timezone
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location("native",Path(__file__).resolve().parents[1]/"scripts/research/native_internal_d1_w1_v1.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def source(path,start,days):
    rows=[{"record_type":"manifest","interval":"1d","candle_count":days,
           "actual_start":start.isoformat().replace("+00:00","Z"),
           "actual_end":(start+timedelta(days=days)-timedelta(milliseconds=1)).isoformat().replace("+00:00","Z")}]
    for i in range(days):
        d=start+timedelta(days=i)
        rows.append({"record_type":"candle","closed":True,
                     "open_time":d.isoformat().replace("+00:00","Z"),
                     "close_time":(d+timedelta(days=1)-timedelta(milliseconds=1)).isoformat().replace("+00:00","Z"),
                     "open":"100","high":"105","low":"95","close":"101","volume":"10"})
    path.write_text("\n".join(map(json.dumps,rows))+"\n")

def test_complete_utc_weeks_only(tmp_path):
    start=datetime(2026,9,1,tzinfo=timezone.utc) # Tuesday
    p=tmp_path/"1d.jsonl";source(p,start,20)
    d=m.native_d1(p);w=m.complete_w1(d)
    assert len(d)==20 and len(w)==2
    assert all(x["close_t"]-x["t"]==7*m.DAY_MS-1 for x in w)

def test_reject_missing_day(tmp_path):
    start=datetime(2026,9,7,tzinfo=timezone.utc)
    p=tmp_path/"1d.jsonl";source(p,start,7)
    rows=p.read_text().splitlines()
    p.write_text("\n".join(rows[:3]+rows[4:])+"\n")
    with pytest.raises(ValueError):
        m.native_d1(p)

def test_partial_week_excluded(tmp_path):
    start=datetime(2026,9,1,tzinfo=timezone.utc)
    p=tmp_path/"1d.jsonl";source(p,start,5)
    assert m.complete_w1(m.native_d1(p))==[]
