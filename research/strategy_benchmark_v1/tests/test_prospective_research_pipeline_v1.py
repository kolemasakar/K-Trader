from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import unittest
from unittest import mock


MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / 'run_prospective_research_pipeline_v1.py'
SPEC = importlib.util.spec_from_file_location('pipeline_v1', MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
pipeline = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipeline)


class PipelineHardeningTests(unittest.TestCase):
    def test_stamp_is_deterministic_utc(self):
        parsed = pipeline.utc('2026-09-16T13:00:00Z')
        self.assertEqual(pipeline.stamp(parsed), '20260916T130000Z')

    @mock.patch.object(pipeline.subprocess, 'run')
    def test_plan_mode_never_executes_subprocess(self, mocked_run):
        records = []
        pipeline.run_stage('capture', ['python', 'capture.py'], False, records)
        mocked_run.assert_not_called()
        self.assertEqual(records[0]['status'], 'PLANNED')

    @mock.patch.object(pipeline.subprocess, 'run')
    def test_failure_is_fail_closed(self, mocked_run):
        mocked_run.return_value = subprocess.CompletedProcess(
            args=['python', 'funding.py'], returncode=7, stdout='failure\n', stderr=''
        )
        records = []
        with self.assertRaisesRegex(RuntimeError, r'STAGE_FAILED funding rc=7'):
            pipeline.run_stage('funding', ['python', 'funding.py'], True, records)
        self.assertEqual(records[0]['status'], 'FAILED')
        self.assertEqual(records[0]['returncode'], 7)

    @mock.patch.object(pipeline.subprocess, 'run')
    def test_success_records_pass(self, mocked_run):
        mocked_run.return_value = subprocess.CompletedProcess(
            args=['python', 'capture.py'], returncode=0, stdout='ok\n', stderr=''
        )
        records = []
        pipeline.run_stage('capture', ['python', 'capture.py'], True, records)
        self.assertEqual(records[0]['status'], 'PASS')
        self.assertEqual(records[0]['returncode'], 0)


if __name__ == '__main__':
    unittest.main()
