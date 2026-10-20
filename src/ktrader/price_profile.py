"""Validate declared historical geometry; declarations do not prove provenance."""
from decimal import Decimal, InvalidOperation


def profile_blockers(profile, symbol):
    reasons=[]
    geometry={}
    for key in ('point','tick_size'):
        value=profile.get(key)
        try:
            if isinstance(value,bool):
                raise ValueError()
            number=Decimal(str(value))
            if not number.is_finite() or number<=0:
                raise ValueError()
            geometry[key]=number
        except (InvalidOperation,ValueError):
            reasons.append(key)
    if len(geometry)==2 and geometry['tick_size']%geometry['point']!=0:
        reasons.append('tick_not_multiple_of_point')
    for key in ('historical_price_geometry_verified','level_universe_reviewed'):
        if profile.get(key) is not True:
            reasons.append(key)
    if not isinstance(profile.get('provenance'),str) or not profile['provenance'].strip():
        reasons.append('provenance')
    if profile.get('broker_symbol')!=symbol:
        reasons.append('broker_symbol')
    if profile.get('asset_class') not in ('us_equity','crypto','forex','gold','energy'):
        reasons.append('asset_class')
    if 'digits' in profile and profile['digits'] is not None:
        digits=profile['digits']
        if type(digits) is not int or not 0<=digits<=12:
            reasons.append('digits')
        elif 'point' in geometry and geometry['point']!=Decimal(10)**(-digits):
            reasons.append('point_digits_mismatch')
    return reasons
