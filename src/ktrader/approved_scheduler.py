"""Compatibility API only; current historical tests use approved_replay directly.

No timer or job service is provided by this module. Retained for old callers.
"""
from ktrader.approved_replay import run_model, finish

__all__ = ["run_model", "finish"]
