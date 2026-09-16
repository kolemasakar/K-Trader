#!/usr/bin/env python3
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import math
import os
import pathlib
import shutil
from datetime import datetime, timezone

SCHEMA = 'ktrader.disk_retention.plan.v1'
DEFAULT_ALLOWED_BASE = pathlib.Path('/data/research')


def ztime(ts: float) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat().replace('+00:00', 'Z')


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def is_within(path: pathlib.Path, parent: pathlib.Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def resolve_no_symlink(path: pathlib.Path) -> pathlib.Path:
    if path.is_symlink():
        raise RuntimeError(f'SYMLINK_CANDIDATE_FORBIDDEN {path}')
    return path.resolve()


def path_size(path: pathlib.Path) -> int:
    if path.is_symlink():
        raise RuntimeError(f'SYMLINK_CANDIDATE_FORBIDDEN {path}')
    if path.is_file():
        return path.stat().st_size
    total = 0
    for root, dirs, files in os.walk(path, followlinks=False):
        root_path = pathlib.Path(root)
        for name in dirs:
            p = root_path / name
            if p.is_symlink():
                raise RuntimeError(f'SYMLINK_INSIDE_CANDIDATE_FORBIDDEN {p}')
            total += p.stat().st_size
        for name in files:
            p = root_path / name
            if p.is_symlink():
                raise RuntimeError(f'SYMLINK_INSIDE_CANDIDATE_FORBIDDEN {p}')
            total += p.stat().st_size
    total += path.stat().st_size
    return total


def load_config(path: pathlib.Path) -> dict:
    cfg = json.loads(path.read_text())
    trigger = int(cfg.get('trigger_percent', 80))
    fraction = float(cfg.get('delete_fraction', 0.20))
    if not 1 <= trigger <= 99:
        raise RuntimeError('INVALID_TRIGGER_PERCENT')
    if not 0 < fraction <= 1:
        raise RuntimeError('INVALID_DELETE_FRACTION')
    for key in ('eligible_globs', 'protected_paths', 'protected_globs', 'protect_latest_for_globs'):
        value = cfg.get(key, [])
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise RuntimeError(f'INVALID_CONFIG_LIST {key}')
    return cfg


def resolved_protected(cfg: dict) -> set[pathlib.Path]:
    protected: set[pathlib.Path] = set()
    for raw in cfg.get('protected_paths', []):
        protected.add(pathlib.Path(raw).resolve(strict=False))
    for pattern in cfg.get('protected_globs', []):
        for raw in glob.glob(pattern):
            protected.add(pathlib.Path(raw).resolve(strict=False))
    for pattern in cfg.get('protect_latest_for_globs', []):
        matches = [pathlib.Path(raw) for raw in glob.glob(pattern)]
        matches = [p for p in matches if p.exists()]
        if matches:
            latest = max(matches, key=lambda p: (p.stat().st_mtime_ns, str(p)))
            protected.add(latest.resolve())
    return protected


def is_protected(candidate: pathlib.Path, protected: set[pathlib.Path]) -> bool:
    if any('holdout' in part.lower() for part in candidate.parts):
        return True
    for protected_path in protected:
        if candidate == protected_path or is_within(candidate, protected_path):
            return True
    return False


def collect_candidates(cfg: dict, allowed_base: pathlib.Path) -> tuple[list[dict], list[dict]]:
    allowed_base = allowed_base.resolve()
    protected = resolved_protected(cfg)
    seen: set[pathlib.Path] = set()
    candidates: list[pathlib.Path] = []
    excluded: list[dict] = []

    for pattern in cfg.get('eligible_globs', []):
        for raw in sorted(glob.glob(pattern)):
            path = pathlib.Path(raw)
            if not path.exists():
                continue
            resolved = resolve_no_symlink(path)
            if resolved == allowed_base or not is_within(resolved, allowed_base):
                raise RuntimeError(f'CANDIDATE_OUTSIDE_ALLOWED_BASE {resolved}')
            if resolved in seen:
                continue
            seen.add(resolved)
            if is_protected(resolved, protected):
                excluded.append({'path': str(resolved), 'reason': 'PROTECTED'})
                continue
            candidates.append(resolved)

    candidates.sort(key=str)
    for i, left in enumerate(candidates):
        for right in candidates[i + 1:]:
            if is_within(right, left) or is_within(left, right):
                raise RuntimeError(f'OVERLAPPING_CANDIDATES {left} {right}')

    rows = []
    for path in candidates:
        st = path.stat()
        rows.append(
            {
                'path': str(path),
                'mtime_utc': ztime(st.st_mtime),
                'mtime_ns': st.st_mtime_ns,
                'bytes': path_size(path),
                'kind': 'directory' if path.is_dir() else 'file',
            }
        )
    rows.sort(key=lambda row: (row['mtime_ns'], row['path']))
    return rows, sorted(excluded, key=lambda row: row['path'])


def select_oldest(candidates: list[dict], fraction: float) -> tuple[list[dict], int]:
    total = sum(row['bytes'] for row in candidates)
    if not candidates or total <= 0:
        return [], 0
    target = max(1, math.ceil(total * fraction))
    selected = []
    selected_bytes = 0
    for row in candidates:
        selected.append(row)
        selected_bytes += row['bytes']
        if selected_bytes >= target:
            break
    return selected, target


def write_manifest(manifest_dir: pathlib.Path, payload: dict) -> tuple[pathlib.Path, str]:
    manifest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    path = manifest_dir / f'disk_retention_plan_{stamp}.json'
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    digest = sha256_file(path)
    path.with_suffix(path.suffix + '.sha256').write_text(f'{digest}  {path.name}\n')
    return path, digest


def main() -> None:
    ap = argparse.ArgumentParser(description='K-Trader fail-closed disk-retention planner (dry-run only)')
    ap.add_argument('--config', required=True)
    ap.add_argument('--manifest-dir', required=True)
    ap.add_argument('--filesystem', default='/')
    ap.add_argument('--allowed-base', default=str(DEFAULT_ALLOWED_BASE))
    ap.add_argument('--force-plan', action='store_true', help='plan even below threshold; never deletes')
    args = ap.parse_args()

    config_path = pathlib.Path(args.config)
    manifest_dir = pathlib.Path(args.manifest_dir)
    allowed_base = pathlib.Path(args.allowed_base)
    cfg = load_config(config_path)

    if not allowed_base.exists():
        raise SystemExit(f'ALLOWED_BASE_MISSING {allowed_base}')

    usage = shutil.disk_usage(args.filesystem)
    used_percent = (usage.used / usage.total * 100.0) if usage.total else 0.0
    trigger = int(cfg.get('trigger_percent', 80))
    fraction = float(cfg.get('delete_fraction', 0.20))
    triggered = used_percent >= trigger

    payload = {
        'schema_version': SCHEMA,
        'mode': 'DRY_RUN_ONLY',
        'deletion_performed': False,
        'filesystem': str(pathlib.Path(args.filesystem).resolve()),
        'allowed_base': str(allowed_base.resolve()),
        'trigger_percent': trigger,
        'delete_fraction': fraction,
        'disk_total_bytes': usage.total,
        'disk_used_bytes': usage.used,
        'disk_free_bytes': usage.free,
        'disk_used_percent': used_percent,
        'triggered': triggered,
        'force_plan': bool(args.force_plan),
        'config_path': str(config_path.resolve()),
        'config_sha256': sha256_file(config_path),
        'eligible_candidates': [],
        'excluded_protected_candidates': [],
        'would_delete': [],
        'eligible_total_bytes': 0,
        'target_delete_bytes': 0,
        'would_delete_bytes': 0,
    }

    if not triggered and not args.force_plan:
        payload['status'] = 'BELOW_TRIGGER_NO_ACTION'
    else:
        candidates, excluded = collect_candidates(cfg, allowed_base)
        selected, target = select_oldest(candidates, fraction)
        payload['eligible_candidates'] = candidates
        payload['excluded_protected_candidates'] = excluded
        payload['would_delete'] = selected
        payload['eligible_total_bytes'] = sum(row['bytes'] for row in candidates)
        payload['target_delete_bytes'] = target
        payload['would_delete_bytes'] = sum(row['bytes'] for row in selected)
        if not candidates:
            payload['status'] = 'TRIGGERED_NO_ELIGIBLE_CANDIDATES' if triggered else 'FORCED_PLAN_NO_ELIGIBLE_CANDIDATES'
        else:
            payload['status'] = 'TRIGGERED_DRY_RUN_PLAN_READY' if triggered else 'FORCED_DRY_RUN_PLAN_READY'

    manifest_path, digest = write_manifest(manifest_dir, payload)
    print(
        json.dumps(
            {
                'status': payload['status'],
                'mode': payload['mode'],
                'disk_used_percent': used_percent,
                'triggered': triggered,
                'eligible_candidate_count': len(payload['eligible_candidates']),
                'would_delete_count': len(payload['would_delete']),
                'would_delete_bytes': payload['would_delete_bytes'],
                'manifest_path': str(manifest_path),
                'manifest_sha256': digest,
            },
            sort_keys=True,
        )
    )


if __name__ == '__main__':
    main()
