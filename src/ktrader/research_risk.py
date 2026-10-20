"""Verified monetary sizing, never guesses zero costs or contract geometry."""
from dataclasses import dataclass
from decimal import ROUND_FLOOR
from ktrader.approved_models import dec


@dataclass(frozen=True)
class RiskProfile:
    value_per_price_unit: object
    volume_min: object
    volume_step: object
    volume_max: object
    estimated_round_trip_cost_per_unit: object
    provenance: str


def size_position(distance, deposit, profile):
    if profile is None or not profile.provenance or profile.estimated_round_trip_cost_per_unit is None:
        return {'status':'UNKNOWN_METADATA_OR_COSTS','volume':None}
    distance,deposit=dec(distance),dec(deposit)
    value,minimum,step,maximum,cost=map(dec,(profile.value_per_price_unit,profile.volume_min,
                                          profile.volume_step,profile.volume_max,
                                          profile.estimated_round_trip_cost_per_unit))
    if min(distance,deposit,value,minimum,step,maximum)<=0 or cost<0 or maximum<minimum:
        raise ValueError('invalid verified risk profile')
    budget=dec('.005')*deposit
    unit_loss=distance*value+cost
    cap=min(maximum,budget/unit_loss)
    quantity=(cap/step).to_integral_value(rounding=ROUND_FLOOR)*step
    if quantity<minimum:
        return {'status':'BELOW_MINIMUM','volume':None}
    return {'status':'SIZED','volume':str(quantity),'budget':str(budget),
            'estimated_loss':str(quantity*unit_loss),'profile_provenance':profile.provenance}
