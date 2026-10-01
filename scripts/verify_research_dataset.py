#!/usr/bin/env python3
"""Verify the immutable K-Trader Phase 11G archive from an isolated research container.

Requires an archive mount with enforced Docker readonly=true, and a separate
writable result mount. Does not import K-Trader runtime or use network access.
"""
import argparse
import errno
import hashlib
import json
import os
import pathlib
import re
import sys
import tempfile

TIMEFRAMES = ("1d", "4h", "1h", "15m", "5m")
EXPECTED_PROVIDER = "binance_usdm"


def file_manifest(root: pathlib.Path):
    entries = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("symlinks are prohibited in verified archives")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if not relative or relative.startswith("/"):
            raise ValueError("unsafe archive path")
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        entries.append({"path": relative, "bytes": path.stat().st_size, "sha256": digest.hexdigest()})
    h = hashlib.sha256()
    for entry in entries:
        h.update(f"{entry['path']} {entry['sha256']}\n".encode("utf-8"))
    return entries, h.hexdigest()


def check_readonly_mount(source: pathlib.Path):
    # Opening without O_TRUNC does not alter file bytes even if a broken mount
    # allows it. We explicitly fail if the descriptor is opened for writing.
    try:
        fd = os.open(source, os.O_WRONLY)
    except OSError as exc:
        if exc.errno in (errno.EROFS, errno.EACCES, errno.EPERM):
            return
        raise
    else:
        os.close(fd)
        raise ValueError("archive is writable: enforced READ-ONLY access missing")


def verify(root: pathlib.Path, expected_sha: str, check_mount: bool = True):
    if not re.fullmatch("[a-f0-9]{64}", expected_sha):
        raise ValueError("expected SHA-256 must be lowercase hexadecimal")
    if check_mount:
        check_readonly_mount(root / "dataset_summary.json")
    summary = json.loads((root / "dataset_summary.json").read_text(encoding="utf-8"))
    if summary.get("provider_id") != EXPECTED_PROVIDER:
        raise ValueError("unexpected market data provider")
    bundles_root = root / "bundles"
    bundles = sorted(p for p in bundles_root.iterdir() if p.is_dir())
    if len(bundles) != summary.get("panel_size") or len(bundles) != 19:
        raise ValueError("bundle count does not match source manifest")
    counts = dict.fromkeys(TIMEFRAMES, 0)
    for bundle in bundles:
        meta = json.loads((bundle / "bundle.json").read_text(encoding="utf-8"))
        if meta["canonical_symbol"] != bundle.name:
            raise ValueError("inconsistent symbol directory")
        for timeframe in TIMEFRAMES:
            count = 0
            with (bundle / f"{timeframe}.jsonl").open(encoding="utf-8") as f:
                first = json.loads(next(f))
                if first.get("record_type") != "manifest":
                    raise ValueError("missing JSONL history manifest")
                for line in f:
                    rec = json.loads(line)
                    if rec.get("record_type") != "candle" or rec.get("closed") is not True:
                        raise ValueError("missing or non-closed candle record")
                    if rec.get("interval") != timeframe or rec.get("symbol") != bundle.name:
                        raise ValueError("inconsistent market series")
                    count += 1
            if count != meta["candle_counts"][timeframe]:
                raise ValueError("bundle candle count mismatch")
            counts[timeframe] += count
    files, tree_sha = file_manifest(root)
    if tree_sha != expected_sha:
        raise ValueError("archive tree SHA-256 differs from the approved dataset version")
    return {
        "status": "VERIFIED_RESEARCH_DATASET",
        "access": "enforced-readonly-mount",
        "dataset_version_sha256": tree_sha,
        "provider_id": summary["provider_id"],
        "as_of": summary["as_of"],
        "symbol_count": len(bundles),
        "candle_counts": counts,
        "file_count": len(files),
        "content_bytes": sum(x["bytes"] for x in files),
        "files": files,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=pathlib.Path, default=pathlib.Path("/archive"))
    parser.add_argument("--results", type=pathlib.Path, default=pathlib.Path("/results"))
    parser.add_argument("--expected-tree-sha", required=True)
    args = parser.parse_args(argv)
    report = verify(args.archive, args.expected_tree_sha)
    args.results.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=args.results, delete=False, prefix=".report-", suffix=".tmp") as f:
        tmp = pathlib.Path(f.name)
        json.dump(report, f, indent=2, sort_keys=True)
        f.write("\n")
    os.replace(tmp, args.results / "verification.json")
    print(json.dumps({k: v for k, v in report.items() if k != "files"}, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError, StopIteration, json.JSONDecodeError) as exc:
        print(f"RESEARCH_DATASET_VERIFY_FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
