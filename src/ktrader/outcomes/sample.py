from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from collections.abc import Mapping, Sequence

from ktrader.outcomes.evaluator import SignalOutcome
from ktrader.outcomes.storage import OutcomeRepository
from ktrader.replay.provenance import StudyRunProvenance, inspect_replay_study


OUTCOME_SAMPLE_SCHEMA_VERSION = "ktrader.outcome_sample.v1"


@dataclass(frozen=True, slots=True)
class OutcomeSample:
    schema_version: str
    source_study_id: str
    source_replay_study_sha256: str
    provider_id: str
    canonical_symbol: str
    statuses: tuple[str, ...]
    outcomes: tuple[SignalOutcome, ...]
    content_sha256: str

    @property
    def record_count(self) -> int:
        return len(self.outcomes)


def build_outcome_sample(
    outcomes: Sequence[SignalOutcome],
    *,
    source_study_id: str,
    source_replay_study_sha256: str,
    provider_id: str,
    canonical_symbol: str,
) -> OutcomeSample:
    study_id = _require_sha256(source_study_id, "source_study_id")
    study_sha = _require_sha256(source_replay_study_sha256, "source_replay_study_sha256")
    if not provider_id or not canonical_symbol:
        raise ValueError("outcome sample provider/symbol identity is required")
    ordered = tuple(sorted(outcomes, key=lambda item: (item.decision_time, item.decision_id)))
    seen: set[str] = set()
    for outcome in ordered:
        if outcome.status not in {"WIN", "LOSS"}:
            raise ValueError("outcome sample accepts only binary WIN/LOSS outcomes")
        if outcome.provider_id != provider_id or outcome.canonical_symbol != canonical_symbol:
            raise ValueError("outcome sample cannot mix provider/symbol identity")
        if outcome.decision_id in seen:
            raise ValueError("outcome sample contains duplicate decision_id")
        _require_sha256(outcome.decision_id, "decision_id")
        seen.add(outcome.decision_id)

    fields = {
        "schema_version": OUTCOME_SAMPLE_SCHEMA_VERSION,
        "source_study_id": study_id,
        "source_replay_study_sha256": study_sha,
        "provider_id": provider_id,
        "canonical_symbol": canonical_symbol,
        "statuses": ["LOSS", "WIN"],
        "outcomes": [_outcome_payload(outcome) for outcome in ordered],
    }
    return OutcomeSample(
        schema_version=OUTCOME_SAMPLE_SCHEMA_VERSION,
        source_study_id=study_id,
        source_replay_study_sha256=study_sha,
        provider_id=provider_id,
        canonical_symbol=canonical_symbol,
        statuses=("LOSS", "WIN"),
        outcomes=ordered,
        content_sha256=_digest(fields),
    )


def build_outcome_sample_from_repository(
    replay_study_path: str | Path,
    provenance: StudyRunProvenance,
    repository: OutcomeRepository,
) -> OutcomeSample:
    info = inspect_replay_study(replay_study_path)
    if provenance.study_id != info.study_id or provenance.replay_study_sha256 != info.file_sha256:
        raise ValueError("study provenance does not match replay study artifact")
    if provenance.provider_id != info.provider_id or provenance.canonical_symbol != info.canonical_symbol:
        raise ValueError("study provenance identity mismatch")

    outcomes: list[SignalOutcome] = []
    for decision_id, expected in info.binary_outcomes.items():
        stored = repository.get(decision_id)
        if stored is None:
            raise ValueError(f"binary replay outcome missing from OutcomeRepository: {decision_id}")
        if stored.status not in {"WIN", "LOSS"}:
            raise ValueError("OutcomeRepository binary outcome status mismatch")
        if _outcome_payload(stored) != _normalize_json(expected):
            raise ValueError("OutcomeRepository outcome differs from replay study artifact")
        outcomes.append(stored)

    return build_outcome_sample(
        outcomes,
        source_study_id=info.study_id,
        source_replay_study_sha256=info.file_sha256,
        provider_id=info.provider_id,
        canonical_symbol=info.canonical_symbol,
    )


