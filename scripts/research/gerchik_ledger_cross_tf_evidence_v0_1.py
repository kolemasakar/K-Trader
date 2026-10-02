"""Read-only bridge: attach reviewed provenance to ledger levels for luft evidence.

Never mutates ledger state or primary type. A confirmation is a view, not promotion.
"""
from dataclasses import dataclass
from .gerchik_cross_tf_v0_1 import _utc
from .gerchik_cross_tf_luft_v0_2 import confirm_pairs
from .gerchik_structural_review_gate_v0_1 import verify_reviewed_extremum


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
        bundle = reviewed_sources.get(key)
        if bundle is None:
            continue
        if not isinstance(bundle, dict) or set(bundle) != {'event', 'source_bar', 'review'}:
            raise ValueError('Complete event/source_bar/review bundle required')
        event, bar, review = bundle['event'], bundle['source_bar'], bundle['review']
        if (event.get('event_id'), event.get('symbol'), event.get('timeframe')) != (
                key, level.symbol, level.timeframe):
            raise ValueError('Reviewed source identity mismatch')
        if str(event.get('price')) != str(level.price) or str(event.get('tick_size')) != str(level.tick_size):
            raise ValueError('Reviewed source price/tick mismatch')
        if not bar.get('opened_at'):
            raise ValueError('Reviewed source bar start required')
        if _utc(review['reviewed_at']) > cutoff:
            continue
        verified = verify_reviewed_extremum(event, bar, review, as_of)
        if _utc(verified['reviewed_at']) < _utc(level.formed_at):
            raise ValueError('Review cannot predate formation')
        views.append(_QualifiedView(
            symbol=level.symbol, timeframe=level.timeframe,
            price=str(level.price), tick_size=level.tick_size,
            primary_type=level.primary_type,
            formed_at=max(_utc(level.formed_at), _utc(verified['reviewed_at'])).isoformat(),
            formation_event_id=key, state=level.state,
            structurally_qualified=True,
            source_opened_at=bar['opened_at'],
            source_closed_at=bar['closed_at'],
        ))
    return confirm_pairs(views, as_of, luft_by_symbol)
