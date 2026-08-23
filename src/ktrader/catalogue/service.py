from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from collections.abc import Sequence

from ktrader.history.bundle import load_mtf_bundle
from ktrader.history.universe import load_universe_archive
from ktrader.outcomes.sample import load_outcome_sample
from ktrader.replay.cohort import load_study_cohort
from ktrader.replay.provenance import (
    file_sha256,
    inspect_replay_study,
    load_study_run_provenance,
    replay_context_sha256,
)


CATALOGUE_SCHEMA_VERSION = "ktrader.dataset_catalogue.v1"


@dataclass(frozen=True, slots=True)
class ArtifactReference:
    kind: str
    schema_version: str
    path: str
    semantic_id: str
    content_sha256: str


@dataclass(frozen=True, slots=True)
class DatasetCatalogueEntry:
    entry_id: str
    provider_id: str
    canonical_symbol: str
    mtf_bundle: ArtifactReference
    universe_archive: ArtifactReference
    study_cohort: ArtifactReference
    replay_study: ArtifactReference
    study_provenance: ArtifactReference
    outcome_sample: ArtifactReference | None = None


@dataclass(frozen=True, slots=True)
class DatasetCatalogue:
    schema_version: str
    entries: tuple[DatasetCatalogueEntry, ...]
    catalogue_sha256: str


def path_content_sha256(path: str | Path) -> str:
    target = Path(path)
    if target.is_symlink():
        raise ValueError("catalogue artifacts cannot be symlinks")
    if target.is_file():
        return file_sha256(target)
    if not target.is_dir():
        raise ValueError(f"catalogue artifact does not exist: {target}")

    rows: list[tuple[str, str]] = []
    for item in sorted(target.rglob("*"), key=lambda value: value.relative_to(target).as_posix()):
        if item.is_symlink():
            raise ValueError("catalogue artifact trees cannot contain symlinks")
        if item.is_dir():
            continue
        if not item.is_file():
            raise ValueError("catalogue artifact tree contains unsupported filesystem entry")
        rows.append((item.relative_to(target).as_posix(), file_sha256(item)))
    if not rows:
        raise ValueError("catalogue artifact directory cannot be empty")
    return _digest(rows)