def write_outcome_sample(path: str | Path, sample: OutcomeSample) -> Path:
    _validate_sample(sample)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="\n") as handle:
        manifest = {
            "record_type": "manifest",
            "schema_version": sample.schema_version,
            "source_study_id": sample.source_study_id,
            "source_replay_study_sha256": sample.source_replay_study_sha256,
            "provider_id": sample.provider_id,
            "canonical_symbol": sample.canonical_symbol,
            "statuses": list(sample.statuses),
            "record_count": sample.record_count,
            "content_sha256": sample.content_sha256,
        }
        handle.write(json.dumps(manifest, sort_keys=True, ensure_ascii=True) + "\n")
        for outcome in sample.outcomes:
            payload = _outcome_payload(outcome)
            payload["record_type"] = "outcome"
            handle.write(json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n")
    return target


def load_outcome_sample(path: str | Path) -> OutcomeSample:
    rows = [
        json.loads(line)
        for line in Path(path).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows or rows[0].get("record_type") != "manifest":
        raise ValueError("outcome sample has no manifest")
    manifest = rows[0]
    if manifest.get("schema_version") != OUTCOME_SAMPLE_SCHEMA_VERSION:
        raise ValueError("unsupported outcome sample schema version")
    outcomes = tuple(_outcome_from_payload(row) for row in rows[1:])
    if len(outcomes) != int(manifest.get("record_count", -1)):
        raise ValueError("outcome sample record_count mismatch")
    raw_statuses = manifest.get("statuses")
    if not isinstance(raw_statuses, list):
        raise ValueError("outcome sample statuses are invalid")
    sample = build_outcome_sample(
        outcomes,
        source_study_id=str(manifest.get("source_study_id")),
        source_replay_study_sha256=str(manifest.get("source_replay_study_sha256")),
        provider_id=str(manifest.get("provider_id")),
        canonical_symbol=str(manifest.get("canonical_symbol")),
    )
    if tuple(str(value) for value in raw_statuses) != sample.statuses:
        raise ValueError("outcome sample statuses mismatch")
    if str(manifest.get("content_sha256")) != sample.content_sha256:
        raise ValueError("outcome sample digest mismatch")
    return sample


def _validate_sample(sample: OutcomeSample) -> None:
    rebuilt = build_outcome_sample(
        sample.outcomes,
        source_study_id=sample.source_study_id,
        source_replay_study_sha256=sample.source_replay_study_sha256,
        provider_id=sample.provider_id,
        canonical_symbol=sample.canonical_symbol,
    )
    if sample.schema_version != OUTCOME_SAMPLE_SCHEMA_VERSION:
        raise ValueError("unsupported outcome sample schema version")
    if sample.statuses != rebuilt.statuses or sample.content_sha256 != rebuilt.content_sha256:
        raise ValueError("outcome sample integrity mismatch")


def _outcome_payload(outcome: SignalOutcome) -> dict[str, object]:
    return _normalize_json(asdict(outcome))


def _outcome_from_payload(payload: Mapping[str, object]) -> SignalOutcome:
    if payload.get("record_type") not in (None, "outcome"):
        raise ValueError("invalid outcome sample record type")
    return SignalOutcome(
        decision_id=str(payload["decision_id"]),
        provider_id=str(payload["provider_id"]),
        canonical_symbol=str(payload["canonical_symbol"]),
        side=str(payload["side"]),
        grade=str(payload["grade"]),
        setup_score=int(payload["setup_score"]),
        setup_type=str(payload["setup_type"]),
        engine_version=str(payload["engine_version"]),
        decision_time=_parse_time(payload["decision_time"]),
        entry=_optional_decimal(payload.get("entry")),
        stop=_optional_decimal(payload.get("stop")),
        target=_optional_decimal(payload.get("target")),
        planned_rr=_optional_decimal(payload.get("planned_rr")),
        status=str(payload["status"]),
        entry_bar_open_time=_optional_time(payload.get("entry_bar_open_time")),
        resolved_bar_open_time=_optional_time(payload.get("resolved_bar_open_time")),
        bars_to_entry=int(payload["bars_to_entry"]) if payload.get("bars_to_entry") is not None else None,
        bars_in_trade=int(payload["bars_in_trade"]) if payload.get("bars_in_trade") is not None else None,
        outcome_r=_optional_decimal(payload.get("outcome_r")),
        reason=str(payload["reason"]) if payload.get("reason") is not None else None,
        evaluated_at=_parse_time(payload["evaluated_at"]),
    )


def _normalize_json(value: object) -> object:
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("outcome datetime must be timezone-aware")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Mapping):
        return {str(key): _normalize_json(item) for key, item in value.items() if key != "record_type"}
    if isinstance(value, (list, tuple)):
        return [_normalize_json(item) for item in value]
    return value


def _optional_decimal(value: object) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _optional_time(value: object) -> datetime | None:
    return None if value is None else _parse_time(value)


def _parse_time(value: object) -> datetime:
    text = str(value)
    parsed = datetime.fromisoformat(text[:-1] + "+00:00" if text.endswith("Z") else text)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("outcome datetime must be timezone-aware")
    return parsed.astimezone(timezone.utc)


def _require_sha256(value: object, name: str) -> str:
    text = str(value or "").lower()
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise ValueError(f"{name} must be a SHA-256 hex digest")
    return text


def _digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(raw.encode("ascii")).hexdigest()
