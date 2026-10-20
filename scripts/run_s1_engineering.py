#!/usr/bin/env python3
"""Owner-approved hypothetical geometry; verified runner gates remain intact."""
import argparse
import hashlib
import json
from pathlib import Path
from ktrader.mt4_research import MT4ResearchCorpus
from ktrader.engineering_s1 import epoch, run_engineering
from scripts.run_approved_backtest import code_manifest


def main(argv=None):
    p=argparse.ArgumentParser()
    for option in ('root','panels','profile','output'):
        p.add_argument('--'+option,required=True)
    p.add_argument('--as-of',default='2026-10-07T00:00:00')
    args=p.parse_args(argv)
    root=Path(args.root).resolve(strict=True)
    output=Path(args.output).resolve(strict=True)
    if root==output or root in output.parents or output in root.parents:
        raise ValueError('source/results overlap')
    corpus=MT4ResearchCorpus(root,wall_clock_mode=True)
    candles={tf:list(corpus.iter_closed('ACHC.us',tf,as_of=args.as_of)) for tf in ('D1','H1','M5')}
    hashes={}
    for tf in candles:
        lines=corpus.paths[('ACHC.us',tf)].read_text(encoding='utf-8-sig').splitlines()
        actual=hashlib.sha256(('\n'.join(lines[1:])+'\n').encode()).hexdigest()
        if actual!=corpus.series[('ACHC.us',tf)]['normalized_sha256']:
            raise ValueError('source content mismatch '+tf)
        hashes[tf]=actual
    profile=json.loads(Path(args.profile).read_text())
    panels=json.loads(Path(args.panels).read_text())
    first=run_engineering(candles,panels,profile,hashes['D1'],epoch(args.as_of))
    second=run_engineering(candles,panels,profile,hashes['D1'],epoch(args.as_of))
    if first!=second:
        raise ValueError('deterministic rerun mismatch')
    report={**first,'rerun_identical':True,'source_content_sha256':hashes,
            'series_counts':{tf:len(x) for tf,x in candles.items()},
            'code_manifest':code_manifest(),
            'profile_sha256':hashlib.sha256(Path(args.profile).read_bytes()).hexdigest(),
            'panels_sha256':hashlib.sha256(Path(args.panels).read_bytes()).hexdigest()}
    with (output/'s1_engineering.json').open('x') as f:
        f.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({k:report[k] for k in ('status','pool_counts','summary','rerun_identical','deterministic_sha256')}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
