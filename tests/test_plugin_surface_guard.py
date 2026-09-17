from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
P=Path(__file__).parents[1]/"scripts"/"plugin_surface_guard.py"
spec=spec_from_file_location("plugin_guard",P); m=module_from_spec(spec); spec.loader.exec_module(m)

def test_read_only_surface_passes():
    text='''paths:\n  /health:\n    get:\n  /v1/scanner/status:\n    get:\n  /v1/signals:\n    get:\n'''; assert m.inspect(text)["status"]=="PASS"

def test_write_method_fails_closed():
    text='''paths:\n  /health:\n    get:\n  /v1/scanner/status:\n    get:\n  /v1/orders:\n    post:\n'''; r=m.inspect(text); assert r["status"]=="FAIL_CLOSED"; assert "post" in r["forbidden_methods"]
