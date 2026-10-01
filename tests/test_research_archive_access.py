"""Fast unit checks for immutable Phase 11G research archive verifier."""
import importlib.util
import json
import pathlib
import tempfile

import pytest

SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "verify_research_dataset.py"
spec = importlib.util.spec_from_file_location("verify_research_dataset", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture_archive(tmp_path):
    root = tmp_path / "archive"
    root.mkdir()
    (root / "dataset_summary.json").write_text(
        json.dumps({"provider_id": "binance_usdm", "panel_size": 19, "as_of": "2026-09-05T14:45:00Z"}),
        encoding="utf-8",
    )
    for i in range(19):
        symbol = f"COIN{i}USDT"
        bundle = root / "bundles" / symbol
        bundle.mkdir(parents=True)
        (bundle / "bundle.json").write_text(
            json.dumps({"canonical_symbol": symbol, "candle_counts": dict.fromkeys(module.TIMEFRAMES, 1)}),
            encoding="utf-8",
        )
        for tf in module.TIMEFRAMES:
            (bundle / f"{tf}.jsonl").write_text(
                json.dumps({"record_type": "manifest"}) + "\n"
                + json.dumps({"record_type": "candle", "symbol": symbol, "interval": tf, "closed": True})
                + "\n",
                encoding="utf-8",
            )
    files, digest = module.file_manifest(root)
    return root, digest


def test_verified_read_and_counts(tmp_path):
    root, digest = fixture_archive(tmp_path)
    report = module.verify(root, digest, check_mount=False)
    assert report["status"] == "VERIFIED_RESEARCH_DATASET"
    assert report["symbol_count"] == 19
    assert report["candle_counts"] == dict.fromkeys(module.TIMEFRAMES, 19)
    assert report["dataset_version_sha256"] == digest


def test_modified_archived_data_fails_closed(tmp_path):
    root, digest = fixture_archive(tmp_path)
    with (root / "bundles" / "COIN0USDT" / "1d.jsonl").open("a") as f:
        f.write("\n")
    with pytest.raises((ValueError, json.JSONDecodeError)):
        module.verify(root, digest, check_mount=False)


def test_expected_hash_cannot_silently_change(tmp_path):
    root, digest = fixture_archive(tmp_path)
    with pytest.raises(ValueError, match="tree SHA-256"):
        module.verify(root, "0" * 64, check_mount=False)


def test_archive_symlink_rejected(tmp_path):
    root, digest = fixture_archive(tmp_path)
    (root / "alias").symlink_to(root / "dataset_summary.json")
    with pytest.raises(ValueError, match="symlinks"):
        module.verify(root, digest, check_mount=False)


def test_rejects_unclosed_candles(tmp_path):
    root, _ = fixture_archive(tmp_path)
    p = root / "bundles" / "COIN0USDT" / "1d.jsonl"
    rows = [json.loads(line) for line in p.read_text().splitlines()]
    rows[1]["closed"] = False
    p.write_text("\n".join(json.dumps(row) for row in rows) + "\n")
    _, digest = module.file_manifest(root)
    with pytest.raises(ValueError, match="non-closed"):
        module.verify(root, digest, check_mount=False)