def build_catalogue_entry(
    artifact_root: str | Path,
    *,
    mtf_bundle_path: str | Path,
    universe_archive_path: str | Path,
    study_cohort_path: str | Path,
    replay_study_path: str | Path,
    study_provenance_path: str | Path,
    outcome_sample_path: str | Path | None = None,
) -> DatasetCatalogueEntry:
    root = Path(artifact_root).resolve()
    if not root.exists() or not root.is_dir():
        raise ValueError("artifact_root must be an existing directory")

    bundle_path = _resolve_inside(root, mtf_bundle_path)
    archive_path = _resolve_inside(root, universe_archive_path)
    cohort_path = _resolve_inside(root, study_cohort_path)
    study_path = _resolve_inside(root, replay_study_path)
    provenance_path = _resolve_inside(root, study_provenance_path)
    sample_path = _resolve_inside(root, outcome_sample_path) if outcome_sample_path is not None else None

    bundle = load_mtf_bundle(bundle_path)
    archive = load_universe_archive(archive_path)
    cohort = load_study_cohort(cohort_path)
    study = inspect_replay_study(study_path)
    provenance = load_study_run_provenance(provenance_path)

    provider_id = bundle.manifest.provider_id
    symbol = bundle.manifest.canonical_symbol
    if archive.provider_id != provider_id or cohort.provider_id != provider_id:
        raise ValueError("catalogue entry cannot mix providers")
    if symbol not in cohort.symbols:
        raise ValueError("catalogue study symbol is absent from cohort")
    if cohort.archive_sha256 != archive.archive_sha256:
        raise ValueError("study cohort does not belong to supplied universe archive")
    if study.provider_id != provider_id or study.canonical_symbol != symbol:
        raise ValueError("replay study identity does not match MTF bundle")
    if study.bundle_sha256 != bundle.manifest.bundle_sha256:
        raise ValueError("replay study does not reference supplied MTF bundle")
    if provenance.provider_id != provider_id or provenance.canonical_symbol != symbol:
        raise ValueError("study provenance identity mismatch")
    if provenance.study_id != study.study_id:
        raise ValueError("study provenance study_id mismatch")
    if provenance.bundle_sha256 != bundle.manifest.bundle_sha256:
        raise ValueError("study provenance bundle digest mismatch")
    if provenance.cohort_sha256 != cohort.cohort_sha256:
        raise ValueError("study provenance cohort digest mismatch")
    if provenance.replay_study_sha256 != study.file_sha256:
        raise ValueError("study provenance replay-study content digest mismatch")
    expected_context_sha = replay_context_sha256(cohort.contexts[symbol])
    if provenance.context_sha256 != expected_context_sha:
        raise ValueError("study provenance context digest does not match cohort symbol context")

    sample_ref: ArtifactReference | None = None
    if sample_path is not None:
        sample = load_outcome_sample(sample_path)
        if sample.provider_id != provider_id or sample.canonical_symbol != symbol:
            raise ValueError("outcome sample identity mismatch")
        if sample.source_study_id != study.study_id:
            raise ValueError("outcome sample study_id mismatch")
        if sample.source_replay_study_sha256 != study.file_sha256:
            raise ValueError("outcome sample replay-study digest mismatch")
        sample_ref = _reference(
            root,
            sample_path,
            kind="OUTCOME_SAMPLE",
            schema_version=sample.schema_version,
            semantic_id=sample.content_sha256,
        )

    refs = {
        "mtf_bundle": _reference(
            root,
            bundle_path,
            kind="MTF_BUNDLE",
            schema_version=bundle.manifest.schema_version,
            semantic_id=bundle.manifest.bundle_sha256,
        ),
        "universe_archive": _reference(
            root,
            archive_path,
            kind="UNIVERSE_ARCHIVE",
            schema_version=archive.schema_version,
            semantic_id=archive.archive_sha256,
        ),
        "study_cohort": _reference(
            root,
            cohort_path,
            kind="STUDY_COHORT",
            schema_version=cohort.schema_version,
            semantic_id=cohort.cohort_sha256,
        ),
        "replay_study": _reference(
            root,
            study_path,
            kind="REPLAY_STUDY",
            schema_version=study.schema_version,
            semantic_id=study.study_id,
        ),
        "study_provenance": _reference(
            root,
            provenance_path,
            kind="STUDY_PROVENANCE",
            schema_version=provenance.schema_version,
            semantic_id=provenance.provenance_sha256,
        ),
        "outcome_sample": sample_ref,
    }
    entry_payload = {
        "provider_id": provider_id,
        "canonical_symbol": symbol,
        **{
            key: asdict(value) if value is not None else None
            for key, value in refs.items()
        },
    }
    return DatasetCatalogueEntry(
        entry_id=_digest(entry_payload),
        provider_id=provider_id,
        canonical_symbol=symbol,
        mtf_bundle=refs["mtf_bundle"],
        universe_archive=refs["universe_archive"],
        study_cohort=refs["study_cohort"],
        replay_study=refs["replay_study"],
        study_provenance=refs["study_provenance"],
        outcome_sample=sample_ref,
    )


def build_dataset_catalogue(entries: Sequence[DatasetCatalogueEntry]) -> DatasetCatalogue:
    ordered = tuple(sorted(entries, key=lambda item: item.entry_id))
    if not ordered:
        raise ValueError("dataset catalogue requires at least one entry")
    if len({entry.entry_id for entry in ordered}) != len(ordered):
        raise ValueError("dataset catalogue contains duplicate entry_id")
    study_ids = [entry.replay_study.semantic_id for entry in ordered]
    if len(set(study_ids)) != len(study_ids):
        raise ValueError("dataset catalogue cannot register the same replay study twice")
    payload = {
        "schema_version": CATALOGUE_SCHEMA_VERSION,
        "entries": [_entry_payload(entry) for entry in ordered],
    }
    return DatasetCatalogue(
        schema_version=CATALOGUE_SCHEMA_VERSION,
        entries=ordered,
        catalogue_sha256=_digest(payload),
    )


