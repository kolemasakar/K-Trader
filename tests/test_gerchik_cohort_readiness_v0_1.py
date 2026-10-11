import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.research.gerchik_cohort_readiness_v0_1 import audit, inspect_file, complete_week_count, rebuild_closed_weeks

DAY = 86400000
MONDAY = 1759104000000


class CohortReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def file(self, offsets=(0, 1, 2), interval="1d", partial=False):
        step = DAY if interval == "1d" else DAY*7
        rows = [[MONDAY+k*step, "100", "110", "90", "105", "10",
                 MONDAY+(k+1)*step-1] for k in offsets]
        if partial:
            rows[-1][6] -= DAY
        path = self.root/"bars.jsonl"
        path.write_text("".join(json.dumps(x)+"\n" for x in rows))
        row = dict(symbol="BTCUSDT", interval=interval, relative_path="bars.jsonl",
                   bars=len(rows), first_open_ms=rows[0][0], last_open_ms=rows[-1][0],
                   sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        return path, row

    def manifest(self, row):
        data = dict(research_only=True, not_first_seen=True, symbols=["BTCUSDT"],
                    intervals=[row["interval"]], rows=[row], requested_start_utc="2025-09-29T00:00:00Z",
                    requested_end_exclusive_utc="2026-09-25T00:00:00Z")
        (self.root/"manifest.json").write_text(json.dumps(data))
        return data

    def test_verified_file(self):
        path, row = self.file()
        self.manifest(row)
        before = path.read_bytes()
        result = audit(self.root)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(result["m5_available"])
        self.assertEqual(before, path.read_bytes())

    def test_hash_mismatch(self):
        path, row = self.file()
        row["sha256"] = "0"*64
        self.assertEqual(inspect_file(path, row)[0]["status"], "FAIL")

    def test_duplicate_and_gap_fail(self):
        for offsets in ((0, 0, 1), (0, 2, 3)):
            path, row = self.file(offsets)
            self.assertEqual(inspect_file(path, row)[0]["status"], "FAIL")

    def test_partial_daily_fails_weekly_is_flagged(self):
        for interval, expected in (("1d", "FAIL"), ("1w", "PARTIAL_W1_REBUILD_REQUIRED")):
            path, row = self.file(interval=interval, partial=True)
            self.assertEqual(inspect_file(path, row)[0]["status"], expected)

    def test_complete_week_excludes_boundaries(self):
        self.assertEqual(complete_week_count([MONDAY+i*DAY for i in range(-2, 12)]), 1)

    def test_weekly_rebuild_exact_volume_and_causal_prefix(self):
        rows = [[MONDAY+i*DAY, "100", "110", "90", "105", "0.1", MONDAY+(i+1)*DAY-1] for i in range(14)]
        first = rebuild_closed_weeks(rows, end_exclusive_ms=MONDAY+7*DAY)
        self.assertEqual(len(first), 1)
        self.assertEqual(first[0][5], "0.7")
        self.assertEqual(first, rebuild_closed_weeks(rows[:7], end_exclusive_ms=MONDAY+7*DAY))
        self.assertFalse(rebuild_closed_weeks(rows, end_exclusive_ms=MONDAY+6*DAY))

    def test_gapped_or_duplicate_week_never_emitted(self):
        rows = [[MONDAY+i*DAY, "100", "110", "90", "105", "1", MONDAY+(i+1)*DAY-1] for i in range(7)]
        self.assertFalse(rebuild_closed_weeks(rows[:3]+rows[4:], end_exclusive_ms=MONDAY+7*DAY))
        self.assertFalse(rebuild_closed_weeks(rows+[rows[0]], end_exclusive_ms=MONDAY+7*DAY))

    def test_full_exchange_week_timestamp_beyond_requested_end_is_partial(self):
        path, row = self.file(offsets=(0,), interval="1w")
        result, _ = inspect_file(path, row, end_exclusive_ms=MONDAY+4*DAY)
        self.assertEqual(result["status"], "PARTIAL_W1_REBUILD_REQUIRED")

    def test_manifest_duplicate_identity_rejected(self):
        _, row = self.file()
        data = self.manifest(row)
        data["rows"].append(row)
        (self.root/"manifest.json").write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            audit(self.root)

    def test_path_escape_rejected(self):
        _, row = self.file()
        row["relative_path"] = "../bars.jsonl"
        self.manifest(row)
        with self.assertRaises(ValueError):
            audit(self.root)

    def test_invalid_ohlc_fails(self):
        path, row = self.file()
        path.write_text(path.read_text().replace('"110"', '"99"'))
        row["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.assertEqual(inspect_file(path, row)[0]["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
