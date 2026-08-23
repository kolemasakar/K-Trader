from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from collections.abc import Mapping, Sequence

from ktrader.market.timeframes import require_utc
from ktrader.market.universe import UniverseCandidate, UniverseConfig, build_universe, liquidity_score
from ktrader.models import NormalizedInstrument, NormalizedTicker
from ktrader.providers.base import MarketDataProvider


UNIVERSE_SNAPSHOT_SCHEMA_VERSION = "ktrader.universe_snapshot.v1"
UNIVERSE_ARCHIVE_SCHEMA_VERSION = "ktrader.universe_archive.v1"


@dataclass(frozen=True, slots=True)
class UniverseSnapshotMember:
    rank: int
    instrument: NormalizedInstrument
    ticker: NormalizedTicker
    liquidity_score: Decimal


@dataclass(frozen=True, slots=True)
class UniverseSnapshot:
    schema_version: str
    provider_id: str
    captured_at: datetime
    config: UniverseConfig
    source_instrument_count: int
    source_ticker_count: int
    members: tuple[UniverseSnapshotMember, ...]
    content_sha256: str

    @property
    def universe_size(self) -> int:
        return len(self.members)


@dataclass(frozen=True, slots=True)
class UniverseSnapshotArchive:
    schema_version: str
    provider_id: str
    config: UniverseConfig
    snapshots: tuple[UniverseSnapshot, ...]
    archive_sha256: str


def build_universe_snapshot(
    provider_id: str,
    instruments: Sequence[NormalizedInstrument],
    tickers: Sequence[NormalizedTicker],
    config: UniverseConfig,
    *,
    captured_at: datetime,
) -> UniverseSnapshot:
    require_utc(captured_at)
    if not provider_id:
        raise ValueError("provider_id is required")
    if any(item.provider_id != provider_id for item in instruments):
        raise ValueError("universe snapshot cannot mix instrument providers")
    if any(item.provider_id != provider_id for item in tickers):
        raise ValueError("universe snapshot cannot mix ticker providers")
    if len({item.symbol for item in instruments}) != len(instruments):
        raise ValueError("universe snapshot instruments contain duplicate symbols")
    if len({item.symbol for item in tickers}) != len(tickers):
        raise ValueError("universe snapshot tickers contain duplicate symbols")
    for ticker in tickers:
        require_utc(ticker.timestamp)
        if ticker.timestamp > captured_at:
            raise ValueError("ticker timestamp cannot be after snapshot captured_at")

    candidates = build_universe(list(instruments), list(tickers), config)
    members = tuple(
        UniverseSnapshotMember(
            rank=rank,
            instrument=item.instrument,
            ticker=item.ticker,
            liquidity_score=item.liquidity_score,
        )
        for rank, item in enumerate(candidates, start=1)
    )
    digest = _snapshot_digest(
        provider_id=provider_id,
        captured_at=captured_at,
        config=config,
        source_instrument_count=len(instruments),
        source_ticker_count=len(tickers),
        members=members,
    )
    return UniverseSnapshot(
        schema_version=UNIVERSE_SNAPSHOT_SCHEMA_VERSION,
        provider_id=provider_id,
        captured_at=captured_at,
        config=config,
        source_instrument_count=len(instruments),
        source_ticker_count=len(tickers),
        members=members,
        content_sha256=digest,
    )


async def capture_universe_snapshot(
    provider: MarketDataProvider,
    config: UniverseConfig | None = None,
    *,
    captured_at: datetime | None = None,
) -> UniverseSnapshot:
    universe_config = config or UniverseConfig()
    instruments = await provider.list_instruments()
    tickers = await provider.get_tickers()
    capture_time = captured_at or datetime.now(timezone.utc)
    require_utc(capture_time)
    return build_universe_snapshot(
        provider.provider_id,
        instruments,
        tickers,
        universe_config,
        captured_at=capture_time,
    )


