#!/usr/bin/env python3
"""No-dependency ARM64 execution smoke; synthetic, not market outcomes."""
import json
from dataclasses import replace
from decimal import Decimal as D
from pathlib import Path
from ktrader.approved_models import Bar,Context
from ktrader.approved_scheduler import run_model


def b(o=100,h=101,l=99,c=100):return Bar(*map(lambda x:D(str(x)),(o,h,l,c)))
c=Context(D(100),1,D('.04'),D('.01'),D('.01'),D(10),'us_equity',True,True,('DOWN',)*3,'UP',True,technical_stop=D('99.9'))
seed=[b()]*20+[b(100.1,100.2,100,100.1)]
scenarios={}
for scenario in ('A','B'):
    bars=[b(100.1,100.15,100.01,100.04),b(100.1,100.6,100.05,100.5)]
    first=run_model(bars,'S1',lambda i,h:c,scenario,seed_history=seed)
    second=run_model(bars,'S1',lambda i,h:c,scenario,seed_history=seed)
    assert first==second and first and first[0]['status']=='TP'
    assert first[0]['gross_r']=='3' and first[0]['net_r'] is None
    scenarios[scenario]={'deterministic':True,'synthetic_orders':len(first),'status':first[0]['status']}
report={'run_kind':'SYNTHETIC_S1_EXECUTION_SMOKE_NOT_MARKET_BACKTEST','scenarios':scenarios,
        'legacy_strategy_used':False,'source_mutated':False}
Path('/data/research/approved-preparation-20261011/synthetic_execution_smoke.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
print(json.dumps(report,sort_keys=True))
