"""Shared causal D1/W1 research level gate; never a broker/trading authorization.

This is an automated *candidate* gate. Full Gerchik strength validation must be
performed by the approved detector/auditor; this gate never fabricates it.
"""
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json

SUPPORTED = frozenset({"MIRROR", "CONSOLIDATION", "LIMIT"})

@dataclass(frozen=True)
class LevelDecision:
    admitted: bool
    reasons: tuple
    evidence_id: str
    available_at_ms: int | None

def research_admit(candidate, rows, *, as_of_ms, source_hash, verified_strength=False):
    """Common for S1/S2A/S2B/S3/S4/S5A/S5B; no broker metadata or reviewer."""
    identity = sha256(json.dumps(
        {"source": source_hash, "candidate": candidate},
        sort_keys=True, default=str, separators=(",", ":")
    ).encode()).hexdigest()
    reasons = []
    if candidate.get("timeframe") not in ("D1", "W1"):
        reasons.append("INVALID_TIMEFRAME")
    if candidate.get("primary_type") not in SUPPORTED:
        reasons.append("STRENGTH_RULE_NOT_VALIDATED")
    if not verified_strength:
        reasons.append("INDEPENDENT_AUTOMATED_STRENGTH_EVIDENCE_MISSING")
    known = candidate.get("known_at_ms")
    if type(known) is not int or known > as_of_ms:
        reasons.append("LEVEL_NOT_CAUSALLY_AVAILABLE")
    index = candidate.get("source_index")
    if type(index) is not int or not 0 <= index < len(rows):
        reasons.append("INVALID_SOURCE_REFERENCE")
    else:
        row = rows[index]
        price = Decimal(str(candidate["price"]))
        if row[0] != candidate.get("source_open_ms") or price not in (Decimal(str(row[2])), Decimal(str(row[3]))):
            reasons.append("PRICE_NOT_SOURCE_EXTREMUM")
    witnesses = candidate.get("witness_indices")
    if not isinstance(witnesses, list) or len(witnesses) < 2 or any(
        type(i) is not int or not 0 <= i < len(rows) or
        type(known) is not int or rows[i][6] + 1 > known for i in witnesses
    ):
        reasons.append("NONCAUSAL_OR_INSUFFICIENT_WITNESSES")
    return LevelDecision(not reasons, tuple(reasons), identity, known if not reasons else None)
