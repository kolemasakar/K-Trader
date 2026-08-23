from __future__ import annotations

import asyncio
import time
from contextlib import suppress
from datetime import datetime, timezone
from collections.abc import Sequence

from ktrader.api.state import ApiReadModel, ScannerRuntimeStatus
from ktrader.market.live import LiveMarketDataService
from ktrader.market.service import select_first_available_provider
from ktrader.operations.maintenance import OperationalSafetyError, RuntimeMaintenance
from ktrader.providers.base import MarketDataProvider, ProviderError
from ktrader.runtime.analyzer import EngineSymbolAnalyzer, SymbolAnalysisResult
from ktrader.runtime.models import RuntimeScannerConfig, ScannerCycleResult, SymbolScanError
from ktrader.storage.sqlite import CandleRepository


class ScannerCoordinator:
    def __init__(
        self,
        providers: Sequence[MarketDataProvider],
        repository: CandleRepository,
        read_model: ApiReadModel,
        *,
        config: RuntimeScannerConfig | None = None,
        analyzer: EngineSymbolAnalyzer | None = None,
        maintenance: RuntimeMaintenance | None = None,
    ) -> None:
        if not providers:
            raise ValueError("at least one provider is required")
        self.providers = list(providers)
        self.repository = repository
        self.read_model = read_model
        self.config = config or RuntimeScannerConfig()
        self.analyzer = analyzer or EngineSymbolAnalyzer(repository, config=self.config)
        self.maintenance = maintenance
        self.live_service = LiveMarketDataService(repository, config=self.config.live)
        self._stop = asyncio.Event()
        self._live_task: asyncio.Task | None = None
        self._live_key: tuple[str, tuple[str, ...]] | None = None
        self._cycle_id = 0

    async def run_once(self, *, now: datetime | None = None) -> ScannerCycleResult:
        current = now or datetime.now(timezone.utc)
        started = time.monotonic()
        self._cycle_id += 1
        cycle_id = self._cycle_id

        if self.maintenance is not None:
            try:
                self.maintenance.preflight()
            except OperationalSafetyError as exc:
                status = ScannerRuntimeStatus(
                    status="ERROR",
                    provider_id=None,
                    universe_size=0,
                    data_ready=False,
                    last_scan_at=current,
                    last_error=str(exc),
                    cycle_id=cycle_id,
                    symbols_ready=0,
                    symbols_failed=0,
                    live_streaming=False,
                    last_cycle_duration_seconds=time.monotonic() - started,
                )
                self.read_model.clear_runtime_data(status=status)
                return ScannerCycleResult(cycle_id, None, 0, 0, 0, ())

        try:
            selection = await select_first_available_provider(self.providers, self.config.universe)
        except Exception as exc:
            status = ScannerRuntimeStatus(
                status="ERROR",
                provider_id=None,
                universe_size=0,
                data_ready=False,
                last_scan_at=current,
                last_error=f"{type(exc).__name__}: {exc}",
                cycle_id=cycle_id,
                symbols_ready=0,
                symbols_failed=0,
                live_streaming=False,
                last_cycle_duration_seconds=time.monotonic() - started,
            )
            self.read_model.clear_runtime_data(status=status)
            return ScannerCycleResult(cycle_id, None, 0, 0, 0, ())

        provider = self._provider_for(selection.snapshot.provider_id)
        universe = selection.snapshot.candidates
        selected = universe[: self.config.analysis_limit]
        operations_warnings: list[str] = []
        if self.maintenance is not None:
            capture_time = current if now is not None else datetime.now(timezone.utc)
            try:
                self.maintenance.capture_universe_if_due(
                    selection.snapshot,
                    captured_at=capture_time,
                )
            except Exception as exc:
                operations_warnings.append(self.maintenance.note_warning(exc))

        await self._ensure_live(provider, [item.instrument for item in selected])

        semaphore = asyncio.Semaphore(self.config.bootstrap_concurrency)

        async def analyze_one(rank: int, item):
            async with semaphore:
                return await self.analyzer.analyze(
                    provider,
                    item,
                    liquidity_rank=rank,
                    universe_size=len(universe),
                    now=current,
                )

        tasks = [analyze_one(rank, item) for rank, item in enumerate(selected, start=1)]
        raw_results = await asyncio.gather(*tasks, return_exceptions=True)
        decisions = []
        series = []
        errors: list[SymbolScanError] = []
        for item, result in zip(selected, raw_results):
            if isinstance(result, BaseException):
                errors.append(SymbolScanError(
                    provider.provider_id,
                    item.instrument.symbol,
                    f"{type(result).__name__}: {result}",
                ))
                continue
            assert isinstance(result, SymbolAnalysisResult)
            decisions.extend(result.decision_set)
            series.extend(result.candle_series)

        if self.maintenance is not None:
            backup_time = current if now is not None else datetime.now(timezone.utc)
            try:
                self.maintenance.backup_if_due(now=backup_time)
            except Exception as exc:
                operations_warnings.append(self.maintenance.note_warning(exc))

        ready = len(selected) - len(errors)
        duration = time.monotonic() - started
        provider_failures = [f"{failure.provider_id}: {failure.error}" for failure in selection.failures]
        symbol_failures = [f"{error.symbol}: {error.error}" for error in errors[:5]]
        messages = provider_failures + symbol_failures + operations_warnings
        status_name = (
            "READY"
            if ready and not errors and not operations_warnings
            else "DEGRADED"
            if ready
            else "ERROR"
        )
        status = ScannerRuntimeStatus(
            status=status_name,
            provider_id=provider.provider_id,
            universe_size=len(universe),
            data_ready=ready > 0,
            last_scan_at=current,
            last_error="; ".join(messages) if messages else None,
            cycle_id=cycle_id,
            symbols_ready=ready,
            symbols_failed=len(errors),
            live_streaming=self._live_task is not None and not self._live_task.done(),
            last_cycle_duration_seconds=duration,
        )
        self.read_model.publish_cycle(
            status=status,
            universe=universe,
            candle_series=series,
            decisions=decisions,
        )
        return ScannerCycleResult(
            cycle_id,
            provider.provider_id,
            len(universe),
            ready,
            len(errors),
            tuple(errors),
        )

    async def run_forever(self) -> None:
        while not self._stop.is_set():
            started = time.monotonic()
            try:
                await self.run_once()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                current = datetime.now(timezone.utc)
                self.read_model.clear_runtime_data(status=ScannerRuntimeStatus(
                    status="ERROR",
                    data_ready=False,
                    last_scan_at=current,
                    last_error=f"{type(exc).__name__}: {exc}",
                    cycle_id=self._cycle_id,
                    live_streaming=False,
                ))
            delay = max(0.0, self.config.scan_interval_seconds - (time.monotonic() - started))
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=delay)
            except asyncio.TimeoutError:
                pass

    async def stop(self) -> None:
        self._stop.set()
        await self._stop_live()
        for provider in self.providers:
            with suppress(Exception):
                await provider.close()

    def _provider_for(self, provider_id: str) -> MarketDataProvider:
        for provider in self.providers:
            if provider.provider_id == provider_id:
                return provider
        raise ProviderError(f"selected provider instance not found: {provider_id}")

    async def _ensure_live(self, provider: MarketDataProvider, instruments) -> None:
        key = (provider.provider_id, tuple(sorted(item.instrument_id for item in instruments)))
        if key == self._live_key and self._live_task is not None and not self._live_task.done():
            return
        await self._stop_live()
        self._live_key = key
        if not instruments:
            return
        self._live_task = asyncio.create_task(
            self.live_service.run(provider, instruments),
            name=f"ktrader-live-{provider.provider_id}",
        )

    async def _stop_live(self) -> None:
        task = self._live_task
        self._live_task = None
        self._live_key = None
        if task is None:
            return
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
