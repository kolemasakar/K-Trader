from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json

import pytest

from ktrader.catalogue import (
    append_catalogue_entry,
    build_catalogue_entry,
    build_dataset_catalogue,
    load_dataset_catalogue,
    write_dataset_catalogue,
)
from ktrader.history import (
    build_history_dataset,
    build_mtf_bundle,
    build_universe_archive,
    build_universe_snapshot,
    write_mtf_bundle,
    write_universe_archive,
)
from ktrader.market.timeframes import expected_close_time
from ktrader.market.universe import UniverseConfig
from ktrader.models import NormalizedCandle, NormalizedInstrument, NormalizedTicker
from ktrader.outcomes import build_outcome_sample, load_outcome_sample, write_outcome_sample
from ktrader.outcomes.evaluator import SignalOutcome
from ktrader.replay import (
    ReplayLiquidityPoint,
    ReplayStudyConfig,
    ReplayStudyContext,
    ReplayStudyResult,
    build_study_cohort,
    build_study_run_provenance,
    inspect_replay_study,
    scanner_config_sha256,
    write_replay_study,
    write_study_cohort,
    write_study_run_provenance,
)
from ktrader.runtime.models import RuntimeScannerConfig


UTC = timezone.utc
PROVIDER = "bybit_linear"
SYMBOL = "SUIUSDT"
T0 = datetime(2026, 8, 23, 0, 0, tzinfo=UTC)


def _instrument() -> NormalizedInstrument:
    return NormalizedInstrument(
        provider_id=PROVIDER,
        symbol=SYMBOL,
        provider_symbol=SYMBOL,
        base_asset="SUI",
        quote_asset="USDT",
        market_type="LINEAR_FUTURES",
        contract_type="PERPETUAL",
        status="TRADING",
        price_tick=Decimal("0.0001"),
        quantity_step=Decimal("0.1"),
    )


def _ticker(timestamp: datetime, *, quote_volume: str = "1000000") -> NormalizedTicker:
    return NormalizedTicker(
        provider_id=PROVIDER,
        symbol=SYMBOL,
        timestamp=timestamp,
        last_price=Decimal("0.8"),
        quote_volume_24h=Decimal(quote_volume),
        base_volume_24h=Decimal("1250000"),
        trade_count_24h=1000,
        bid_price=Decimal("0.7999"),
        ask_price=Decimal("0.8001"),
    )


def _candle(interval: str) -> NormalizedCandle:
    return NormalizedCandle(
        provider_id=PROVIDER,
        symbol=SYMBOL,
        interval=interval,
        open_time=T0,
        close_time=expected_close_time(T0, interval),
        open=Decimal("0.8"),
        high=Decimal("0.82"),
        low=Decimal("0.79"),
        close=Decimal("0.81"),
        volume=Decimal("1000"),
        quote_volume=Decimal("810"),
        trade_count=100,
        closed=True,
    )