def build_universe_archive(
    snapshots: Sequence[UniverseSnapshot],
) -> UniverseSnapshotArchive:
    if not snapshots:
        raise ValueError("universe archive requires at least one snapshot")
    ordered = tuple(snapshots)
    first = ordered[0]
    provider_id = first.provider_id
    config = first.config
    previous: datetime | None = None
    for snapshot in ordered:
        _validate_snapshot(snapshot)
        if snapshot.provider_id != provider_id:
            raise ValueError("universe archive cannot mix providers")
        if snapshot.config != config:
            raise ValueError("universe archive cannot mix universe configurations")
        if previous is not None and snapshot.captured_at <= previous:
            raise ValueError("universe archive snapshots must be strictly chronological")
        previous = snapshot.captured_at
    digest = _archive_digest(provider_id, config, ordered)
    return UniverseSnapshotArchive(
        schema_version=UNIVERSE_ARCHIVE_SCHEMA_VERSION,
        provider_id=provider_id,
        config=config,
        snapshots=ordered,
        archive_sha256=digest,
    )


def append_universe_snapshot(
    archive: UniverseSnapshotArchive | None,
    snapshot: UniverseSnapshot,
) -> UniverseSnapshotArchive:
    if archive is None:
        return build_universe_archive((snapshot,))
    _validate_archive(archive)
    return build_universe_archive((*archive.snapshots, snapshot))


def write_universe_archive(path: str | Path, archive: UniverseSnapshotArchive) -> Path:
    _validate_archive(archive)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        manifest = {
            "record_type": "manifest",
            "schema_version": archive.schema_version,
            "provider_id": archive.provider_id,
            "config": _serialize_config(archive.config),
            "snapshot_count": len(archive.snapshots),
            "archive_sha256": archive.archive_sha256,
        }
        handle.write(json.dumps(manifest, sort_keys=True, ensure_ascii=True) + "\n")
        for snapshot in archive.snapshots:
            payload = _serialize_snapshot(snapshot)
            payload["record_type"] = "snapshot"
            handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n")
    return target


def load_universe_archive(path: str | Path) -> UniverseSnapshotArchive:
    rows = [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) < 2:
        raise ValueError("universe archive is incomplete")
    manifest = rows[0]
    if manifest.get("record_type") != "manifest":
        raise ValueError("universe archive has no manifest record")
    if manifest.get("schema_version") != UNIVERSE_ARCHIVE_SCHEMA_VERSION:
        raise ValueError("unsupported universe archive schema version")
    snapshots = tuple(_deserialize_snapshot(row) for row in rows[1:])
    rebuilt = build_universe_archive(snapshots)
    if rebuilt.provider_id != str(manifest.get("provider_id")):
        raise ValueError("universe archive provider mismatch")
    if rebuilt.config != _deserialize_config(manifest.get("config")):
        raise ValueError("universe archive config mismatch")
    if len(snapshots) != int(manifest.get("snapshot_count", -1)):
        raise ValueError("universe archive snapshot-count mismatch")
    if rebuilt.archive_sha256 != str(manifest.get("archive_sha256")):
        raise ValueError("universe archive digest mismatch")
    return rebuilt


def _validate_archive(archive: UniverseSnapshotArchive) -> None:
    if archive.schema_version != UNIVERSE_ARCHIVE_SCHEMA_VERSION:
        raise ValueError("unsupported universe archive schema version")
    rebuilt = build_universe_archive(archive.snapshots)
    if rebuilt.provider_id != archive.provider_id or rebuilt.config != archive.config:
        raise ValueError("universe archive identity mismatch")
    if rebuilt.archive_sha256 != archive.archive_sha256:
        raise ValueError("universe archive digest mismatch")


