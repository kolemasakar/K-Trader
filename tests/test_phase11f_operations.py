from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from ktrader.api.app import create_app
from ktrader.api.state import ApiReadModel, ScannerRuntimeStatus
from ktrader.history import load_universe_archive
from ktrader.market.service import UniverseSnapshot as LiveUniverseSnapshot, load_universe
from ktrader.market.universe import UniverseConfig, build_universe
from ktrader.models import NormalizedCandle, NormalizedInstrument, NormalizedTicker
from ktrader.operations import OperationalSafetyError, RuntimeMaintenance, RuntimeMaintenanceConfig
from ktrader.runtime.coordinator import ScannerCoordinator
from ktrader.storage.sqlite import CandleRepository


UTC = timezone.utc
T0 = datetime(2026, 8, 23, 17, 0, tzinfo=UTC)


def _instrument(symbol: str = "SUIUSDT") -> NormalizedInstrument:
    return NormalizedInstrument(
        provider_id="bybit_linear",
        symbol=symbol,
        provider_symbol=symbol,
        base_asset=symbol.removesuffix("USDT"),
        quote_asset="USDT",
        market_type="LINEAR_FUTURES",
        contract_type="PERPETUAL",
        status="TRADING",
        price_tick=Decimal("0.0001"),
        quantity_step=Decimal("0.1"),
    )


def _ticker(symbol: str, quote_volume: str, *, timestamp: datetime) -> NormalizedTicker:
    last = Decimal("0.8") if symbol == "SUIUSDT" else Decimal("0.2")
    return NormalizedTicker(
        provider_id="bybit_linear",
        symbol=symbol,
        timestamp=timestamp,
        last_price=last,
        quote_volume_24h=Decimal(quote_volume),
        base_volume_24h=Decimal("100000"),
        trade_count_24h=1000,
        bid_price=last - Decimal("0.0001"),
        ask_price=last + Decimal("0.0001"),
    )


def _candle() -> NormalizedCandle:
    return NormalizedCandle(
        provider_id="bybit_linear",
        symbol="SUIUSDT",
        interval="5m",
        open_time=T0 - timedelta(minutes=5),
        close_time=T0 - timedelta(milliseconds=1),
        open=Decimal("0.8"),
        high=Decimal("0.82"),
        low=Decimal("0.79"),
        close=Decimal("0.81"),
        volume=Decimal("1000"),
    )


def _live_snapshot(config: UniverseConfig) -> LiveUniverseSnapshot:
    instruments = (_instrument("SUIUSDT"), _instrument("DOGEUSDT"))
    tickers = (
        _ticker("SUIUSDT", "1000000", timestamp=T0 - timedelta(seconds=1)),
        _ticker("DOGEUSDT", "2000000", timestamp=T0 - timedelta(seconds=1)),
    )
    candidates = tuple(build_universe(list(instruments), list(tickers), config))
    return LiveUniverseSnapshot("bybit_linear", candidates, instruments, tickers)


def test_sqlite_online_backup_is_integrity_checked_and_restorable(tmp_path: Path):
    source = tmp_path / "ktrader.db"
    repository = CandleRepository(source)
    repository.upsert_many([_candle()])
    backup = repository.backup_to(tmp_path / "backups" / "snapshot.db")
    assert CandleRepository.verify_database(backup)
    repository.close()

    restored = CandleRepository(backup)
    try:
        assert restored.count("bybit_linear", "SUIUSDT", "5m") == 1
        assert restored.latest("bybit_linear", "SUIUSDT", "5m").close == Decimal("0.81")
    finally:
        restored.close()


def test_verify_database_rejects_corrupt_file(tmp_path: Path):
    corrupt = tmp_path / "bad.db"
    corrupt.write_bytes(b"not-a-sqlite-database")
    assert CandleRepository.verify_database(corrupt) is False


def test_disk_guard_fails_closed_when_required_space_exceeds_device(tmp_path: Path):
    repository = CandleRepository(tmp_path / "ktrader.db")
    config = UniverseConfig()
    maintenance = RuntimeMaintenance(
        repository,
        config,
        config=RuntimeMaintenanceConfig(
            disk_min_free_bytes=10**30,
            disk_min_free_percent=0,
            research_root=tmp_path / "research",
            backup_root=tmp_path / "backups",
        ),
    )
    with pytest.raises(OperationalSafetyError, match="disk guard rejected"):
        maintenance.preflight()
    repository.close()


@pytest.mark.asyncio
async def test_coordinator_disk_guard_clears_publishable_state_before_provider_access(tmp_path: Path):
    repository = CandleRepository(tmp_path / "ktrader.db")
    read_model = ApiReadModel()
    maintenance = RuntimeMaintenance(
        repository,
        UniverseConfig(),
        config=RuntimeMaintenanceConfig(
            disk_min_free_bytes=10**30,
            disk_min_free_percent=0,
            research_root=tmp_path / "research",
            backup_root=tmp_path / "backups",
        ),
    )
    coordinator = ScannerCoordinator([object()], repository, read_model, maintenance=maintenance)  # type: ignore[list-item]
    result = await coordinator.run_once(now=T0)
    assert result.provider_id is None
    status = read_model.get_status()
    assert status.status == "ERROR"
    assert status.data_ready is False
    assert "disk guard rejected" in (status.last_error or "")
    repository.close()