def _prepare_chain(tmp_path):
    root = tmp_path / "artifacts"
    root.mkdir()

    intervals = ("1d", "4h", "1h", "15m", "5m")
    datasets = {
        interval: build_history_dataset(
            (_candle(interval),),
            provider_symbol=SYMBOL,
            requested_bars=1,
            fetched_at=T0 + timedelta(days=1),
        )
        for interval in intervals
    }
    as_of = datasets["1d"].candles[-1].close_time
    bundle = build_mtf_bundle(datasets, as_of=as_of, required_intervals=intervals)
    bundle_path = write_mtf_bundle(root / "bundle", bundle)

    capture_time = T0 + timedelta(hours=12)
    universe_config = UniverseConfig(max_price=Decimal("3"), max_candidates=50)
    snapshot = build_universe_snapshot(
        PROVIDER,
        [_instrument()],
        [_ticker(capture_time - timedelta(seconds=1))],
        universe_config,
        captured_at=capture_time,
    )
    archive = build_universe_archive((snapshot,))
    archive_path = write_universe_archive(root / "universe.jsonl", archive)
    cohort = build_study_cohort(archive, max_context_age_seconds=300.0)
    cohort_path = write_study_cohort(root / "cohort", cohort)

    result = ReplayStudyResult(
        schema_version="ktrader.replay_study.v1",
        study_id="1" * 64,
        bundle_sha256=bundle.manifest.bundle_sha256,
        provider_id=PROVIDER,
        canonical_symbol=SYMBOL,
        analyzed_cutoffs=0,
        skipped_insufficient_history=1,
        skipped_missing_context=0,
        decision_records=(),
        outcome_counts={},
        unique_tradable_signals=0,
        binary_resolved_count=0,
    )
    study_path = write_replay_study(root / "study.jsonl", result)
    scanner = RuntimeScannerConfig()
    study_config = ReplayStudyConfig(step_bars=1, horizon_bars=24)
    context = cohort.contexts[SYMBOL]
    provenance = build_study_run_provenance(
        result,
        study_path,
        context,
        scanner,
        study_config,
        cohort_sha256=cohort.cohort_sha256,
    )
    provenance_path = write_study_run_provenance(root / "study.provenance.json", provenance)

    info = inspect_replay_study(study_path)
    sample = build_outcome_sample(
        (),
        source_study_id=info.study_id,
        source_replay_study_sha256=info.file_sha256,
        provider_id=PROVIDER,
        canonical_symbol=SYMBOL,
    )
    sample_path = write_outcome_sample(root / "outcomes.jsonl", sample)

    return {
        "root": root,
        "bundle": bundle,
        "bundle_path": bundle_path,
        "archive": archive,
        "archive_path": archive_path,
        "cohort": cohort,
        "cohort_path": cohort_path,
        "result": result,
        "study_path": study_path,
        "scanner": scanner,
        "study_config": study_config,
        "provenance": provenance,
        "provenance_path": provenance_path,
        "sample": sample,
        "sample_path": sample_path,
    }


def _entry(chain):
    return build_catalogue_entry(
        chain["root"],
        mtf_bundle_path=chain["bundle_path"],
        universe_archive_path=chain["archive_path"],
        study_cohort_path=chain["cohort_path"],
        replay_study_path=chain["study_path"],
        study_provenance_path=chain["provenance_path"],
        outcome_sample_path=chain["sample_path"],
    )


def test_full_dataset_catalogue_chain_roundtrip_and_artifact_verification(tmp_path):
    chain = _prepare_chain(tmp_path)
    entry = _entry(chain)
    catalogue = build_dataset_catalogue((entry,))
    path = write_dataset_catalogue(chain["root"] / "catalogue.json", catalogue)
    loaded = load_dataset_catalogue(path, artifact_root=chain["root"])

    assert loaded.catalogue_sha256 == catalogue.catalogue_sha256
    assert loaded.entries[0].entry_id == entry.entry_id
    assert loaded.entries[0].mtf_bundle.semantic_id == chain["bundle"].manifest.bundle_sha256
    assert loaded.entries[0].study_cohort.semantic_id == chain["cohort"].cohort_sha256
    assert loaded.entries[0].study_provenance.semantic_id == chain["provenance"].provenance_sha256
    assert loaded.entries[0].outcome_sample.semantic_id == chain["sample"].content_sha256