def _validate_snapshot(snapshot: UniverseSnapshot) -> None:
    if snapshot.schema_version != UNIVERSE_SNAPSHOT_SCHEMA_VERSION:
        raise ValueError("unsupported universe snapshot schema version")
    require_utc(snapshot.captured_at)
    if snapshot.source_instrument_count < 0 or snapshot.source_ticker_count < 0:
        raise ValueError("snapshot source counts cannot be negative")
    instruments = [member.instrument for member in snapshot.members]
    tickers = [member.ticker for member in snapshot.members]
    expected = build_universe(instruments, tickers, snapshot.config)
    if len(expected) != len(snapshot.members):
        raise ValueError("snapshot members do not reproduce configured universe")
    for rank, (member, candidate) in enumerate(zip(snapshot.members, expected), start=1):
        if member.rank != rank:
            raise ValueError("snapshot ranks must be contiguous from one")
        if member.instrument.provider_id != snapshot.provider_id or member.ticker.provider_id != snapshot.provider_id:
            raise ValueError("snapshot member provider mismatch")
        if member.instrument.symbol != member.ticker.symbol:
            raise ValueError("snapshot member instrument/ticker symbol mismatch")
        if member.instrument.symbol != candidate.instrument.symbol:
            raise ValueError("snapshot member order does not reproduce liquidity ranking")
        if member.liquidity_score != candidate.liquidity_score:
            raise ValueError("snapshot liquidity score mismatch")
        if member.liquidity_score != liquidity_score(member.ticker):
            raise ValueError("snapshot liquidity score is not reproducible from ticker")
        require_utc(member.ticker.timestamp)
        if member.ticker.timestamp > snapshot.captured_at:
            raise ValueError("snapshot ticker timestamp is after captured_at")
    expected_digest = _snapshot_digest(
        provider_id=snapshot.provider_id,
        captured_at=snapshot.captured_at,
        config=snapshot.config,
        source_instrument_count=snapshot.source_instrument_count,
        source_ticker_count=snapshot.source_ticker_count,
        members=snapshot.members,
    )
    if expected_digest != snapshot.content_sha256:
        raise ValueError("universe snapshot digest mismatch")


def _snapshot_digest(
    *,
    provider_id: str,
    captured_at: datetime,
    config: UniverseConfig,
    source_instrument_count: int,
    source_ticker_count: int,
    members: Sequence[UniverseSnapshotMember],
) -> str:
    payload = {
        "schema_version": UNIVERSE_SNAPSHOT_SCHEMA_VERSION,
        "provider_id": provider_id,
        "captured_at": _time(captured_at),
        "config": _serialize_config(config),
        "source_instrument_count": source_instrument_count,
        "source_ticker_count": source_ticker_count,
        "members": [_serialize_member(member) for member in members],
    }
    return _digest(payload)


def _archive_digest(
    provider_id: str,
    config: UniverseConfig,
    snapshots: Sequence[UniverseSnapshot],
) -> str:
    return _digest({
        "schema_version": UNIVERSE_ARCHIVE_SCHEMA_VERSION,
        "provider_id": provider_id,
        "config": _serialize_config(config),
        "snapshot_digests": [snapshot.content_sha256 for snapshot in snapshots],
    })


def _serialize_snapshot(snapshot: UniverseSnapshot) -> dict[str, object]:
    return {
        "schema_version": snapshot.schema_version,
        "provider_id": snapshot.provider_id,
        "captured_at": _time(snapshot.captured_at),
        "config": _serialize_config(snapshot.config),
        "source_instrument_count": snapshot.source_instrument_count,
        "source_ticker_count": snapshot.source_ticker_count,
        "members": [_serialize_member(member) for member in snapshot.members],
        "content_sha256": snapshot.content_sha256,
    }


def _deserialize_snapshot(payload: Mapping[str, object]) -> UniverseSnapshot:
    if payload.get("record_type") not in (None, "snapshot"):
        raise ValueError("invalid universe snapshot record type")
    raw_members = payload.get("members")
    if not isinstance(raw_members, list):
        raise ValueError("universe snapshot members must be a list")
    snapshot = UniverseSnapshot(
        schema_version=str(payload.get("schema_version")),
        provider_id=str(payload.get("provider_id")),
        captured_at=_parse_time(payload.get("captured_at")),
        config=_deserialize_config(payload.get("config")),
        source_instrument_count=int(payload.get("source_instrument_count", -1)),
        source_ticker_count=int(payload.get("source_ticker_count", -1)),
        members=tuple(_deserialize_member(item) for item in raw_members),
        content_sha256=str(payload.get("content_sha256")),
    )
    _validate_snapshot(snapshot)
    return snapshot


def _serialize_member(member: UniverseSnapshotMember) -> dict[str, object]:
    return {
        "rank": member.rank,
        "instrument": _serialize_instrument(member.instrument),
        "ticker": _serialize_ticker(member.ticker),
        "liquidity_score": format(member.liquidity_score, "f"),
    }


