from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

from ktrader.history.universe import (
    build_universe_archive,
    load_universe_archive,
    write_universe_archive,
)


def _utc(value: str | None) -> datetime | None:
    if value is None:
        return None
    text = value.strip()
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    if parsed.tzinfo is None or parsed.utcoffset() is None or parsed.utcoffset().total_seconds() != 0:
        raise argparse.ArgumentTypeError("timestamp must be timezone-aware UTC")
    return parsed.astimezone(timezone.utc)


def _source_files(sources: list[Path], *, output: Path) -> list[Path]:
    output_resolved = output.resolve()
    files: set[Path] = set()
    for source in sources:
        if source.is_file():
            candidates = (source,)
        elif source.is_dir():
            candidates = tuple(source.rglob("*.jsonl"))
        else:
            raise SystemExit(f"source does not exist: {source}")
        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved == output_resolved:
                continue
            files.add(resolved)
    if not files:
        raise SystemExit("no universe archive source files found")
    return sorted(files)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Build one verified K-Trader universe archive from immutable Phase 11F "
            "universe capture files"
        )
    )
    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        nargs="+",
        help="One or more universe archive files or directories containing *.jsonl captures",
    )
    parser.add_argument("--provider", required=True)
    parser.add_argument("--start", type=_utc)
    parser.add_argument("--end", type=_utc)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    if args.start is not None and args.end is not None and args.end < args.start:
        parser.error("--end must not be before --start")

    files = _source_files(args.source, output=args.output)
    selected = []

    for path in files:
        archive = load_universe_archive(path)
        for snapshot in archive.snapshots:
            if snapshot.provider_id != args.provider:
                continue
            if args.start is not None and snapshot.captured_at < args.start:
                continue
            if args.end is not None and snapshot.captured_at > args.end:
                continue
            selected.append(snapshot)

    if not selected:
        raise SystemExit("no universe snapshots matched provider/time filters")

    selected.sort(key=lambda item: item.captured_at)
    digests = [snapshot.content_sha256 for snapshot in selected]
    duplicate_count = len(digests) - len(set(digests))
    if duplicate_count:
        raise SystemExit(f"duplicate universe snapshot digests selected: {duplicate_count}")

    archive = build_universe_archive(selected)
    output = write_universe_archive(args.output, archive)

    # Reload through the canonical verifier before reporting success.
    verified = load_universe_archive(output)
    if verified.archive_sha256 != archive.archive_sha256:
        raise RuntimeError("written universe archive failed digest round-trip verification")

    print(
        json.dumps(
            {
                "output": str(output),
                "schema_version": verified.schema_version,
                "provider_id": verified.provider_id,
                "source_file_count": len(files),
                "snapshot_count": len(verified.snapshots),
                "start": verified.snapshots[0].captured_at.isoformat().replace("+00:00", "Z"),
                "end": verified.snapshots[-1].captured_at.isoformat().replace("+00:00", "Z"),
                "archive_sha256": verified.archive_sha256,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
