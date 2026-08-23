from __future__ import annotations

import argparse
import json
from pathlib import Path

from ktrader.catalogue import (
    append_catalogue_entry,
    build_catalogue_entry,
    load_dataset_catalogue,
    write_dataset_catalogue,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register one fully linked K-Trader replay/outcome dataset chain in the audit catalogue"
    )
    parser.add_argument("--root", required=True, type=Path, help="Artifact root; every referenced path must remain inside it")
    parser.add_argument("--catalogue", required=True, type=Path)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--universe-archive", required=True, type=Path)
    parser.add_argument("--cohort", required=True, type=Path)
    parser.add_argument("--study", required=True, type=Path)
    parser.add_argument("--provenance", required=True, type=Path)
    parser.add_argument("--outcome-sample", type=Path, default=None)
    args = parser.parse_args()

    root = args.root.resolve()
    catalogue_path = args.catalogue
    if not catalogue_path.is_absolute():
        catalogue_path = root / catalogue_path
    catalogue_path = catalogue_path.resolve()
    try:
        catalogue_path.relative_to(root)
    except ValueError as exc:
        raise SystemExit("--catalogue must remain inside --root") from exc

    entry = build_catalogue_entry(
        root,
        mtf_bundle_path=args.bundle,
        universe_archive_path=args.universe_archive,
        study_cohort_path=args.cohort,
        replay_study_path=args.study,
        study_provenance_path=args.provenance,
        outcome_sample_path=args.outcome_sample,
    )
    existing = (
        load_dataset_catalogue(catalogue_path, artifact_root=root, verify_artifacts=True)
        if catalogue_path.exists()
        else None
    )
    updated = append_catalogue_entry(existing, entry)
    output = write_dataset_catalogue(catalogue_path, updated)

    print(
        json.dumps(
            {
                "output": str(output),
                "entry_id": entry.entry_id,
                "provider_id": entry.provider_id,
                "symbol": entry.canonical_symbol,
                "study_id": entry.replay_study.semantic_id,
                "outcome_sample": entry.outcome_sample.semantic_id if entry.outcome_sample is not None else None,
                "entry_count": len(updated.entries),
                "catalogue_sha256": updated.catalogue_sha256,
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
