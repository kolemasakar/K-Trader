from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import pathlib
import subprocess
import sys
import tempfile
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

    def _prepare_plan_fixture(self, root: pathlib.Path):
        script_dir = root / 'scripts'
        script_dir.mkdir()
        primary = [
            'run_prospective_v2_2_shadow_cycle.py',
            'export_prospective_funding_snapshot_v1.py',
            'prospective_v2_2_outcome_resolver_offline_v1_2.py',
            'prospective_v2_2_post30_diagnostics.py',
            'prospective_post30_statistical_diagnostics.py',
        ]
        for name in primary + list(pipeline.CAPTURE_RUNTIME_DEPENDENCIES):
            (script_dir / name).touch()
        prior = root / 'prior'
        prior.mkdir()
        (prior / 'observations.jsonl').touch()
        return script_dir, prior

    def test_plan_has_explicit_v1_2_output_root_and_full_preflight(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            script_dir, prior = self._prepare_plan_fixture(root)
            base = root / 'base'
            manifests = root / 'manifests'
            argv = [
                'pipeline',
                '--as-of', '2026-09-16T13:30:00Z',
                '--prior-outcomes', str(prior),
                '--script-dir', str(script_dir),
                '--base', str(base),
                '--manifest-dir', str(manifests),
            ]
            with mock.patch.object(sys, 'argv', argv), contextlib.redirect_stdout(io.StringIO()):
                pipeline.main()
            report = json.loads(
                (manifests / 'pipeline_20260916T133000Z_plan.json').read_text()
            )
            resolver = next(x for x in report['stages'] if x['stage'] == 'resolver')
            self.assertIn('--output-root', resolver['command'])
            i = resolver['command'].index('--output-root')
            expected = base / 'strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_2'
            self.assertEqual(resolver['command'][i + 1], str(expected))
            self.assertEqual(report['outcomes_root'], str(expected / '20260916T133000Z'))
            self.assertEqual(report['runtime_preflight_file_count'], 10)

    def test_missing_capture_dependency_fails_before_plan(self):
        with tempfile.TemporaryDirectory() as td:
            root = pathlib.Path(td)
            script_dir, prior = self._prepare_plan_fixture(root)
            missing = script_dir / pipeline.CAPTURE_RUNTIME_DEPENDENCIES[0]
            missing.unlink()
            argv = [
                'pipeline',
                '--as-of', '2026-09-16T13:30:00Z',
                '--prior-outcomes', str(prior),
                '--script-dir', str(script_dir),
                '--base', str(root / 'base'),
                '--manifest-dir', str(root / 'manifests'),
            ]
            with mock.patch.object(sys, 'argv', argv):
                with self.assertRaisesRegex(SystemExit, 'MISSING_PIPELINE_RUNTIME_FILES'):
                    pipeline.main()


if __name__ == '__main__':
    unittest.main()
