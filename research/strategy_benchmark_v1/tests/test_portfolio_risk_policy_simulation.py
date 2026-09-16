from __future__ import annotations

import importlib.util
import pathlib
import unittest
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = HERE / 'portfolio_risk_policy_simulation.py'
spec = importlib.util.spec_from_file_location('risk_sim', SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class PortfolioRiskPolicySimulationTests(unittest.TestCase):
    def test_cluster_cap_blocks_third_correlated_position(self):
        rows = [
            {'setup_family_id': 'a', 'symbol': 'ADAUSDT', 'side': 'SHORT', 'entry_time': '2026-09-16T10:00:00Z', 'resolved': True, 'exit_time': '2026-09-16T12:00:00Z', 'realized_R': 1.0},
            {'setup_family_id': 'b', 'symbol': 'DOGEUSDT', 'side': 'SHORT', 'entry_time': '2026-09-16T10:15:00Z', 'resolved': True, 'exit_time': '2026-09-16T12:15:00Z', 'realized_R': -1.0},
            {'setup_family_id': 'c', 'symbol': 'XRPUSDT', 'side': 'SHORT', 'entry_time': '2026-09-16T10:30:00Z', 'resolved': True, 'exit_time': '2026-09-16T12:30:00Z', 'realized_R': 0.5},
        ]
        policy = {
            'policy_id': 'T', 'risk_per_family_pct': 0.5, 'max_open_positions': 5,
            'max_portfolio_open_risk_pct': 5.0, 'max_same_side_open_risk_pct': 5.0,
            'max_correlated_cluster_open_risk_pct': 1.0,
        }
        result = mod.simulate(rows, {'ADAUSDT': 'C01', 'DOGEUSDT': 'C01', 'XRPUSDT': 'C01'}, policy, datetime(2026, 9, 16, 13, tzinfo=timezone.utc))
        self.assertEqual(result['accepted_family_count'], 2)
        self.assertEqual(result['blocked_family_count'], 1)
        self.assertIn('MAX_CORRELATED_CLUSTER_OPEN_RISK', result['blocked_families'][0]['reasons'])

    def test_releases_resolved_position_before_later_entry(self):
        rows = [
            {'setup_family_id': 'a', 'symbol': 'ADAUSDT', 'side': 'SHORT', 'entry_time': '2026-09-16T10:00:00Z', 'resolved': True, 'exit_time': '2026-09-16T10:30:00Z', 'realized_R': 1.0},
            {'setup_family_id': 'b', 'symbol': 'DOGEUSDT', 'side': 'SHORT', 'entry_time': '2026-09-16T10:45:00Z', 'resolved': True, 'exit_time': '2026-09-16T11:00:00Z', 'realized_R': -1.0},
        ]
        policy = {
            'policy_id': 'T', 'risk_per_family_pct': 0.5, 'max_open_positions': 1,
            'max_portfolio_open_risk_pct': 0.5, 'max_same_side_open_risk_pct': 0.5,
            'max_correlated_cluster_open_risk_pct': 0.5,
        }
        result = mod.simulate(rows, {'ADAUSDT': 'C01', 'DOGEUSDT': 'C01'}, policy, datetime(2026, 9, 16, 12, tzinfo=timezone.utc))
        self.assertEqual(result['accepted_family_count'], 2)
        self.assertEqual(result['blocked_family_count'], 0)


if __name__ == '__main__':
    unittest.main()