def _deserialize_member(payload: Mapping[str, object]) -> UniverseSnapshotMember:
    instrument = payload.get("instrument")
    ticker = payload.get("ticker")
    if not isinstance(instrument, dict) or not isinstance(ticker, dict):
        raise ValueError("invalid universe snapshot member")
    return UniverseSnapshotMember(
        rank=int(payload["rank"]),
        instrument=_deserialize_instrument(instrument),
        ticker=_deserialize_ticker(ticker),
        liquidity_score=Decimal(str(payload["liquidity_score"])),
    )


def _serialize_config(config: UniverseConfig) -> dict[str, object]:
    return {
        "quote_asset": config.quote_asset,
        "price_limit_enabled": config.price_limit_enabled,
        "max_price": format(config.max_price, "f"),
        "max_candidates": config.max_candidates,
    }


def _deserialize_config(payload: object) -> UniverseConfig:
    if not isinstance(payload, dict):
        raise ValueError("invalid universe config")
    return UniverseConfig(
        quote_asset=str(payload["quote_asset"]),
        price_limit_enabled=bool(payload["price_limit_enabled"]),
        max_price=Decimal(str(payload["max_price"])),
        max_candidates=int(payload["max_candidates"]),
    )


def _serialize_instrument(instrument: NormalizedInstrument) -> dict[str, object]:
    return {
        "provider_id": instrument.provider_id,
        "symbol": instrument.symbol,
        "base_asset": instrument.base_asset,
        "quote_asset": instrument.quote_asset,
        "market_type": instrument.market_type,
        "contract_type": instrument.contract_type,
        "status": instrument.status,
        "price_tick": _decimal(instrument.price_tick),
        "quantity_step": _decimal(instrument.quantity_step),
        "provider_symbol": instrument.provider_symbol,
        "metadata": dict(instrument.metadata),
    }


def _deserialize_instrument(payload: Mapping[str, object]) -> NormalizedInstrument:
    metadata = payload.get("metadata")
    return NormalizedInstrument(
        provider_id=str(payload["provider_id"]),
        symbol=str(payload["symbol"]),
        base_asset=str(payload["base_asset"]),
        quote_asset=str(payload["quote_asset"]),
        market_type=str(payload["market_type"]),
        contract_type=str(payload["contract_type"]),
        status=str(payload["status"]),
        price_tick=_optional_decimal(payload.get("price_tick")),
        quantity_step=_optional_decimal(payload.get("quantity_step")),
        provider_symbol=str(payload["provider_symbol"]) if payload.get("provider_symbol") is not None else None,
        metadata={str(key): str(value) for key, value in metadata.items()} if isinstance(metadata, dict) else {},
    )


def _serialize_ticker(ticker: NormalizedTicker) -> dict[str, object]:
    return {
        "provider_id": ticker.provider_id,
        "symbol": ticker.symbol,
        "timestamp": _time(ticker.timestamp),
        "last_price": format(ticker.last_price, "f"),
        "quote_volume_24h": _decimal(ticker.quote_volume_24h),
        "base_volume_24h": _decimal(ticker.base_volume_24h),
        "trade_count_24h": ticker.trade_count_24h,
        "bid_price": _decimal(ticker.bid_price),
        "ask_price": _decimal(ticker.ask_price),
        "open_interest": _decimal(ticker.open_interest),
    }


def _deserialize_ticker(payload: Mapping[str, object]) -> NormalizedTicker:
    return NormalizedTicker(
        provider_id=str(payload["provider_id"]),
        symbol=str(payload["symbol"]),
        timestamp=_parse_time(payload["timestamp"]),
        last_price=Decimal(str(payload["last_price"])),
        quote_volume_24h=_optional_decimal(payload.get("quote_volume_24h")),
        base_volume_24h=_optional_decimal(payload.get("base_volume_24h")),
        trade_count_24h=int(payload["trade_count_24h"]) if payload.get("trade_count_24h") is not None else None,
        bid_price=_optional_decimal(payload.get("bid_price")),
        ask_price=_optional_decimal(payload.get("ask_price")),
        open_interest=_optional_decimal(payload.get("open_interest")),
    )


def _digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(raw.encode("ascii")).hexdigest()


def _decimal(value: Decimal | None) -> str | None:
    return None if value is None else format(value, "f")


def _optional_decimal(value: object) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _time(value: datetime) -> str:
    require_utc(value)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _parse_time(value: object) -> datetime:
    text = str(value)
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    require_utc(parsed)
    return parsed.astimezone(timezone.utc)
