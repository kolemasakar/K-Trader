from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json

import pytest

from ktrader.history import (
    MTF_BUNDLE_SCHEMA_VERSION,
    build_history_dataset,
    build_mtf_bundle,
    load_mtf_bundle,
    slice_datasets_asof,
    write_mtf_bundle,
)
from ktrader.market.timeframes import CANONICAL_INTERVALS, interval_seconds
from ktrader.models import NormalizedCandle


UTC = timezone.utc


def dataset(interval: str, *, provider_id: str = "binance_usdm", count: int = 4):
    step = timedelta(seconds=interval_seconds(interval))
    start = datetime(2026, 8, 1, tzinfo=UTC)
    candles = []
    for index in range(count):
        open_time = start + step * index
        candles.append(
            NormalizedCandle(
                provider_id=provider_id,
                symbol="SUIUSDT",
                interval=interval,
                open_time=open_time,
                close_time=open_time + step - timedelta(milliseconds=1),
                open=Decimal("1.00"),
                high=Decimal("1.03"),
                low=Decimal("0.98"),
                close=Decimal("1.01"),
                volume=Decimal("100"),
                closed=True,
            )
        )
    return build_history_dataset(
        candles,
        provider_symbol="SUIUSDT",
        requested_bars=count,
        fetched_at=datetime(2026, 8, 10, tzinfo=UTC),
    )


def all_datasets(*, provider_id: str = "binance_usdm", count: int = 4):
    return {interval: dataset(interval, provider_id=provider_id, count=count) for interval in CANONICAL_INTERVALS}


def test_mtf_bundle_is_deterministic_and_provider_coherent():
    as_of = datetime(2026, 8, 10, tzinfo=UTC)
    first = build_mtf_bundle(all_datasets(), as_of=as_of)
    second = build_mtf_bundle(all_datasets(), as_of=as_of)
    assert first.manifest.schema_version == MTF_BUNDLE_SCHEMA_VERSION
    assert first.manifest.bundle_sha256 == second.manifest.bundle_sha256
    assert tuple(first.manifest.intervals) == CANONICAL_INTERVALS
    assert first.manifest.candle_counts["5m"] == 4


def test_mtf_bundle_rejects_provider_mixing():
    datasets = all_datasets()
    datasets["5m"] = dataset("5m", provider_id="bybit_linear")
    with pytest.raises(ValueError, match="mix providers"):
        build_mtf_bundle(datasets, as_of=datetime(2026, 8, 10, tzinfo=UTC))


def test_mtf_bundle_rejects_future_candle():
    with pytest.raises(ValueError, match="future candle"):
        build_mtf_bundle(all_datasets(), as_of=datetime(2026, 8, 1, 0, 6, tzinfo=UTC))


def test_slice_datasets_asof_removes_future_without_lookahead():
    source = all_datasets(count=8)
    cutoff = datetime(2026, 8, 3, 2, 0, tzinfo=UTC)
    bundle = slice_datasets_asof(
        source,
        as_of=cutoff,
        minimum_bars={interval: 1 for interval in CANONICAL_INTERVALS},
    )
    for history in bundle.datasets.values():
        assert history.candles[-1].close_time <= cutoff
    assert bundle.manifest.as_of == cutoff


def test_mtf_bundle_roundtrip_and_tamper_detection(tmp_path):
    bundle = build_mtf_bundle(all_datasets(), as_of=datetime(2026, 8, 10, tzinfo=UTC))
    root = write_mtf_bundle(tmp_path / "bundle", bundle)
    loaded = load_mtf_bundle(root)
    assert loaded.manifest.bundle_sha256 == bundle.manifest.bundle_sha256
    assert loaded.datasets["1h"].manifest.content_sha256 == bundle.datasets["1h"].manifest.content_sha256

    manifest_path = root / "bundle.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    payload["bundle_sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="bundle digest mismatch"):
        load_mtf_bundle(root)


def test_slice_requires_minimum_history_at_cutoff():
    with pytest.raises(ValueError, match="insufficient 1d history"):
        slice_datasets_asof(
            all_datasets(count=2),
            as_of=datetime(2026, 8, 1, 12, tzinfo=UTC),
            minimum_bars={"1d": 2, "4h": 1, "1h": 1, "15m": 1, "5m": 1},
        )
