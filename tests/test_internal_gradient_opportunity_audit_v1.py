"""Archived algorithm regression; preserved but excluded from active CI."""
import pytest
pytest.skip("ARCHIVED_LEVEL_ALGORITHM_DO_NOT_USE", allow_module_level=True)

import importlib.util
from pathlib import Path
import pytest
p=Path(__file__).resolve().parents[1]/"scripts/research/internal_gradient_opportunity_audit_v1.py"
spec=importlib.util.spec_from_file_location("audit",p)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def test_range_cross_without_close():
    z={"kind":"support","low":100,"center":101,"high":102}
    x=m.classify(z,{"l":99,"h":103,"c":104})
    assert x["range_cross"] and x["range_center_cross"] and not x["close_inside"]

def test_edge_only_range_not_misclassified_as_center():
    z={"kind":"support","low":100,"center":101,"high":102}
    x=m.classify(z,{"l":99,"h":100.5,"c":99.5})
    assert x["range_edge_only"] and not x["range_center_cross"]

def test_singleton_is_separate():
    x=m.classify({"low":100,"center":100,"high":100},
                 {"l":99,"h":101,"c":101})
    assert x["width"]=="singleton" and x["range_cross"] and not x["close_inside"]

def test_close_groups():
    z={"kind":"support","low":100,"center":101,"high":102}
    assert m.classify(z,{"l":100,"h":102,"c":101})["close_group"]=="center"
    assert m.classify(z,{"l":100,"h":102,"c":100.1})["close_group"]=="edge"
    assert m.classify(z,{"l":100,"h":102,"c":100.5})["close_group"]=="middle"

def test_invalid_geometry():
    with pytest.raises(ValueError):
        m.classify({"kind":"support","low":102,"center":101,"high":100},{"l":99,"h":103,"c":101})

def test_support_uses_low_not_close():
    z={"kind":"support","low":100,"center":101,"high":102}
    x=m.classify(z,{"l":100.1,"h":103,"c":103})
    assert x["extreme_inside"] and x["extreme_group"]=="edge"
    assert not x["close_inside"]

def test_resistance_uses_high_not_close():
    z={"kind":"resistance","low":100,"center":101,"high":102}
    x=m.classify(z,{"l":99,"h":101,"c":99})
    assert x["extreme_inside"] and x["extreme_group"]=="center"
    assert not x["close_inside"]