def test_catalogue_detects_registered_replay_study_file_tampering(tmp_path):
    chain = _prepare_chain(tmp_path)
    catalogue_path = write_dataset_catalogue(
        chain["root"] / "catalogue.json",
        build_dataset_catalogue((_entry(chain),)),
    )
    chain["study_path"].write_text(
        chain["study_path"].read_text(encoding="utf-8") + "\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="replay-study content digest|artifact verification"):
        load_dataset_catalogue(catalogue_path, artifact_root=chain["root"])


def test_catalogue_rejects_provenance_context_not_from_cohort(tmp_path):
    chain = _prepare_chain(tmp_path)
    context = chain["cohort"].contexts[SYMBOL]
    changed_point = replace(context.liquidity_points[0], liquidity_score=Decimal("999"))
    changed_context = ReplayStudyContext(
        instrument=context.instrument,
        liquidity_points=(changed_point,),
        max_context_age_seconds=context.max_context_age_seconds,
    )
    wrong = build_study_run_provenance(
        chain["result"],
        chain["study_path"],
        changed_context,
        chain["scanner"],
        chain["study_config"],
        cohort_sha256=chain["cohort"].cohort_sha256,
    )
    wrong_path = write_study_run_provenance(chain["root"] / "wrong.provenance.json", wrong)
    with pytest.raises(ValueError, match="context digest does not match cohort"):
        build_catalogue_entry(
            chain["root"],
            mtf_bundle_path=chain["bundle_path"],
            universe_archive_path=chain["archive_path"],
            study_cohort_path=chain["cohort_path"],
            replay_study_path=chain["study_path"],
            study_provenance_path=wrong_path,
        )


def test_catalogue_rejects_cohort_from_different_archive(tmp_path):
    chain = _prepare_chain(tmp_path)
    later = T0 + timedelta(hours=13)
    second_snapshot = build_universe_snapshot(
        PROVIDER,
        [_instrument()],
        [_ticker(later - timedelta(seconds=1), quote_volume="2000000")],
        UniverseConfig(max_price=Decimal("3"), max_candidates=50),
        captured_at=later,
    )
    second_archive = build_universe_archive((second_snapshot,))
    second_path = write_universe_archive(chain["root"] / "other-universe.jsonl", second_archive)
    with pytest.raises(ValueError, match="does not belong"):
        build_catalogue_entry(
            chain["root"],
            mtf_bundle_path=chain["bundle_path"],
            universe_archive_path=second_path,
            study_cohort_path=chain["cohort_path"],
            replay_study_path=chain["study_path"],
            study_provenance_path=chain["provenance_path"],
        )


def test_outcome_sample_roundtrip_and_nonbinary_rejection(tmp_path):
    chain = _prepare_chain(tmp_path)
    loaded = load_outcome_sample(chain["sample_path"])
    assert loaded.record_count == 0
    assert loaded.content_sha256 == chain["sample"].content_sha256

    outcome = SignalOutcome(
        decision_id="2" * 64,
        provider_id=PROVIDER,
        canonical_symbol=SYMBOL,
        side="LONG",
        grade="A",
        setup_score=85,
        setup_type="TRAP_LEVEL_CONFIRMATION",
        engine_version="test",
        decision_time=T0,
        entry=Decimal("0.8"),
        stop=Decimal("0.79"),
        target=Decimal("0.83"),
        planned_rr=Decimal("3"),
        status="AMBIGUOUS",
        entry_bar_open_time=None,
        resolved_bar_open_time=None,
        bars_to_entry=None,
        bars_in_trade=None,
        outcome_r=None,
        reason="TEST",
        evaluated_at=T0 + timedelta(hours=1),
    )
    with pytest.raises(ValueError, match="only binary"):
        build_outcome_sample(
            (outcome,),
            source_study_id="1" * 64,
            source_replay_study_sha256="3" * 64,
            provider_id=PROVIDER,
            canonical_symbol=SYMBOL,
        )


def test_replay_study_inspection_rejects_probability(tmp_path):
    chain = _prepare_chain(tmp_path)
    rows = chain["study_path"].read_text(encoding="utf-8").splitlines()
    manifest = json.loads(rows[0])
    manifest["estimated_probability"] = 0.75
    rows[0] = json.dumps(manifest, sort_keys=True)
    chain["study_path"].write_text("\n".join(rows) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must not contain estimated probability"):
        inspect_replay_study(chain["study_path"])


def test_scanner_config_digest_changes_when_analysis_threshold_changes():
    baseline = RuntimeScannerConfig()
    changed = replace(baseline, vsa_high_volume_min=Decimal("2.1"))
    assert scanner_config_sha256(baseline) != scanner_config_sha256(changed)


def test_catalogue_rejects_duplicate_replay_study_registration(tmp_path):
    chain = _prepare_chain(tmp_path)
    entry = _entry(chain)
    first = append_catalogue_entry(None, entry)
    with pytest.raises(ValueError, match="same replay study|duplicate"):
        append_catalogue_entry(first, entry)
