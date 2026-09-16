#!/usr/bin/env python3
from __future__ import annotations

"""Versioned v1.3 overlay for the frozen-v2.2 offline resolver.

v1.3 keeps v1.1 outcome/economic semantics, but hardens accepted-prior identity:
- accepted entry price must match exactly;
- stop recomputation drift may pass the existing 3e-9 absolute guard or a
  scale-aware limit of 1e-4 of accepted initial risk;
- prior terminal-path revalidation always uses accepted prior entry/stop,
  so later recomputation drift cannot alter an accepted terminal path.

The overlay is hash-pinned to the immutable v1.1 source and fails closed if the
base source changes or an expected transform no longer matches exactly.
"""

import hashlib
import pathlib
import types

HERE = pathlib.Path(__file__).resolve().parent
BASE = HERE / 'prospective_v2_2_outcome_resolver_offline_v1_1.py'
EXPECTED_BASE_SHA256 = '2e67e032b6477bb849a5aa46c81461d7df440a6adf32139f8761fcd813bf65f2'
OUTROOT = pathlib.Path('/data/research/phase11g/strategy_benchmark_v1/combined_rules/prospective_v2_2_outcomes_offline_v1_3')


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f'V1_3_PATCH_MISMATCH {label} count={count}')
    return source.replace(old, new, 1)


def replace_first(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count < 1:
        raise RuntimeError(f'V1_3_PATCH_MISSING {label}')
    return source.replace(old, new, 1)


def build_base_module():
    raw = BASE.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_BASE_SHA256:
        raise RuntimeError(
            f'V1_3_BASE_HASH_MISMATCH expected={EXPECTED_BASE_SHA256} actual={actual}'
        )

    source = raw.decode('utf-8')
    source = replace_once(
        source,
        "PRIOR_PRICE_ABS_TOL = 2e-9\nPRIOR_PRICE_REL_TOL = 1e-12\n",
        "PRIOR_PRICE_ABS_TOL = 3e-9\nPRIOR_PRICE_REL_TOL = 1e-12\nPRIOR_STOP_RISK_FRACTION_TOL = 1e-4\n",
        'constants',
    )
    source = replace_once(
        source,
        "\n\ndef main() -> None:\n",
        "\n\ndef stop_close(event: dict, prior: dict) -> bool:\n"
        "    current = float(event['stop_price'])\n"
        "    accepted = float(prior['stop_price'])\n"
        "    if price_close(current, accepted):\n"
        "        return True\n"
        "    risk = abs(float(prior['entry_price']) - accepted)\n"
        "    return risk > 0 and abs(current - accepted) <= PRIOR_STOP_RISK_FRACTION_TOL * risk\n"
        "\n\ndef main() -> None:\n",
        'stop_close',
    )
    source = replace_once(
        source,
        "price_close(event['entry_price'], prior['entry_price'])\n"
        "                    and price_close(event['stop_price'], prior['stop_price'])",
        "float(event['entry_price']) == float(prior['entry_price'])\n"
        "                    and stop_close(event, prior)",
        'identity_guard',
    )
    source = replace_first(
        source,
        "path = offline.terminal_path(event, bars_cache[symbol], as_of)",
        "revalidation_event = dict(event)\n"
        "                revalidation_event['entry_price'] = prior['entry_price']\n"
        "                revalidation_event['stop_price'] = prior['stop_price']\n"
        "                path = offline.terminal_path(revalidation_event, bars_cache[symbol], as_of)",
        'prior_revalidation_event',
    )
    source = replace_once(
        source,
        "row['identity_price_tolerance_rel'] = PRIOR_PRICE_REL_TOL\n",
        "row['identity_price_tolerance_rel'] = PRIOR_PRICE_REL_TOL\n"
        "                row['identity_entry_exact_match_required'] = True\n"
        "                row['identity_stop_risk_fraction_tolerance'] = PRIOR_STOP_RISK_FRACTION_TOL\n",
        'observation_metadata',
    )
    source = replace_once(
        source,
        "'prior_identity_rel_tol': PRIOR_PRICE_REL_TOL,",
        "'prior_identity_rel_tol': PRIOR_PRICE_REL_TOL,\n"
        "        'prior_entry_exact_match_required': True,\n"
        "        'prior_stop_risk_fraction_tol': PRIOR_STOP_RISK_FRACTION_TOL,\n"
        "        'resolver_version': 'v1.3',",
        'report_metadata',
    )

    module = types.ModuleType('prospective_v2_2_offline_v1_3_runtime')
    module.__file__ = str(BASE)
    exec(compile(source, str(BASE), 'exec'), module.__dict__)
    module.OUTROOT = OUTROOT
    return module


def main() -> None:
    build_base_module().main()


if __name__ == '__main__':
    main()
