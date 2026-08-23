from __future__ import annotations

import asyncio
import os
from contextlib import asynccontextmanager
from decimal import Decimal
from pathlib import Path

from ktrader.api.app import create_app
from ktrader.api.state import ApiReadModel
from ktrader.market.universe import UniverseConfig
from ktrader.operations import RuntimeMaintenance, RuntimeMaintenanceConfig
from ktrader.providers.registry import create_provider
from ktrader.runtime.coordinator import ScannerCoordinator
from ktrader.runtime.models import RuntimeScannerConfig
from ktrader.storage.sqlite import CandleRepository


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def build_runtime_app():
    provider_ids = tuple(
        value.strip()
        for value in os.getenv("KTRADER_PROVIDERS", "binance_usdm,bybit_linear").split(",")
        if value.strip()
    )
    if not provider_ids:
        raise RuntimeError("KTRADER_PROVIDERS cannot be empty")

    max_price = Decimal(os.getenv("KTRADER_MAX_PRICE", "3"))
    universe = UniverseConfig(
        quote_asset=os.getenv("KTRADER_QUOTE_ASSET", "USDT"),
        price_limit_enabled=_env_bool("KTRADER_PRICE_LIMIT_ENABLED", True),
        max_price=max_price,
        max_candidates=int(os.getenv("KTRADER_MAX_CANDIDATES", "50")),
    )
    config = RuntimeScannerConfig(
        universe=universe,
        analysis_limit=int(os.getenv("KTRADER_ANALYSIS_LIMIT", "20")),
        scan_interval_seconds=float(os.getenv("KTRADER_SCAN_INTERVAL_SECONDS", "60")),
        bootstrap_concurrency=int(os.getenv("KTRADER_BOOTSTRAP_CONCURRENCY", "2")),
    )
    repository = CandleRepository(os.getenv("KTRADER_DB_PATH", "data/ktrader.db"))
    maintenance_config = RuntimeMaintenanceConfig(
        research_capture_enabled=_env_bool("KTRADER_RESEARCH_CAPTURE_ENABLED", True),
        research_capture_interval_seconds=float(
            os.getenv("KTRADER_RESEARCH_CAPTURE_INTERVAL_SECONDS", "300")
        ),
        research_root=Path(
            os.getenv("KTRADER_RESEARCH_ROOT", "data/research/universe")
        ),
        backup_enabled=_env_bool("KTRADER_BACKUP_ENABLED", True),
        backup_interval_seconds=float(
            os.getenv("KTRADER_BACKUP_INTERVAL_SECONDS", "21600")
        ),
        backup_root=Path(os.getenv("KTRADER_BACKUP_ROOT", "data/backups")),
        backup_retention=int(os.getenv("KTRADER_BACKUP_RETENTION", "7")),
        disk_min_free_bytes=int(
            os.getenv("KTRADER_DISK_MIN_FREE_BYTES", str(2 * 1024 * 1024 * 1024))
        ),
        disk_min_free_percent=float(
            os.getenv("KTRADER_DISK_MIN_FREE_PERCENT", "5")
        ),
    )
    maintenance = RuntimeMaintenance(
        repository,
        universe,
        config=maintenance_config,
    )
    read_model = ApiReadModel()
    providers = [create_provider(provider_id) for provider_id in provider_ids]
    coordinator = ScannerCoordinator(
        providers,
        repository,
        read_model,
        config=config,
        maintenance=maintenance,
    )
    health_max_scan_age_seconds = float(
        os.getenv(
            "KTRADER_HEALTH_MAX_SCAN_AGE_SECONDS",
            str(max(180.0, config.scan_interval_seconds * 3.0)),
        )
    )

    @asynccontextmanager
    async def lifespan(_app):
        coordinator_task = asyncio.create_task(
            coordinator.run_forever(),
            name="ktrader-scanner-coordinator",
        )
        try:
            yield
        finally:
            await coordinator.stop()
            try:
                await coordinator_task
            except asyncio.CancelledError:
                pass
            repository.close()

    app = create_app(
        read_model,
        lifespan=lifespan,
        action_api_key=os.getenv("KTRADER_ACTION_API_KEY") or None,
        health_max_scan_age_seconds=health_max_scan_age_seconds,
    )
    app.state.coordinator = coordinator
    app.state.repository = repository
    app.state.maintenance = maintenance
    return app


app = build_runtime_app()
