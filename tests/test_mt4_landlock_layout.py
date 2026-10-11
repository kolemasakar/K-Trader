import pytest
from scripts.run_readonly_research import validate_paths

def test_mt4_archive_under_tmp_remains_prohibited(tmp_path):
    source=tmp_path/"source";source.mkdir()
    (source/"full_corpus_series_validation_20261009.csv").write_text("broker_symbol,timeframe,status\n")
    (source/"research_max_available"/"normalized").mkdir(parents=True)
    results=tmp_path/"results";results.mkdir()
    with pytest.raises(ValueError,match="reserve /tmp"):
        validate_paths(source,results)
