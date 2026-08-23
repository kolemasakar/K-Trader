from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from collections.abc import Mapping

from ktrader.replay.study import ReplayStudyConfig, ReplayStudyContext, ReplayStudyResult
from ktrader.runtime.models import RuntimeScannerConfig


STUDY_RUN_PROVENANCE_SCHEMA_VERSION = "ktrader.study_run_provenance.v1"


@dataclass(frozen=True, slots=True)
class ReplayStudyArtifactInfo:
    schema_version: str
    study_id: str
    bundle_sha256: str
    provider_id: str
    canonical_symbol: str
    analyzed_cutoffs: int
    unique_tradable_signals: int
    binary_resolved_count: int
    decision_ids: tuple[str, ...]
    binary_outcomes: Mapping[str, Mapping[str, object]]
    file_sha256: str


@dataclass(frozen=True, slots=True)
class StudyRunProvenance:
    schema_version: str
    study_id: str
    provider_id: str
    canonical_symbol: str
    bundle_sha256: str
    cohort_sha256: str
    context_sha256: str
    scanner_config_sha256: str
    study_config_sha256: str
    replay_study_sha256: str
    provenance_sha256: str


def replay_context_sha256(context: ReplayStudyContext) -> str:
    return _digest(_jsonable(asdict(context)))


def scanner_config_sha256(config: RuntimeScannerConfig) -> str:
    return _digest(_jsonable(asdict(config)))


def study_config_sha256(config: ReplayStudyConfig) -> str:
    return _digest(_jsonable(asdict(config)))


