from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Mapping

from ktrader.history.dataset import (
    HistoricalDataset,
    build_history_dataset,
    load_history_dataset,
    write_history_dataset,
)
from ktrader.market.timeframes import CANONICAL_INTERVALS, require_utc


MTF_BUNDLE_SCHEMA_VERSION = "ktrader.mtf_bundle.v1"


@dataclass(frozen=True, slots=True)
class MTFBundleManifest:
    schema_version: str
    provider_id: str
    canonical_symbol: str
    provider_symbol: str
    as_of: datetime
    intervals: tuple[str, ...]
    candle_counts: Mapping[str, int]
    history_digests: Mapping[str, str]
    bundle_sha256: str


@dataclass(frozen=True, slots=True)
class MTFReplayBundle:
    manifest: MTFBundleManifest
    datasets: Mapping[str, HistoricalDataset]


def build_mtf_bundle(
    datasets: Mapping[str, HistoricalDataset],
    *,
    as_of: datetime,
    required_intervals: tuple[str, ...] = CANONICAL_INTERVALS,
) -> MTFReplayBundle:
    require_utc(as_of)
    if not required_intervals:
        raise ValueError("required_intervals cannot be empty")
    if set(datasets) != set(required_intervals):
        raise ValueError("MTF bundle must contain exactly the required intervals")

    first = datasets[required_intervals[0]].manifest
    provider_id = first.provider_id
    canonical_symbol = first.canonical_symbol
    provider_symbol = first.provider_symbol
    counts: dict[str, int] = {}
    digests: dict[str, str] = {}

    for interval in required_intervals:
        dataset = datasets[interval]
        manifest = dataset.manifest
        if manifest.interval != interval:
            raise ValueError("MTF bundle interval key/manifest mismatch")
        if manifest.provider_id != provider_id:
            raise ValueError("MTF bundle cannot mix providers")
        if manifest.canonical_symbol != canonical_symbol:
            raise ValueError("MTF bundle cannot mix canonical symbols")
        if manifest.provider_symbol != provider_symbol:
            raise ValueError("MTF bundle cannot mix provider symbols")
        if not dataset.candles:
            raise ValueError("MTF bundle datasets cannot be empty")
        if dataset.candles[-1].close_time > as_of:
            raise ValueError("MTF bundle contains future candle beyond as_of")
        counts[interval] = len(dataset.candles)
        digests[interval] = manifest.content_sha256

    digest = _bundle_digest(
        provider_id=provider_id,
        canonical_symbol=canonical_symbol,
        provider_symbol=provider_symbol,
        as_of=as_of,
        required_intervals=required_intervals,
        candle_counts=counts,
        history_digests=digests,
    )
    manifest = MTFBundleManifest(
        schema_version=MTF_BUNDLE_SCHEMA_VERSION,
        provider_id=provider_id,
        canonical_symbol=canonical_symbol,
        provider_symbol=provider_symbol,
        as_of=as_of,
        intervals=tuple(required_intervals),
        candle_counts=counts,
        history_digests=digests,
        bundle_sha256=digest,
    )
    return MTFReplayBundle(manifest=manifest, datasets=dict(datasets))


def slice_datasets_asof(
    datasets: Mapping[str, HistoricalDataset],
    *,
    as_of: datetime,
    required_intervals: tuple[str, ...] = CANONICAL_INTERVALS,
    minimum_bars: Mapping[str, int] | None = None,
) -> MTFReplayBundle:
    """Create an MTF replay snapshot using only candles closed by ``as_of``."""
    require_utc(as_of)
    minimums = dict(minimum_bars or {})
    sliced: dict[str, HistoricalDataset] = {}
    for interval in required_intervals:
        if interval not in datasets:
            raise ValueError(f"missing interval {interval}")
        source = datasets[interval]
        candles = tuple(candle for candle in source.candles if candle.close_time <= as_of)
        minimum = minimums.get(interval, 1)
        if minimum <= 0:
            raise ValueError("minimum_bars values must be positive")
        if len(candles) < minimum:
            raise ValueError(
                f"insufficient {interval} history at replay cutoff: need {minimum}, have {len(candles)}"
            )
        sliced[interval] = build_history_dataset(
            candles,
            provider_symbol=source.manifest.provider_symbol,
            requested_bars=len(candles),
            fetched_at=as_of,
        )
    return build_mtf_bundle(
        sliced,
        as_of=as_of,
        required_intervals=required_intervals,
    )


