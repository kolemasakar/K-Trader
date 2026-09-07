from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING

from ktrader.outcomes.evaluator import (
    SignalOutcome,
    decision_fingerprint,
    evaluate_signal_outcome,
)
from ktrader.outcomes.storage import OutcomeRepository

if TYPE_CHECKING:
    from ktrader.outcomes.sample import (
        OUTCOME_SAMPLE_SCHEMA_VERSION,
        OutcomeSample,
        build_outcome_sample,
        build_outcome_sample_from_repository,
        load_outcome_sample,
        write_outcome_sample,
    )

_SAMPLE_EXPORTS = {
    "OUTCOME_SAMPLE_SCHEMA_VERSION",
    "OutcomeSample",
    "build_outcome_sample",
    "build_outcome_sample_from_repository",
    "load_outcome_sample",
    "write_outcome_sample",
}


def __getattr__(name: str):
    if name not in _SAMPLE_EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module("ktrader.outcomes.sample")
    value = getattr(module, name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))


__all__ = [
    "OUTCOME_SAMPLE_SCHEMA_VERSION",
    "OutcomeRepository",
    "OutcomeSample",
    "SignalOutcome",
    "build_outcome_sample",
    "build_outcome_sample_from_repository",
    "decision_fingerprint",
    "evaluate_signal_outcome",
    "load_outcome_sample",
    "write_outcome_sample",
]