def append_catalogue_entry(
    catalogue: DatasetCatalogue | None,
    entry: DatasetCatalogueEntry,
) -> DatasetCatalogue:
    if catalogue is None:
        return build_dataset_catalogue((entry,))
    _validate_catalogue_digest(catalogue)
    return build_dataset_catalogue((*catalogue.entries, entry))


def write_dataset_catalogue(path: str | Path, catalogue: DatasetCatalogue) -> Path:
    _validate_catalogue_digest(catalogue)
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": catalogue.schema_version,
        "entries": [_entry_payload(entry) for entry in catalogue.entries],
        "catalogue_sha256": catalogue.catalogue_sha256,
    }
    target.write_text(
        json.dumps(payload, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return target


def load_dataset_catalogue(
    path: str | Path,
    *,
    artifact_root: str | Path | None = None,
    verify_artifacts: bool = True,
) -> DatasetCatalogue:
    target = Path(path)
    payload = json.loads(target.read_text(encoding="utf-8"))
    if payload.get("schema_version") != CATALOGUE_SCHEMA_VERSION:
        raise ValueError("unsupported dataset catalogue schema version")
    raw_entries = payload.get("entries")
    if not isinstance(raw_entries, list):
        raise ValueError("dataset catalogue entries must be a list")
    entries = tuple(_entry_from_payload(item) for item in raw_entries)
    catalogue = DatasetCatalogue(
        schema_version=CATALOGUE_SCHEMA_VERSION,
        entries=entries,
        catalogue_sha256=str(payload.get("catalogue_sha256")),
    )
    _validate_catalogue_digest(catalogue)

    if verify_artifacts:
        root = Path(artifact_root).resolve() if artifact_root is not None else target.parent.resolve()
        for entry in catalogue.entries:
            rebuilt = build_catalogue_entry(
                root,
                mtf_bundle_path=root / entry.mtf_bundle.path,
                universe_archive_path=root / entry.universe_archive.path,
                study_cohort_path=root / entry.study_cohort.path,
                replay_study_path=root / entry.replay_study.path,
                study_provenance_path=root / entry.study_provenance.path,
                outcome_sample_path=(root / entry.outcome_sample.path) if entry.outcome_sample is not None else None,
            )
            if rebuilt != entry:
                raise ValueError("dataset catalogue artifact verification mismatch")
    return catalogue


def _reference(
    root: Path,
    path: Path,
    *,
    kind: str,
    schema_version: str,
    semantic_id: str,
) -> ArtifactReference:
    semantic = _require_sha256(semantic_id, f"{kind} semantic_id")
    return ArtifactReference(
        kind=kind,
        schema_version=schema_version,
        path=_relative_path(root, path),
        semantic_id=semantic,
        content_sha256=path_content_sha256(path),
    )


def _resolve_inside(root: Path, path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("catalogue artifact path escapes artifact_root") from exc
    if not resolved.exists():
        raise ValueError(f"catalogue artifact path does not exist: {resolved}")
    return resolved


def _relative_path(root: Path, path: Path) -> str:
    relative = path.resolve().relative_to(root).as_posix()
    if not relative or relative == "." or relative.startswith("../"):
        raise ValueError("invalid catalogue artifact relative path")
    return relative


def _entry_payload(entry: DatasetCatalogueEntry) -> dict[str, object]:
    return {
        "entry_id": entry.entry_id,
        "provider_id": entry.provider_id,
        "canonical_symbol": entry.canonical_symbol,
        "mtf_bundle": asdict(entry.mtf_bundle),
        "universe_archive": asdict(entry.universe_archive),
        "study_cohort": asdict(entry.study_cohort),
        "replay_study": asdict(entry.replay_study),
        "study_provenance": asdict(entry.study_provenance),
        "outcome_sample": asdict(entry.outcome_sample) if entry.outcome_sample is not None else None,
    }


def _entry_from_payload(payload: object) -> DatasetCatalogueEntry:
    if not isinstance(payload, dict):
        raise ValueError("invalid dataset catalogue entry")
    entry = DatasetCatalogueEntry(
        entry_id=_require_sha256(payload.get("entry_id"), "entry_id"),
        provider_id=str(payload.get("provider_id") or ""),
        canonical_symbol=str(payload.get("canonical_symbol") or ""),
        mtf_bundle=_reference_from_payload(payload.get("mtf_bundle")),
        universe_archive=_reference_from_payload(payload.get("universe_archive")),
        study_cohort=_reference_from_payload(payload.get("study_cohort")),
        replay_study=_reference_from_payload(payload.get("replay_study")),
        study_provenance=_reference_from_payload(payload.get("study_provenance")),
        outcome_sample=_reference_from_payload(payload.get("outcome_sample")) if payload.get("outcome_sample") is not None else None,
    )
    if not entry.provider_id or not entry.canonical_symbol:
        raise ValueError("dataset catalogue entry identity is required")
    for reference in (
        entry.mtf_bundle,
        entry.universe_archive,
        entry.study_cohort,
        entry.replay_study,
        entry.study_provenance,
        entry.outcome_sample,
    ):
        if reference is not None:
            _validate_stored_path(reference.path)
    expected = _digest({
        "provider_id": entry.provider_id,
        "canonical_symbol": entry.canonical_symbol,
        "mtf_bundle": asdict(entry.mtf_bundle),
        "universe_archive": asdict(entry.universe_archive),
        "study_cohort": asdict(entry.study_cohort),
        "replay_study": asdict(entry.replay_study),
        "study_provenance": asdict(entry.study_provenance),
        "outcome_sample": asdict(entry.outcome_sample) if entry.outcome_sample is not None else None,
    })
    if expected != entry.entry_id:
        raise ValueError("dataset catalogue entry digest mismatch")
    return entry


def _reference_from_payload(payload: object) -> ArtifactReference:
    if not isinstance(payload, dict):
        raise ValueError("invalid artifact reference")
    reference = ArtifactReference(
        kind=str(payload.get("kind") or ""),
        schema_version=str(payload.get("schema_version") or ""),
        path=str(payload.get("path") or ""),
        semantic_id=_require_sha256(payload.get("semantic_id"), "artifact semantic_id"),
        content_sha256=_require_sha256(payload.get("content_sha256"), "artifact content_sha256"),
    )
    if not reference.kind or not reference.schema_version:
        raise ValueError("artifact reference kind/schema_version is required")
    _validate_stored_path(reference.path)
    return reference


def _validate_stored_path(path: str) -> None:
    candidate = Path(path)
    if candidate.is_absolute() or not path or ".." in candidate.parts:
        raise ValueError("unsafe dataset catalogue artifact path")


def _validate_catalogue_digest(catalogue: DatasetCatalogue) -> None:
    if catalogue.schema_version != CATALOGUE_SCHEMA_VERSION:
        raise ValueError("unsupported dataset catalogue schema version")
    if not catalogue.entries:
        raise ValueError("dataset catalogue requires entries")
    if len({entry.entry_id for entry in catalogue.entries}) != len(catalogue.entries):
        raise ValueError("dataset catalogue contains duplicate entry_id")
    if len({entry.replay_study.semantic_id for entry in catalogue.entries}) != len(catalogue.entries):
        raise ValueError("dataset catalogue contains duplicate replay study")
    payload = {
        "schema_version": catalogue.schema_version,
        "entries": [_entry_payload(entry) for entry in catalogue.entries],
    }
    if _digest(payload) != _require_sha256(catalogue.catalogue_sha256, "catalogue_sha256"):
        raise ValueError("dataset catalogue digest mismatch")


def _require_sha256(value: object, name: str) -> str:
    text = str(value or "").lower()
    if len(text) != 64 or any(character not in "0123456789abcdef" for character in text):
        raise ValueError(f"{name} must be a SHA-256 hex digest")
    return text


def _digest(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return sha256(raw.encode("ascii")).hexdigest()