def test_continuous_research_capture_is_immutable_and_interval_bounded(tmp_path: Path):
    repository = CandleRepository(tmp_path / "ktrader.db")
    universe_config = UniverseConfig(max_price=Decimal("3"), max_candidates=2)
    maintenance = RuntimeMaintenance(
        repository,
        universe_config,
        config=RuntimeMaintenanceConfig(
            research_capture_interval_seconds=300,
            research_root=tmp_path / "research",
            backup_enabled=False,
            backup_root=tmp_path / "backups",
            disk_min_free_bytes=0,
            disk_min_free_percent=0,
        ),
    )
    snapshot = _live_snapshot(universe_config)
    first = maintenance.capture_universe_if_due(snapshot, captured_at=T0)
    assert first is not None and first.is_file()
    assert maintenance.capture_universe_if_due(snapshot, captured_at=T0 + timedelta(minutes=1)) is None
    second = maintenance.capture_universe_if_due(snapshot, captured_at=T0 + timedelta(minutes=5))
    assert second is not None and second.is_file() and second != first
    files = sorted((tmp_path / "research" / "bybit_linear").rglob("*.jsonl"))
    assert len(files) == 2
    for path in files:
        archive = load_universe_archive(path)
        assert len(archive.snapshots) == 1
        assert archive.snapshots[0].universe_size == 2
        assert [item.rank for item in archive.snapshots[0].members] == [1, 2]
    repository.close()


def test_periodic_backup_retention_keeps_latest_verified_files(tmp_path: Path):
    repository = CandleRepository(tmp_path / "ktrader.db")
    repository.upsert_many([_candle()])
    maintenance = RuntimeMaintenance(
        repository,
        UniverseConfig(),
        config=RuntimeMaintenanceConfig(
            research_capture_enabled=False,
            research_root=tmp_path / "research",
            backup_interval_seconds=1,
            backup_root=tmp_path / "backups",
            backup_retention=2,
            disk_min_free_bytes=0,
            disk_min_free_percent=0,
        ),
    )
    for offset in (0, 2, 4):
        assert maintenance.backup_if_due(now=T0 + timedelta(seconds=offset)) is not None
    backups = sorted((tmp_path / "backups").glob("ktrader_*.db"))
    assert len(backups) == 2
    assert all(CandleRepository.verify_database(path) for path in backups)
    restored = CandleRepository(backups[-1])
    try:
        assert restored.count("bybit_linear", "SUIUSDT", "5m") == 1
    finally:
        restored.close()
        repository.close()


@pytest.mark.asyncio
async def test_load_universe_retains_exact_source_inputs_for_research_capture():
    instruments = [_instrument("SUIUSDT"), _instrument("DOGEUSDT")]
    tickers = [
        _ticker("SUIUSDT", "1000000", timestamp=T0),
        _ticker("DOGEUSDT", "2000000", timestamp=T0),
    ]

    class Provider:
        provider_id = "bybit_linear"

        async def list_instruments(self):
            return list(instruments)

        async def get_tickers(self):
            return list(tickers)

    snapshot = await load_universe(Provider(), UniverseConfig(max_candidates=2))  # type: ignore[arg-type]
    assert snapshot.instruments == tuple(instruments)
    assert snapshot.tickers == tuple(tickers)
    assert [item.instrument.symbol for item in snapshot.candidates] == ["DOGEUSDT", "SUIUSDT"]


def test_health_watchdog_degrades_stale_scanner_without_api_shape_change():
    read_model = ApiReadModel()
    read_model.set_status(ScannerRuntimeStatus(
        status="READY",
        provider_id="bybit_linear",
        universe_size=2,
        data_ready=True,
        last_scan_at=datetime.now(UTC) - timedelta(minutes=10),
    ))
    app = create_app(read_model, health_max_scan_age_seconds=30)
    client = TestClient(app)
    stale = client.get("/health")
    assert stale.status_code == 200
    payload = stale.json()
    assert payload["status"] == "degraded"
    assert set(payload) == {
        "status",
        "mode",
        "api_version",
        "data_ready",
        "scanner_status",
        "provider_id",
        "action_auth_enabled",
        "generated_at",
    }

    read_model.set_status(ScannerRuntimeStatus(
        status="READY",
        provider_id="bybit_linear",
        universe_size=2,
        data_ready=True,
        last_scan_at=datetime.now(UTC),
    ))
    assert client.get("/health").json()["status"] == "ok"
