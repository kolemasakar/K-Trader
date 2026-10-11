"""Fail-closed admission of reviewed D1/W1 levels, separate from candidates."""
from dataclasses import dataclass
from decimal import Decimal
from hashlib import sha256
import json

TYPES = {'TREND_BREAK','HISTORICAL','MIRROR','LIMIT','PARANORMAL_BAR','CONSOLIDATION','GAP'}
FEATURES = {'TOUCH','NEAR_MISS','FALSE_BREAKOUT','NEW_EXTREME','REJECTION_WICK','ROUND_PRICE','CROSS_TF'}


def fingerprint(candidate):
    fields = ('price','timeframe','side','primary_type','source_open_ms','known_at_ms','witness_indices')
    return sha256(json.dumps({k:candidate[k] for k in fields},sort_keys=True,separators=(',',':')).encode()).hexdigest()


@dataclass(frozen=True)
class Admission:
    admitted: bool
    reasons: tuple
    evidence_id: str
    available_at_ms: int | None


def admit(candidate, review, rows, *, as_of_ms, tick, source_hash):
    reasons=[]
    eid=fingerprint(candidate)
    if candidate['timeframe'] not in ('D1','W1') or candidate['primary_type'] not in TYPES:
        reasons.append('UNQUALIFIED_OR_AMBIGUOUS_TYPE')
    if candidate['known_at_ms']>as_of_ms:
        reasons.append('FORMATION_UNAVAILABLE')
    index=candidate.get('source_index')
    if type(index) is not int or not 0<=index<len(rows):
        reasons.append('SOURCE_REFERENCE_INVALID')
    else:
        row=rows[index]
        if row[0]!=candidate['source_open_ms'] or Decimal(candidate['price']) not in (Decimal(row[2]),Decimal(row[3])):
            reasons.append('NOT_SOURCE_D1_W1_HIGH_LOW')
    witnesses=candidate.get('witness_indices',[])
    if not witnesses or any(type(i) is not int or not 0<=i<len(rows) or rows[i][6]+1>candidate['known_at_ms'] for i in witnesses):
        reasons.append('NONCAUSAL_OR_INVALID_WITNESS')
    if tick is None:
        reasons.append('HISTORICAL_TICK_UNVERIFIED')
    else:
        t=Decimal(str(tick))
        if not t.is_finite() or t<=0 or Decimal(candidate['price'])%t!=0:
            reasons.append('PRICE_OFF_VERIFIED_TICK')
    if not review:
        reasons.append('INDEPENDENT_REVIEW_MISSING')
        return Admission(False,tuple(reasons),eid,None)
    if review.get('evidence_id')!=eid or review.get('source_sha256')!=source_hash:
        reasons.append('REVIEW_SOURCE_OR_ID_MISMATCH')
    if review.get('decision')!='CONFIRMED' or not review.get('reviewer') or review.get('method')!='INDEPENDENT_LABEL':
        reasons.append('REVIEW_NOT_CONFIRMED')
    reviewed=review.get('known_at_ms')
    if type(reviewed) is not int or reviewed<candidate['known_at_ms'] or reviewed>as_of_ms:
        reasons.append('REVIEW_NOT_CAUSALLY_AVAILABLE')
    proofs=review.get('strengthening',[])
    eligible=[]
    for proof in proofs:
        when=proof.get('known_at_ms')
        refs=proof.get('witness_indices',[])
        if (proof.get('kind') in FEATURES and proof.get('confirmed') is True
                and type(when) is int and candidate['known_at_ms']<=when<=as_of_ms
                and refs and all(type(i) is int and 0<=i<len(rows) and rows[i][6]+1<=when for i in refs)
                and proof.get('rule_id') and proof.get('reviewer')):
            eligible.append(proof)
    if not eligible:
        reasons.append('NO_CONFIRMED_STRENGTHENING')
    if review.get('invalidated_at_ms') is not None and review['invalidated_at_ms']<=as_of_ms:
        reasons.append('LEVEL_INVALIDATED')
    available=max(candidate['known_at_ms'],reviewed,min(p['known_at_ms'] for p in eligible)) if not reasons else None
    return Admission(not reasons,tuple(reasons),eid,available)
