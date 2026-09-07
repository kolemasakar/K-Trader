from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path
import subprocess
import sys

from ktrader.history.universe import (
    build_universe_archive,
    build_universe_snapshot,
    load_universe_archive,
    write_universe_archive,
)
from ktrader.market.universe import UniverseConfig
from ktrader.models import NormalizedInstrument, NormalizedTicker


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_universe_archive.py"


def _snapshot(captured_at: datetime, *, volume: str):
    instrument = NormalizedInstrument(
        provider_id="binance_usdm",
        symbol="SUIUSDT",
        base_asset="SUI",
        quote_asset="USDT",
        market_type="futures",
        contract_type="PERPETUAL",
        status="TRADING",
        provider_symbol="SUIUSDT",
    )
    ticker = NormalizedTicker(
        provider_id="binance_usdm",
        symbol="SUIUSDT",
        timestamp=captured_at,
        last_price=Decimal("1.25"),
        quote_volume_24h=Decimal(volume),
    )
    return build_universe_snapshot(
        "binance_usdm",
        [instrument],
        [ticker],
        UniverseConfig(),
        captured_at=captured_at,
    )


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def test_cli_builds_filtered_verified_archive_from_capture_directory(tmp_path: Path) -> None:
    source = tmp_path / "captures"
    source.mkdir()

    t0 = datetime(2026, 9, 5, 14, 40, tzinfo=timezone.utc)
    snapshots = (
        _snapshot(t0, volume="1000"),
        _snapshot(t0 + timedelta(minutes=5), volume="1100"),
        _snapshot(t0 + timedelta(minutes=10), volume="1200"),
    )

    for index, snapshot in enumerate(snapshots):
        write_universe_archive(
            source / f"capture_{index}.jsonl",
            build_universe_archive((snapshot,)),
        )

    output = tmp_path / "combined.jsonl"
    result = _run(
        "--source",
        str(source),
        "--provider",
        "binance_usdm",
        "--start",
        "2026-09-05T14:45:00Z",
        "--end",
        "2026-09-05T14:50:00Z",
        "--output",
        str(output),
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    archive = load_universe_archive(output)

    assert payload["schema_version"] == "ktrader.universe_archive.v1"
    assert payload["provider_id"] == "binance_usdm"
    assert payload["source_file_count"] == 3
    assert payload["snapshot_count"] == 2
    assert payload["archive_sha256"] == archive.archive_sha256
    assert tuple(item.captured_at for item in archive.snapshots) == (
        t0 + timedelta(minutes=5),
        t0 + timedelta(minutes=10),
    )


def test_cli_rejects_duplicate_snapshot_digests(tmp_path: Path) -> None:
    source = tmp_path / "captures"
    source.mkdir()
    captured_at = datetime(2026, 9, 5, 14, 40, tzinfo=timezone.utc)
    snapshot = _snapshot(captured_at, volume="1000")
    archive = build_universe_archive((snapshot,))

    write_universe_archive(source / "one.jsonl", archive)
    write_universe_archive(source / "two.jsonl", archive)

    result = _run(
        "--source",
        str(source),
        "--provider",
        "binance_usdm",
        "--output",
        str(tmp_path / "combined.jsonl"),
    )

    assert result.returncode != 0
    assert "duplicate universe snapshot digests selected" in result.stderr


def test_cli_requires_utc_bounds() -> None:
    result = _run(
        "--source",
        ".",
        "--provider",
        "binance_usdm",
        "--start",
        "2026-09-05T14:45:00",
        "--output",
        "unused.jsonl",
    )

    assert result.returncode != 0
    assert "timestamp must be timezone-aware UTC" in result.stderr
