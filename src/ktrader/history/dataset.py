from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from collections.abc import Sequence

from ktrader.market.validation import validate_sequence
from ktrader.models import NormalizedCandle


HISTORY_SCHEMA_VERSION = "ktrader.history.v1"


@dataclass(frozen=True, slots=True)
class HistoryManifest:
    schema_version: str
    provider_id: str
    canonical_symbol: str
    provider_symbol: str
    interval: str
    requested_bars: int
    actual_start: datetime
    actual_end: datetime
    candle_count: int
    fetched_at: datetime
    source_kind: str
    content_sha256: str


@dataclass(frozen=True, slots=True)
class HistoricalDataset:
    manifest: HistoryManifest
    candles: tuple[NormalizedCandle, ...]


def build_history_dataset(
    candles: Sequence[NormalizedCandle],
    *,
    provider_symbol: str,
    requested_bars: int | None = None,
    fetched_at: datetime | None = None,
) -> HistoricalDataset:
    if not candles:
        raise ValueError("historical dataset cannot be empty")
    first = candles[0]
    validate_sequence(
        candles,
        provider_id=first.provider_id,
        symbol=first.symbol,
        interval=first.interval,
        require_closed=True,
        require_contiguous=True,
    )
    current = fetched_at or datetime.now(timezone.utc)
    _require_utc(current)
    materialized = tuple(candles)
    requested = requested_bars if requested_bars is not None else len(materialized)
    if requested <= 0:
        raise ValueError("requested_bars must be positive")
    manifest = HistoryManifest(
        schema_version=HISTORY_SCHEMA_VERSION,
        provider_id=first.provider_id,
        canonical_symbol=first.symbol,
        provider_symbol=provider_symbol,
        interval=first.interval,
        requested_bars=requested,
        actual_start=materialized[0].open_time,
        actual_end=materialized[-1].close_time,
        candle_count=len(materialized),
        fetched_at=current,
        source_kind="provider",
        content_sha256=candle_content_digest(materialized),
    )
    return HistoricalDataset(manifest, materialized)


def candle_content_digest(candles: Sequence[NormalizedCandle]) -> str:
    payload = "\n".join(
        json.dumps(_serialize_candle(candle), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        for candle in candles
    )
    return sha256(payload.encode("ascii")).hexdigest()


def write_history_dataset(path: str | Path, dataset: HistoricalDataset) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps({"record_type": "manifest", **_serialize_manifest(dataset.manifest)}, sort_keys=True, ensure_ascii=True) + "\n")
        for candle in dataset.candles:
            handle.write(json.dumps({"record_type": "candle", **_serialize_candle(candle)}, sort_keys=True, ensure_ascii=True) + "\n")
    return target


def load_history_dataset(path: str | Path) -> HistoricalDataset:
    target = Path(path)
    with target.open("r", encoding="utf-8") as handle:
        lines = [line.strip() for line in handle if line.strip()]
    if len(lines) < 2:
        raise ValueError("history dataset must contain manifest and candles")
    first = json.loads(lines[0])
    if first.pop("record_type", None) != "manifest":
        raise ValueError("history dataset first record must be manifest")
    manifest = _deserialize_manifest(first)
    if manifest.schema_version != HISTORY_SCHEMA_VERSION:
        raise ValueError("unsupported history dataset schema version")
    if manifest.source_kind != "provider":
        raise ValueError("history dataset source_kind must be provider")
    candles: list[NormalizedCandle] = []
    for line in lines[1:]:
        payload = json.loads(line)
        if payload.pop("record_type", None) != "candle":
            raise ValueError("history dataset contains non-candle record after manifest")
        candles.append(_deserialize_candle(payload))
    dataset = build_history_dataset(
        candles,
        provider_symbol=manifest.provider_symbol,
        requested_bars=manifest.requested_bars,
        fetched_at=manifest.fetched_at,
    )
    if dataset.manifest.content_sha256 != manifest.content_sha256:
        raise ValueError("history dataset content digest mismatch")
    if dataset.manifest.provider_id != manifest.provider_id or dataset.manifest.canonical_symbol != manifest.canonical_symbol or dataset.manifest.interval != manifest.interval:
        raise ValueError("history dataset manifest identity mismatch")
    if dataset.manifest.candle_count != manifest.candle_count or dataset.manifest.actual_start != manifest.actual_start or dataset.manifest.actual_end != manifest.actual_end:
        raise ValueError("history dataset manifest range mismatch")
    return HistoricalDataset(manifest, tuple(candles))


def _serialize_manifest(manifest: HistoryManifest) -> dict[str, object]:
    payload = asdict(manifest)
    for key in ("actual_start", "actual_end", "fetched_at"):
        payload[key] = _time(payload[key])
    return payload


def _deserialize_manifest(payload: dict[str, object]) -> HistoryManifest:
    return HistoryManifest(
        schema_version=str(payload["schema_version"]),
        provider_id=str(payload["provider_id"]),
        canonical_symbol=str(payload["canonical_symbol"]),
        provider_symbol=str(payload["provider_symbol"]),
        interval=str(payload["interval"]),
        requested_bars=int(payload["requested_bars"]),
        actual_start=_parse_time(payload["actual_start"]),
        actual_end=_parse_time(payload["actual_end"]),
        candle_count=int(payload["candle_count"]),
        fetched_at=_parse_time(payload["fetched_at"]),
        source_kind=str(payload["source_kind"]),
        content_sha256=str(payload["content_sha256"]),
    )


def _serialize_candle(candle: NormalizedCandle) -> dict[str, object]:
    return {
        "provider_id": candle.provider_id,
        "symbol": candle.symbol,
        "interval": candle.interval,
        "open_time": _time(candle.open_time),
        "close_time": _time(candle.close_time),
        "open": format(candle.open, "f"),
        "high": format(candle.high, "f"),
        "low": format(candle.low, "f"),
        "close": format(candle.close, "f"),
        "volume": format(candle.volume, "f"),
        "quote_volume": _decimal(candle.quote_volume),
        "trade_count": candle.trade_count,
        "taker_buy_volume": _decimal(candle.taker_buy_volume),
        "taker_buy_quote_volume": _decimal(candle.taker_buy_quote_volume),
        "closed": candle.closed,
    }


def _deserialize_candle(payload: dict[str, object]) -> NormalizedCandle:
    return NormalizedCandle(
        provider_id=str(payload["provider_id"]),
        symbol=str(payload["symbol"]),
        interval=str(payload["interval"]),
        open_time=_parse_time(payload["open_time"]),
        close_time=_parse_time(payload["close_time"]),
        open=Decimal(str(payload["open"])),
        high=Decimal(str(payload["high"])),
        low=Decimal(str(payload["low"])),
        close=Decimal(str(payload["close"])),
        volume=Decimal(str(payload["volume"])),
        quote_volume=_optional_decimal(payload.get("quote_volume")),
        trade_count=int(payload["trade_count"]) if payload.get("trade_count") is not None else None,
        taker_buy_volume=_optional_decimal(payload.get("taker_buy_volume")),
        taker_buy_quote_volume=_optional_decimal(payload.get("taker_buy_quote_volume")),
        closed=bool(payload["closed"]),
    )


def _decimal(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _optional_decimal(value: object) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _time(value: datetime) -> str:
    _require_utc(value)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_time(value: object) -> datetime:
    text = str(value)
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    _require_utc(parsed)
    return parsed.astimezone(timezone.utc)


def _require_utc(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None or value.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp must be timezone-aware UTC")
