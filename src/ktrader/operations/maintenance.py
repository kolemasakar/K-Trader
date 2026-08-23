from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import logging
import os
from pathlib import Path
import shutil

from ktrader.history.universe import build_universe_archive, build_universe_snapshot, write_universe_archive
from ktrader.market.service import UniverseSnapshot as LiveUniverseSnapshot
from ktrader.market.timeframes import require_utc
from ktrader.market.universe import UniverseConfig
from ktrader.storage.sqlite import CandleRepository


_LOG = logging.getLogger(__name__)


class OperationalSafetyError(RuntimeError):
    """Hard operational safety condition that should fail the scan closed."""


@dataclass(frozen=True, slots=True)
class DiskHealth:
    path: str
    total_bytes: int
    free_bytes: int
    free_percent: float
    required_free_bytes: int
    healthy: bool


@dataclass(frozen=True, slots=True)
class RuntimeMaintenanceConfig:
    research_capture_enabled: bool = True
    research_capture_interval_seconds: float = 300.0
    research_root: Path = Path("data/research/universe")
    backup_enabled: bool = True
    backup_interval_seconds: float = 21600.0
    backup_root: Path = Path("data/backups")
    backup_retention: int = 7
    disk_min_free_bytes: int = 2 * 1024 * 1024 * 1024
    disk_min_free_percent: float = 5.0

    def __post_init__(self) -> None:
        if self.research_capture_interval_seconds <= 0:
            raise ValueError("research_capture_interval_seconds must be positive")
        if self.backup_interval_seconds <= 0:
            raise ValueError("backup_interval_seconds must be positive")
        if self.backup_retention <= 0:
            raise ValueError("backup_retention must be positive")
        if self.disk_min_free_bytes < 0:
            raise ValueError("disk_min_free_bytes cannot be negative")
        if not 0 <= self.disk_min_free_percent < 100:
            raise ValueError("disk_min_free_percent must be in [0, 100)")


class RuntimeMaintenance:
    """Small synchronous operations layer invoked from scanner cycles.

    It deliberately does not own market-data provider requests. Research
    capture consumes the exact source instruments/tickers already fetched by
    the live universe cycle, preventing a second request from producing a
    subtly different historical rank snapshot.
    """

    def __init__(
        self,
        repository: CandleRepository,
        universe_config: UniverseConfig,
        *,
        config: RuntimeMaintenanceConfig | None = None,
    ) -> None:
        self.repository = repository
        self.universe_config = universe_config
        self.config = config or RuntimeMaintenanceConfig()
        self._last_capture_at: datetime | None = None
        self._last_backup_at: datetime | None = None
        self.last_warning: str | None = None
        self.last_disk_health: DiskHealth | None = None

    def preflight(self) -> DiskHealth:
        health = self.check_disk()
        self.last_disk_health = health
        if not health.healthy:
            raise OperationalSafetyError(
                "disk guard rejected runtime write path: "
                f"free={health.free_bytes} required={health.required_free_bytes}"
            )
        return health

    def check_disk(self) -> DiskHealth:
        root = self._data_root()
        root.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(root)
        free_percent = (usage.free / usage.total * 100.0) if usage.total else 0.0
        percent_bytes = int(usage.total * (self.config.disk_min_free_percent / 100.0))
        required = max(self.config.disk_min_free_bytes, percent_bytes)
        return DiskHealth(
            path=str(root),
            total_bytes=usage.total,
            free_bytes=usage.free,
            free_percent=free_percent,
            required_free_bytes=required,
            healthy=usage.free >= required,
        )

    def capture_universe_if_due(
        self,
        live_snapshot: LiveUniverseSnapshot,
        *,
        captured_at: datetime,
    ) -> Path | None:
        require_utc(captured_at)
        if not self.config.research_capture_enabled:
            return None
        if not self._due(self._last_capture_at, captured_at, self.config.research_capture_interval_seconds):
            return None
        if not live_snapshot.instruments or not live_snapshot.tickers:
            raise RuntimeError("live universe snapshot does not retain source instruments/tickers")

        snapshot = build_universe_snapshot(
            live_snapshot.provider_id,
            live_snapshot.instruments,
            live_snapshot.tickers,
            self.universe_config,
            captured_at=captured_at,
        )
        archive = build_universe_archive((snapshot,))
        provider_root = self.config.research_root / snapshot.provider_id
        day_root = provider_root / captured_at.strftime("%Y/%m/%d")
        day_root.mkdir(parents=True, exist_ok=True)
        stamp = captured_at.strftime("%Y%m%dT%H%M%S%fZ")
        target = day_root / f"{stamp}_{snapshot.content_sha256[:12]}.jsonl"
        temp = target.with_suffix(target.suffix + ".tmp")
        if target.exists():
            self._last_capture_at = captured_at
            return target
        write_universe_archive(temp, archive)
        os.replace(temp, target)
        self._last_capture_at = captured_at
        self.last_warning = None
        return target

    def backup_if_due(self, *, now: datetime) -> Path | None:
        require_utc(now)
        if not self.config.backup_enabled:
            return None
        if not self._due(self._last_backup_at, now, self.config.backup_interval_seconds):
            return None
        self.preflight()
        self.config.backup_root.mkdir(parents=True, exist_ok=True)
        stamp = now.strftime("%Y%m%dT%H%M%S%fZ")
        target = self.config.backup_root / f"ktrader_{stamp}.db"
        self.repository.backup_to(target)
        self._prune_backups()
        self._last_backup_at = now
        self.last_warning = None
        return target

    def note_warning(self, exc: BaseException) -> str:
        message = f"operations: {type(exc).__name__}: {exc}"
        self.last_warning = message
        _LOG.warning(message)
        return message

    @property
    def last_capture_at(self) -> datetime | None:
        return self._last_capture_at

    @property
    def last_backup_at(self) -> datetime | None:
        return self._last_backup_at

    def _data_root(self) -> Path:
        if self.repository.path == ":memory:":
            return Path.cwd()
        return Path(self.repository.path).expanduser().resolve().parent

    def _prune_backups(self) -> None:
        backups = sorted(
            self.config.backup_root.glob("ktrader_*.db"),
            key=lambda item: item.name,
            reverse=True,
        )
        for stale in backups[self.config.backup_retention :]:
            stale.unlink(missing_ok=True)

    @staticmethod
    def _due(last: datetime | None, now: datetime, interval_seconds: float) -> bool:
        if last is None:
            return True
        return (now - last).total_seconds() >= interval_seconds
