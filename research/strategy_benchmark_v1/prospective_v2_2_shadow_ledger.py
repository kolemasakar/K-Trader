#!/usr/bin/env python3
from __future__ import annotations

"""Compatibility entry point for the canonical prospective ledger.

Ledger v1.2 preserves the first valid payload for every prospective event key
and audits later recomputation conflicts without rewriting causal history.
"""

from prospective_v2_2_shadow_ledger_v1_2 import main


if __name__ == '__main__':
    main()
