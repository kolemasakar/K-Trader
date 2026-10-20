"""Offline tests: no source mutation, no future candles, fail-closed corruption."""
import csv
import json
import pytest
from pathlib import Path
from ktrader.mt4_research import MT4ResearchCorpus, CorpusError

def make_source(tmp_path, corrupt=False):
    root = tmp_path / "source"
    path = root / "research_max_available" / "normalized" / "a" / "SUI"
    path.mkdir(parents=True)
    fields = ("asset_class","broker_symbol","timeframe","candles","status")
    with (root / "full_corpus_series_validation_20261009.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        w.writerow(dict(asset_class="crypto",broker_symbol="SUIUSDt",timeframe="M5",candles=2,status="PASS"))
    rows=[dict(provider_id="mt4",broker_symbol="SUIUSDt",mt4_timeframe="M5",closed_bars_only=True,candle_count=2)]
    for minute in (0, 5):
        rows.append(dict(record_type="candle",closed=True,open_time=f"2026-01-01T00:{minute:02d}:00",
                         close_time=f"2026-01-01T00:{minute+5:02d}:00",open=1,high=2,low=0.5,close=1.5))
    if corrupt: rows[-1]["high"]=0.7
    (path / "5m.jsonl").write_text("".join(json.dumps(x)+"\n" for x in rows))
    return root

def test_no_lookahead(tmp_path):
    corpus=MT4ResearchCorpus(make_source(tmp_path), verified_broker_timezone="UTC")
    assert len(list(corpus.iter_closed("SUIUSDt","M5",as_of="2026-01-01T00:05:00Z")))==1
    assert len(list(corpus.iter_closed("SUIUSDt","M5",as_of="2026-01-01T00:10:00Z")))==2
    assert corpus.inventory()["assets"]==1

def test_invalid_ohlc_fails_closed(tmp_path):
    corpus=MT4ResearchCorpus(make_source(tmp_path,True), verified_broker_timezone="UTC")
    with pytest.raises(CorpusError):
        list(corpus.iter_closed("SUIUSDt","M5",as_of="2026-01-02T00:00:00Z"))

def test_cutoff_is_required(tmp_path):
    corpus=MT4ResearchCorpus(make_source(tmp_path), verified_broker_timezone="UTC")
    with pytest.raises(TypeError):
        list(corpus.iter_closed("SUIUSDt","M5"))


def test_opaque_clock_fails_closed(tmp_path):
    corpus=MT4ResearchCorpus(make_source(tmp_path))
    with pytest.raises(CorpusError, match="timezone"):
        list(corpus.iter_closed("SUIUSDt","M5",as_of="2026-01-01T00:10:00Z"))


def test_explicit_artificial_wall_clock(tmp_path):
    corpus=MT4ResearchCorpus(make_source(tmp_path), wall_clock_mode=True)
    assert len(list(corpus.iter_closed("SUIUSDt","M5",as_of="2026-01-01T00:05:00")))==1
    assert len(list(corpus.iter_closed("SUIUSDt","M5",as_of="2026-01-01T00:10:00")))==2

def test_clock_modes_mutually_exclusive(tmp_path):
    with pytest.raises(CorpusError, match="either"):
        MT4ResearchCorpus(make_source(tmp_path),wall_clock_mode=True,verified_broker_timezone="UTC")

def test_canonical_manifest_excludes_extra_acquisition(tmp_path):
    import hashlib
    root=make_source(tmp_path)
    canonical=root/'research_max_available/normalized/a/SUI/5m.jsonl'
    lines=canonical.read_text().splitlines()
    digest=hashlib.sha256(('\n'.join(lines[1:])+'\n').encode()).hexdigest()
    csvpath=root/'full_corpus_series_validation_20261009.csv'
    with csvpath.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['asset_class','broker_symbol','timeframe','candles','status','normalized_sha256'])
        writer.writeheader();writer.writerow(dict(asset_class='crypto',broker_symbol='SUIUSDt',timeframe='M5',candles=2,status='PASS',normalized_sha256=digest))
    extra=root/'research_max_available/normalized/extra/SUI/5m.jsonl'
    extra.parent.mkdir(parents=True);extra.write_text(canonical.read_text())
    manifests=root/'research_max_available/manifests';manifests.mkdir()
    (manifests/'a.json').write_text(json.dumps({'results':[{'broker_symbol':'SUIUSDt','timeframe':'M5','normalized_file':r'D:\source\normalized\a\SUI\5m.jsonl','normalized_content_sha256':digest}]}))
    corpus=MT4ResearchCorpus(root,wall_clock_mode=True)
    assert corpus.paths[('SUIUSDt','M5')]==canonical
    assert len(corpus.excluded_noncanonical)==1
    assert len(list(corpus.iter_closed('SUIUSDt','M5',as_of='2026-01-01T00:10:00')))==2
    canonical.write_text(canonical.read_text().replace('1.5','1.6'))
    with pytest.raises(CorpusError,match='hash mismatch'):
        list(corpus.iter_closed('SUIUSDt','M5',as_of='2026-01-01T00:10:00'))
