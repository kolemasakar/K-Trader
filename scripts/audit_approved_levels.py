#!/usr/bin/env python3
"""Read-only source -> separate diagnostic; never creates admission labels."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from ktrader.mt4_research import MT4ResearchCorpus
from ktrader.s1_equity_level_rows import completed_daily, completed_weekly
from ktrader.level_semantic_audit import audit_panels


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--root',required=True)
    p.add_argument('--panels',required=True)
    p.add_argument('--output',required=True)
    p.add_argument('--symbol',default='ACHC.us')
    p.add_argument('--as-of',default='2026-10-07T00:00:00')
    args=p.parse_args(argv)
    root=Path(args.root).resolve(strict=True)
    panels_path=Path(args.panels).resolve(strict=True)
    output=Path(args.output).resolve()
    if output==root or root in output.parents or output==panels_path:
        raise ValueError('diagnostic output must not overwrite source or panels')
    corpus=MT4ResearchCorpus(root,wall_clock_mode=True)
    d=list(corpus.iter_closed(args.symbol,'D1',as_of=args.as_of))
    lines=corpus.paths[(args.symbol,'D1')].read_text(encoding='utf-8-sig').splitlines()
    actual=hashlib.sha256(('\n'.join(lines[1:])+'\n').encode()).hexdigest()
    if actual!=corpus.series[(args.symbol,'D1')]['normalized_sha256']:
        raise ValueError('D1 source content mismatch')
    panels=json.loads(panels_path.read_text())
    if any(x['source_sha256']!=actual for x in panels):
        raise ValueError('panel/source mismatch')
    cutoff=int(datetime.fromisoformat(args.as_of).replace(tzinfo=timezone.utc).timestamp()*1000)
    report=audit_panels(panels,{'D1':completed_daily(d),'W1':completed_weekly(d)},as_of_ms=cutoff)
    from ktrader import level_semantic_audit
    report.update(symbol=args.symbol,source_sha256=actual,
                  panels_sha256=hashlib.sha256(panels_path.read_bytes()).hexdigest(),
                  auditor_code_sha256=hashlib.sha256(Path(level_semantic_audit.__file__).read_bytes()).hexdigest())
    # Exclusive creation prevents accidentally replacing prior diagnostic evidence.
    with output.open('x') as f:
        f.write(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps({'counts':report['counts'],'admitted_levels':0,'output':str(output)}))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
