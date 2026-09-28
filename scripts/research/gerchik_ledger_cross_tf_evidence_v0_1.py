"""Read-only bridge: attach reviewed provenance to ledger levels for luft evidence.

Never mutates ledger state or primary type. A confirmation is a view, not promotion.
"""
from dataclasses import dataclass
from .gerchik_cross_tf_v0_1 import _utc
from .gerchik_cross_tf_luft_v0_2 import confirm_pairs


@dataclass(frozen=True)
class _QualifiedView:
    symbol: str
    timeframe: str
    price: str
    tick_size: str
    primary_type: str
    formed_at: str
    formation_event_id: str
    state: str
    structurally_qualified: bool
    source_opened_at: str
    source_closed_at: str


def ledger_cross_tf_evidence(ledger, reviewed_sources, as_of, luft_by_symbol):
    """Return qualified cross-TF pairs without changing canonical ledger levels.

    reviewed_sources: mapping formation_event_id -> full source bar/review evidence
    with source_opened_at, source_closed_at, verified_at, symbol, timeframe.
    The mapping must come from a trusted upstream review pipeline; it is not
    an authentication boundary.
    """
    cutoff = _utc(as_of)
    views = []
    levels = ledger.as_of(as_of)
    seen = set()
    for level in levels:
        key = level.formation_event_id
        if key in seen:
            raise ValueError('Duplicate formation event ID across ledger levels')
        seen.add(key)
        source = reviewed_sources.get(key)
        if source is None:
            continue
        required = ('symbol', 'timeframe', 'source_opened_at', 'source_closed_at',
                    'verified_at', 'reviewed_formation_event_id')
        if any(not source.get(k) for k in required):
            raise ValueError('Incomplete reviewed source provenance')
        if (source['symbol'], source['timeframe'],
                source['reviewed_formation_event_id']) != (
                level.symbol, level.timeframe, key):
            raise ValueError('Reviewed source identity mismatch')
        if _utc(source['verified_at']) > cutoff:
            continue
        if _utc(source['verified_at']) < _utc(level.formed_at):
            raise ValueError('Review cannot predate formation')
        views.append(_QualifiedView(
            symbol=level.symbol, timeframe=level.timeframe,
            price=str(level.price), tick_size=level.tick_size,
            primary_type=level.primary_type,
            formed_at=max(_utc(level.formed_at), _utc(source['verified_at'])).isoformat(),
            formation_event_id=key, state=level.state,
            structurally_qualified=True,
            source_opened_at=source['source_opened_at'],
            source_closed_at=source['source_closed_at'],
        ))
    return confirm_pairs(views, as_of, luft_by_symbol)
