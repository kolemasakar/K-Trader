import importlib.util
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"scripts/research/internal_architectural_extremes_v1.py"
s=importlib.util.spec_from_file_location("arch",p)
m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
D=86400000
def b(i,h,l,c):
    return {"t":i*D,"close_t":(i+1)*D-1,"h":h,"l":l,"c":c}
def p(kind,price):
    return {"tf":"1d","kind":kind,"price":price,"pivot_open_ms":D,
            "confirmed_close_ms":3*D-1}
def test_high_anchor_uses_high_and_later_confirmed_break():
    bars=[b(0,9,3,6),b(1,10,4,5),b(2,9,4,6),b(3,9,3,9),b(4,12,3,11)]
    out=m.select_break_anchors(bars,[p("resistance",10)])
    assert len(out)==1 and out[0]["price"]==10
    assert out[0]["confirmed_close_ms"]==bars[4]["close_t"]
def test_low_anchor_uses_low_and_later_confirmed_break():
    bars=[b(0,9,3,6),b(1,10,4,5),b(2,9,4,6),b(3,9,3,5),b(4,9,2,3)]
    out=m.select_break_anchors(bars,[p("support",4)])
    assert len(out)==1 and out[0]["price"]==4
def test_unbroken_pivot_excluded():
    bars=[b(0,9,3,6),b(1,10,4,5),b(2,9,4,6),b(3,9,3,5),b(4,12,3,9)]
    assert not m.select_break_anchors(bars,[p("resistance",10)])
def test_reject_non_extreme_price():
    bars=[b(0,9,3,6),b(1,10,4,5),b(2,9,4,6),b(3,9,3,5)]
    try:m.select_break_anchors(bars,[p("resistance",5)])
    except AssertionError:return
    raise AssertionError("non-extreme was accepted")