def file_sha256(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_replay_study(path: str | Path) -> ReplayStudyArtifactInfo:
    target = Path(path)
    rows = [
        json.loads(line)
        for line in target.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not rows:
        raise ValueError("replay study artifact is empty")
    manifest = rows[0]
    if manifest.get("record_type") != "manifest":
        raise ValueError("replay study artifact has no manifest")
    if manifest.get("schema_version") != "ktrader.replay_study.v1":
        raise ValueError("unsupported replay study schema version")
    if manifest.get("estimated_probability") is not None:
        raise ValueError("replay study must not contain estimated probability")

    study_id = _require_sha256(manifest.get("study_id"), "study_id")
    bundle_sha256 = _require_sha256(manifest.get("bundle_sha256"), "bundle_sha256")
    provider_id = str(manifest.get("provider_id") or "")
    symbol = str(manifest.get("canonical_symbol") or "")
    if not provider_id or not symbol:
        raise ValueError("replay study provider/symbol identity is required")

    decision_ids: list[str] = []
    seen_ids: set[str] = set()
    signal_keys: set[str] = set()
    binary_outcomes: dict[str, Mapping[str, object]] = {}
    outcome_counts: dict[str, int] = {}

    for row in rows[1:]:
        if row.get("record_type") != "decision":
            raise ValueError("unexpected replay study record type")
        decision_id = _require_sha256(row.get("decision_id"), "decision_id")
        if decision_id in seen_ids:
            raise ValueError("duplicate replay study decision_id")
        seen_ids.add(decision_id)
        decision_ids.append(decision_id)

        decision = row.get("decision")
        if not isinstance(decision, dict):
            raise ValueError("replay study decision payload is invalid")
        if str(decision.get("provider_id")) != provider_id or str(decision.get("canonical_symbol")) != symbol:
            raise ValueError("replay study decision identity mismatch")
        if decision.get("estimated_probability") is not None:
            raise ValueError("replay decision must not contain estimated probability")

        signal_key = row.get("signal_key")
        if signal_key is not None:
            signal_keys.add(_require_sha256(signal_key, "signal_key"))

        outcome = row.get("outcome")
        if outcome is None:
            continue
        if not isinstance(outcome, dict):
            raise ValueError("replay study outcome payload is invalid")
        if str(outcome.get("decision_id")) != decision_id:
            raise ValueError("replay study outcome decision_id mismatch")
        if str(outcome.get("provider_id")) != provider_id or str(outcome.get("canonical_symbol")) != symbol:
            raise ValueError("replay study outcome identity mismatch")
        status = str(outcome.get("status") or "")
        if not status:
            raise ValueError("replay study outcome status is required")
        outcome_counts[status] = outcome_counts.get(status, 0) + 1
        if status in {"WIN", "LOSS"}:
            binary_outcomes[decision_id] = outcome

    analyzed = int(manifest.get("analyzed_cutoffs", -1))
    unique_signals = int(manifest.get("unique_tradable_signals", -1))
    binary_count = int(manifest.get("binary_resolved_count", -1))
    if analyzed != len(decision_ids):
        raise ValueError("replay study analyzed_cutoffs mismatch")
    if unique_signals != len(signal_keys):
        raise ValueError("replay study unique_tradable_signals mismatch")
    if binary_count != len(binary_outcomes):
        raise ValueError("replay study binary_resolved_count mismatch")
    raw_counts = manifest.get("outcome_counts")
    if not isinstance(raw_counts, dict):
        raise ValueError("replay study outcome_counts are invalid")
    normalized_counts = {str(key): int(value) for key, value in raw_counts.items()}
    if normalized_counts != dict(sorted(outcome_counts.items())):
        raise ValueError("replay study outcome_counts mismatch")

    return ReplayStudyArtifactInfo(
        schema_version="ktrader.replay_study.v1",
        study_id=study_id,
        bundle_sha256=bundle_sha256,
        provider_id=provider_id,
        canonical_symbol=symbol,
        analyzed_cutoffs=analyzed,
        unique_tradable_signals=unique_signals,
        binary_resolved_count=binary_count,
        decision_ids=tuple(decision_ids),
        binary_outcomes=dict(binary_outcomes),
        file_sha256=file_sha256(target),
    )


def build_study_run_provenance(
    result: ReplayStudyResult,
    replay_study_path: str | Path,
    context: ReplayStudyContext,
    scanner_config: RuntimeScannerConfig,
    study_config: ReplayStudyConfig,
    *,
    cohort_sha256: str,
) -> StudyRunProvenance:
    cohort_digest = _require_sha256(cohort_sha256, "cohort_sha256")
    info = inspect_replay_study(replay_study_path)
    if info.study_id != result.study_id or info.bundle_sha256 != result.bundle_sha256:
        raise ValueError("replay study file does not match ReplayStudyResult")
    if info.provider_id != result.provider_id or info.canonical_symbol != result.canonical_symbol:
        raise ValueError("replay study result identity mismatch")
    instrument = context.instrument
    if instrument.provider_id != result.provider_id or instrument.symbol != result.canonical_symbol:
        raise ValueError("replay context identity does not match study")

    fields = {
        "schema_version": STUDY_RUN_PROVENANCE_SCHEMA_VERSION,
        "study_id": result.study_id,
        "provider_id": result.provider_id,
        "canonical_symbol": result.canonical_symbol,
        "bundle_sha256": result.bundle_sha256,
        "cohort_sha256": cohort_digest,
        "context_sha256": replay_context_sha256(context),
        "scanner_config_sha256": scanner_config_sha256(scanner_config),
        "study_config_sha256": study_config_sha256(study_config),
        "replay_study_sha256": info.file_sha256,
    }
    return StudyRunProvenance(
        **fields,
        provenance_sha256=_digest(fields),
    )


def write_study_run_provenance(path: str | Path, provenance: StudyRunProvenance) -> Path:
    _validate_provenance(provenance)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(asdict(provenance), sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return target


def load_study_run_provenance(path: str | Path) -> StudyRunProvenance:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    provenance = StudyRunProvenance(
        schema_version=str(payload.get("schema_version")),
        study_id=str(payload.get("study_id")),
        provider_id=str(payload.get("provider_id")),
        canonical_symbol=str(payload.get("canonical_symbol")),
        bundle_sha256=str(payload.get("bundle_sha256")),
        cohort_sha256=str(payload.get("cohort_sha256")),
        context_sha256=str(payload.get("context_sha256")),
        scanner_config_sha256=str(payload.get("scanner_config_sha256")),
        study_config_sha256=str(payload.get("study_config_sha256")),
        replay_study_sha256=str(payload.get("replay_study_sha256")),
        provenance_sha256=str(payload.get("provenance_sha256")),
    )
    _validate_provenance(provenance)
    return provenance


def _validate_provenance(provenance: StudyRunProvenance) -> None:
    if provenance.schema_version != STUDY_RUN_PROVENANCE_SCHEMA_VERSION:
        raise ValueError("unsupported study-run provenance schema version")
    if not provenance.provider_id or not provenance.canonical_symbol:
        raise ValueError("study-run provenance identity is required")
    for name in (
        "study_id",
        "bundle_sha256",
        "cohort_sha256",
        "context_sha256",
        "scanner_config_sha256",
        "study_config_sha256",
        "replay_study_sha256",
        "provenance_sha256",
    ):
        _require_sha256(getattr(provenance, name), name)
    fields = asdict(provenance)
    supplied = fields.pop("provenance_sha256")
    if _digest(fields) != supplied:
        raise ValueError("study-run provenance digest mismatch")


def _require_sha256(value: object, name: str) -> str:
    text = str(value or "")
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text.lower()):
        raise ValueError(f"{name} must be a SHA-256 hex digest")
    return text.lower()


def _jsonable(value: object) -> object:
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("datetime must be timezone-aware")
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        values = [_jsonable(item) for item in value]
        return sorted(values) if isinstance(value, (set, frozenset)) else values
    return value


def _digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(raw.encode("ascii")).hexdigest()
