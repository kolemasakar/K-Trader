from scripts.run_readonly_research import validate_paths

def test_mt4_manifest_layout(tmp_path):
    source=tmp_path/"source"; source.mkdir()
    (source/"full_corpus_series_validation_20261009.csv").write_text("broker_symbol,timeframe,status\n")
    (source/"research_max_available"/"normalized").mkdir(parents=True)
    results=tmp_path/"results";results.mkdir()
    a,b=validate_paths(source,results)
    assert a==source.resolve() and b==results.resolve()
