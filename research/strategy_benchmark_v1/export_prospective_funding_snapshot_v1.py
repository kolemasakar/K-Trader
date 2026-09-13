#!/usr/bin/env python3
from __future__ import annotations

import argparse, hashlib, json, pathlib, time, urllib.parse, urllib.request
from datetime import datetime, timezone

ENDPOINT = 'https://fapi.binance.com/fapi/v1/fundingRate'
SOURCE = 'Binance official fapi /fapi/v1/fundingRate'


def utc(v):
    d = datetime.fromisoformat(v[:-1] + '+00:00' if v.endswith('Z') else v)
    if d.tzinfo is None or d.utcoffset() is None or d.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError('UTC required')
    return d.astimezone(timezone.utc)


def ms(d): return int(d.timestamp() * 1000)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def request_page(symbol, start_ms, end_ms):
    q = urllib.parse.urlencode({'symbol': symbol, 'startTime': start_ms, 'endTime': end_ms, 'limit': 1000})
    req = urllib.request.Request(ENDPOINT + '?' + q, headers={'User-Agent': 'K-Trader-Research/1.0'})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.load(r)
        except Exception:
            if attempt == 3: raise
            time.sleep(0.5 * (2 ** attempt))


def collect(symbol, start_ms, end_ms):
    rows = {}; cursor = start_ms
    while cursor <= end_ms:
        page = request_page(symbol, cursor, end_ms)
        if not page: break
        for row in page:
            t = int(row['fundingTime'])
            if start_ms <= t <= end_ms: rows[t] = row
        last = max(int(row['fundingTime']) for row in page); nxt = last + 1
        if nxt <= cursor: raise RuntimeError('funding pagination stalled')
        cursor = nxt
        if len(page) < 1000: break
    return [rows[k] for k in sorted(rows)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot-root', required=True)
    ap.add_argument('--as-of', required=True, type=utc)
    args = ap.parse_args()
    root = pathlib.Path(args.snapshot_root); bundles = root / 'bundles'; out = root / 'funding_offline_v1'
    if out.exists(): raise SystemExit(f'OUTPUT_EXISTS {out}')
    out.mkdir(parents=True)
    end_ms = ms(args.as_of); rows = []
    for sdir in sorted(p for p in bundles.iterdir() if p.is_dir()):
        with (sdir / '1d.jsonl').open() as f: manifest = json.loads(next(f))
        if manifest.get('record_type') != 'manifest': raise RuntimeError(f'missing manifest: {sdir}')
        symbol = sdir.name; start_ms = ms(utc(manifest['actual_start'])); records = collect(symbol, start_ms, end_ms)
        payload = {'schema_version':'ktrader.prospective_funding_snapshot.v1','source':SOURCE,'symbol':symbol,
                   'query_start_ms':start_ms,'query_end_ms':end_ms,'records':records}
        p = out / f'{symbol}.json'; p.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
        rows.append({'symbol':symbol,'record_count':len(records),'first_funding_time':int(records[0]['fundingTime']) if records else None,
                     'last_funding_time':int(records[-1]['fundingTime']) if records else None,'sha256':sha(p)})
    summary = {'schema_version':'ktrader.prospective_funding_snapshot_summary.v1','source':SOURCE,
               'as_of':args.as_of.isoformat().replace('+00:00','Z'),'symbol_count':len(rows),'rows':rows}
    sp = out / 'summary.json'; sp.write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'symbol_count':len(rows),'records_total':sum(x['record_count'] for x in rows),
                      'summary_path':str(sp),'summary_sha256':sha(sp)}, sort_keys=True))

if __name__ == '__main__': main()