def write_mtf_bundle(path: str | Path, bundle: MTFReplayBundle) -> Path:
    root = Path(path)
    root.mkdir(parents=True, exist_ok=True)
    files: dict[str, str] = {}
    for interval in bundle.manifest.intervals:
        filename = f"{interval}.jsonl"
        write_history_dataset(root / filename, bundle.datasets[interval])
        files[interval] = filename

    payload = _serialize_manifest(bundle.manifest)
    payload["history_files"] = files
    with (root / "bundle.json").open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n")
    return root


def load_mtf_bundle(path: str | Path) -> MTFReplayBundle:
    root = Path(path)
    payload = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
    files = payload.pop("history_files", None)
    if not isinstance(files, dict):
        raise ValueError("MTF bundle manifest has no history_files map")
    manifest = _deserialize_manifest(payload)
    if manifest.schema_version != MTF_BUNDLE_SCHEMA_VERSION:
        raise ValueError("unsupported MTF bundle schema version")
    datasets: dict[str, HistoricalDataset] = {}
    for interval in manifest.intervals:
        filename = files.get(interval)
        if not isinstance(filename, str) or Path(filename).name != filename:
            raise ValueError("invalid MTF bundle history filename")
        datasets[interval] = load_history_dataset(root / filename)
    rebuilt = build_mtf_bundle(
        datasets,
        as_of=manifest.as_of,
        required_intervals=manifest.intervals,
    )
    if rebuilt.manifest.bundle_sha256 != manifest.bundle_sha256:
        raise ValueError("MTF bundle digest mismatch")
    if dict(rebuilt.manifest.candle_counts) != dict(manifest.candle_counts):
        raise ValueError("MTF bundle candle-count mismatch")
    if dict(rebuilt.manifest.history_digests) != dict(manifest.history_digests):
        raise ValueError("MTF bundle history-digest mismatch")
    return MTFReplayBundle(manifest=manifest, datasets=datasets)


def _bundle_digest(
    *,
    provider_id: str,
    canonical_symbol: str,
    provider_symbol: str,
    as_of: datetime,
    required_intervals: tuple[str, ...],
    candle_counts: Mapping[str, int],
    history_digests: Mapping[str, str],
) -> str:
    payload = {
        "schema_version": MTF_BUNDLE_SCHEMA_VERSION,
        "provider_id": provider_id,
        "canonical_symbol": canonical_symbol,
        "provider_symbol": provider_symbol,
        "as_of": _time(as_of),
        "intervals": list(required_intervals),
        "candle_counts": {key: candle_counts[key] for key in required_intervals},
        "history_digests": {key: history_digests[key] for key in required_intervals},
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")
    return sha256(encoded).hexdigest()


def _serialize_manifest(manifest: MTFBundleManifest) -> dict[str, object]:
    payload = asdict(manifest)
    payload["as_of"] = _time(manifest.as_of)
    payload["intervals"] = list(manifest.intervals)
    payload["candle_counts"] = dict(manifest.candle_counts)
    payload["history_digests"] = dict(manifest.history_digests)
    return payload


def _deserialize_manifest(payload: Mapping[str, object]) -> MTFBundleManifest:
    counts = payload.get("candle_counts")
    digests = payload.get("history_digests")
    intervals = payload.get("intervals")
    if not isinstance(counts, dict) or not isinstance(digests, dict) or not isinstance(intervals, list):
        raise ValueError("invalid MTF bundle manifest mappings")
    return MTFBundleManifest(
        schema_version=str(payload["schema_version"]),
        provider_id=str(payload["provider_id"]),
        canonical_symbol=str(payload["canonical_symbol"]),
        provider_symbol=str(payload["provider_symbol"]),
        as_of=_parse_time(payload["as_of"]),
        intervals=tuple(str(item) for item in intervals),
        candle_counts={str(key): int(value) for key, value in counts.items()},
        history_digests={str(key): str(value) for key, value in digests.items()},
        bundle_sha256=str(payload["bundle_sha256"]),
    )


def _time(value: datetime) -> str:
    require_utc(value)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_time(value: object) -> datetime:
    text = str(value)
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    require_utc(parsed)
    return parsed.astimezone(timezone.utc)
