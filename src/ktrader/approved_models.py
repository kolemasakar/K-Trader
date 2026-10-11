"""Owner-approved research models. No legacy strategy or trading API imports.

All observations are causal prefixes supplied by the scheduler; gates are
explicit evidence, not values guessed from incomplete broker metadata.
"""
from dataclasses import dataclass, field, replace
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR


def dec(x):
    v = Decimal(str(x))
    if not v.is_finite():
        raise ValueError('nonfinite value')
    return v


def round_price(value, tick, up):
    tick = dec(tick)
    if tick <= 0:
        raise ValueError('positive verified tick required')
    return (dec(value) / tick).to_integral_value(
        rounding=ROUND_CEILING if up else ROUND_FLOOR) * tick


@dataclass(frozen=True)
class Bar:
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal

    @classmethod
    def from_row(cls, row):
        return cls(*(dec(row[k]) for k in ('open', 'high', 'low', 'close')))

    def __post_init__(self):
        if not self.low <= min(self.open, self.close) <= max(self.open, self.close) <= self.high:
            raise ValueError('invalid OHLC')


def trend(bars):
    highs, lows = [], []
    for i in range(2, len(bars)-2):
        if all(bars[i].high > bars[j].high for j in (i-2, i-1, i+1, i+2)):
            highs.append(bars[i].high)
        if all(bars[i].low < bars[j].low for j in (i-2, i-1, i+1, i+2)):
            lows.append(bars[i].low)
    if len(highs) < 2 or len(lows) < 2:
        return 'UNKNOWN'
    if highs[-1] > highs[-2] and lows[-1] > lows[-2]:
        return 'UP'
    if highs[-1] < highs[-2] and lows[-1] < lows[-2]:
        return 'DOWN'
    return 'NEUTRAL'


def large_bar(bar, preceding):
    if len(preceding) < 20:
        return None
    mean = sum((b.high-b.low for b in preceding[-20:]), dec(0))/20
    return None if mean <= 0 else bar.high-bar.low >= 2*mean


def squeeze(bars, level, side):
    """side is direction of prospective breakout."""
    if len(bars) < 3:
        return False
    a,b,c = (x.close for x in bars[-3:])
    return a < b < c <= level if side == 1 else a > b > c >= level


def luft(level, asset_class, point):
    if asset_class in ('us_equity', 'crypto'):
        return dec(level)*dec('.0004')
    if asset_class == 'gold':
        return dec('.15')
    if asset_class == 'energy':
        return dec('.03')
    if asset_class == 'forex' and point is not None and dec(point) > 0:
        return 3*dec(point)
    raise ValueError('unsupported class or missing point; no guessed silver rule')


@dataclass(frozen=True)
class Context:
    level: Decimal
    side: int
    delta: Decimal
    tick: Decimal
    point: Decimal
    atr: Decimal
    asset_class: str
    admitted: bool
    strengthened: bool
    approach: tuple
    daily_direction: str
    space_verified: bool
    session: str = 'NOT_EVALUATED_TIMEZONE_UNKNOWN'
    interval_ended: bool = False
    technical_stop: Decimal | None = None
    channel: tuple | None = None
    forex_stop_points: int | None = None
    opposing_level: Decimal | None = None
    breakout_next_level: Decimal | None = None

    def __post_init__(self):
        if self.side not in (-1, 1) or min(self.level,self.delta,self.tick,self.point,self.atr) <= 0:
            raise ValueError('invalid verified context')

    @property
    def target_r(self):
        return dec('1.5') if self.asset_class == 'crypto' else dec(3)


@dataclass(frozen=True)
class Order:
    model: str
    side: int
    level: Decimal
    entry: Decimal
    stop: Decimal
    target: Decimal
    kind: str
    target_r: Decimal

    @property
    def distance(self):
        return abs(self.entry-self.stop)


def gates(ctx, model, last_close, observed, previous):
    reasons = []
    if not ctx.admitted or not ctx.strengthened:
        reasons.append('LEVEL_NOT_ADMITTED_OR_STRENGTH_UNCONFIRMED')
    if not ctx.space_verified:
        reasons.append('TARGET_SPACE_UNVERIFIED')
    if model in ('S1', 'CHANNEL', 'S2A', 'S2B', 'S3') and ctx.session == 'BLOCKED':
        reasons.append('SESSION_BLOCKED')
    if model in ('CHANNEL', 'S2A', 'S2B', 'S3') and ctx.interval_ended:
        reasons.append('INTERVAL_ENDED')
    if model in ('S1', 'S2A', 'S2B', 'S3'):
        direction = ctx.side if model.startswith('S2') or model == 'S3' else -ctx.side
        expected = 'UP' if direction == 1 else 'DOWN'
        # S3 stores the initial breakout approach, never recomputes on retest.
        if ctx.approach != (expected,)*3:
            reasons.append('APPROACH_MISALIGNMENT')
    if model in ('S4','S5A','S5B'):
        if ctx.daily_direction != ('UP' if ctx.side == 1 else 'DOWN'):
            reasons.append('D1_DIRECTION_UNCONFIRMED')
    if model != 'CHANNEL':
        spent = max(dec(0),ctx.side*(last_close-ctx.level))
        if ctx.atr-spent < dec('.6')*ctx.atr:
            reasons.append('MOVE_RESERVE')
    big = large_bar(observed,previous)
    if big is not False:
        reasons.append('LARGE_BAR' if big else 'ACTIVITY_UNKNOWN')
    return reasons


def make_order(ctx, model, observed, *, structure=None, bounds=None):
    s,L,d,t = ctx.side,ctx.level,ctx.delta,ctx.tick
    anchor = L
    if model == 'S2B':
        if bounds is None:
            raise ValueError('frozen range required')
        D,U = bounds
        anchor = max(L,U) if s == 1 else min(L,D)
    # Limits round toward L and must remain within the allowed luft.
    entry = round_price(anchor+s*d,t,up=s == 1 if model not in ('S1','S3','CHANNEL') else s == -1)
    if model in ('S1','CHANNEL'):
        if ctx.asset_class == 'gold':
            stop = L-s*dec(3)
        elif ctx.asset_class == 'energy':
            stop = L-s*dec('.20')
        elif ctx.asset_class == 'forex':
            if ctx.forex_stop_points not in (20,25):
                raise ValueError('Forex base stop needs explicit 20/25 Point symbol profile')
            stop = L-s*ctx.forex_stop_points*ctx.point
        else:
            if ctx.technical_stop is None:
                raise ValueError('verified protective structure required')
            stop = ctx.technical_stop
    elif model == 'S3':
        stop = L-s*2*d
    else:
        b = structure or observed
        stop = min(L-2*d,b.low-2*t) if s == 1 else max(L+2*d,b.high+2*t)
    stop = round_price(stop,t,up=s == -1)
    distance = s*(entry-stop)
    if distance <= 0:
        raise ValueError('invalid stop geometry')
    if model in ('S1','CHANNEL'):
        if not 0 <= s*(entry-L) <= d:
            raise ValueError('limit outside luft')
        if ctx.asset_class == 'us_equity' and distance > dec('.002')*L:
            raise ValueError('equity technical stop cap')
        if ctx.asset_class == 'crypto' and distance > dec('.20')*ctx.atr:
            raise ValueError('technical stop cap')
    target = entry+s*ctx.target_r*distance
    if ctx.opposing_level is not None and s*(ctx.opposing_level-target)<0:
        raise ValueError('insufficient space to opposing level')
    if model == 'CHANNEL':
        if ctx.channel is None:
            raise ValueError('channel boundaries required')
        D,U = ctx.channel
        if not D < U or ctx.target_r*distance > dec('.8')*(U-D) or not D <= target <= U:
            raise ValueError('channel 80 percent or boundary')
    return Order(model,s,L,entry,stop,target,
                 'LIMIT' if model in ('S1','S3','CHANNEL') else 'PROGRAMMATIC_STOP',ctx.target_r)


def rebound(ctx, first, observed, preceding, *, model='S1', compression_active=False):
    s,L = ctx.side,ctx.level
    tolerance = 2*ctx.point if ctx.asset_class == 'forex' else dec(0)
    a = first.low if s == 1 else first.high
    b = observed.low if s == 1 else observed.high
    reasons = gates(ctx,model,first.close,observed,preceding)
    if not 0 <= s*(a-L) <= tolerance:
        reasons.append('BPU1_TOUCH')
    if not 0 <= s*(b-L) <= ctx.delta:
        reasons.append('BPU2_TOUCH_OR_PENETRATION')
    if compression_active:
        reasons.append('COMPRESSION_ACTIVE')
    return reasons


def consolidation(bars, ctx):
    """Twenty closed bars before the three compression bars; no sliding bounds."""
    if len(bars) != 20:
        return None
    U,D = max(x.high for x in bars),min(x.low for x in bars)
    if not 0 < U-D <= ctx.atr/3:
        return None
    boundary = U if ctx.side == 1 else D
    if abs(boundary-ctx.level) > ctx.delta:
        return None
    for upper in (True,False):
        hits = [i for i,b in enumerate(bars) if
                (U-ctx.delta <= b.high <= U if upper else D <= b.low <= D+ctx.delta)]
        if not any(j-i >= 2 for i in hits for j in hits if j > i):
            return None
    return D,U


@dataclass
class ModelState:
    """Lifecycle consumes completed bars and live-prefix price events separately."""
    model: str
    ctx: Context
    phase: str = 'IDLE'
    structure: list = field(default_factory=list)
    frozen_bounds: tuple | None = None
    approach_close: Decimal | None = None
    order: Order | None = None
    reasons: list = field(default_factory=list)

    def cancel(self, reason):
        self.phase = 'CANCELLED'
        self.reasons.append(reason)

    def on_closed(self, history):
        bar = history[-1]
        s,L = self.ctx.side,self.ctx.level
        if self.phase == 'FILLED':
            return  # SL/TP only; never close a position with prefill rules
        if self.order is not None:
            if self.ctx.interval_ended and self.model in ('CHANNEL','S3'):
                self.cancel('INTERVAL_ENDED')
                return
            if abs(bar.close-L) >= 2*self.order.distance:
                self.cancel('CLOSE_DISTANCE_2R')
            return
        if self.model in ('S2A','S2B','S3'):
            if self.ctx.interval_ended:
                self.cancel('INTERVAL_ENDED')
                return
            if self.phase == 'RETEST_WAIT':
                if self.ctx.atr-max(dec(0),s*(bar.close-L)) < dec('.6')*self.ctx.atr or not self.ctx.admitted or not self.ctx.strengthened:
                    self.cancel('RETEST_PRECONDITIONS_LOST')
                return
            if self.phase == 'IDLE':
                bounds = consolidation(history[-23:-3],self.ctx) if self.model == 'S2B' else None
                boundary = (bounds[1] if s == 1 else bounds[0]) if bounds else L
                if self.model == 'S2B' and bounds is None:
                    return
                if squeeze(history,boundary,s):
                    if bounds and any(b.low < bounds[0] or b.high > bounds[1] for b in history[-3:]):
                        return
                    if gates(self.ctx,self.model,bar.close,bar,history[:-1]):
                        return
                    self.phase='ARMED'
                    self.frozen_bounds=bounds
                    self.approach_close=bar.close
            elif self.phase == 'ARMED':
                boundary = (self.frozen_bounds[1] if s == 1 else self.frozen_bounds[0]) if self.frozen_bounds else L
                if self.model == 'S3' and s*(bar.close-L)>0:
                    self.phase='RETEST_WAIT'
                elif abs(bar.close-boundary) >= abs(self.approach_close-boundary):
                    self.cancel('NO_CLOSER_CLOSE')
                else:
                    self.approach_close=bar.close
        elif self.model in ('S5A','S5B'):
            if self.phase == 'IDLE' and s*(bar.open-L)>0 and s*(bar.close-L)<0:
                if large_bar(bar,history[:-1]) is not False:
                    self.cancel('STRUCTURE_ACTIVITY')
                    return
                self.structure=[bar]
                self.phase='OUTSIDE'
            elif self.phase in ('OUTSIDE','ARMED'):
                if self.model == 'S5A':
                    self.cancel('SECOND_BAR_ENDED')
                    return
                if self.phase == 'OUTSIDE':
                    outside = bar.open<L and bar.close<L and bar.high<=L if s == 1 else bar.open>L and bar.close>L and bar.low>=L
                    if not outside:
                        self.cancel('RETURN_BEFORE_READY')
                        return
                if large_bar(bar,history[:-1]) is not False:
                    self.cancel('STRUCTURE_ACTIVITY')
                    return
                self.structure.append(bar)
                if len(self.structure)>=3:
                    self.phase='ARMED'

    def on_prefix(self, history, observed, previous_price, price, fraction, *, next_level_hit=False):
        """No final bar high/low/close may be passed before its availability."""
        if self.phase in ('CANCELLED','FILLED'):
            return None
        c,s,L = self.ctx,self.ctx.side,self.ctx.level
        if self.model in ('S1','S3','CHANNEL'):
            if self.model == 'S3' and self.phase != 'RETEST_WAIT' and self.order is None:
                return None
            if self.order:
                if s*((observed.low if s == 1 else observed.high)-L)<0:
                    self.cancel('CONFIRMATION_PENETRATION')
                return self.order if self.phase!='CANCELLED' else None
            if fraction == dec('.9') and history:
                compressed=squeeze(history,L,-s)
                reasons=rebound(c,history[-1],observed,history,model=self.model,compression_active=compressed)
                if reasons:
                    self.reasons=reasons
                    return None
                if self.model in ('S1','CHANNEL') and c.asset_class in ('us_equity','crypto'):
                    technical=(min(history[-1].low,observed.low)-3*c.point if s==1 else max(history[-1].high,observed.high)+3*c.point)
                    c=replace(c,technical_stop=technical)
                self.order=make_order(c,self.model,observed)
                self.phase='PENDING'
                return self.order
            return None
        if self.model == 'S4':
            if self.phase == 'IDLE' and s*(observed.open-L)>0 and s*((observed.low if s==1 else observed.high)-L)<=-c.tick:
                self.phase='ARMED'
            if fraction>=1:
                self.cancel('SAME_BAR_ENDED')
                return None
        if self.model == 'S5A' and self.phase == 'OUTSIDE':
            if s*(observed.open-L)>=0:
                self.cancel('SECOND_OPEN_NOT_OUTSIDE')
                return None
            self.phase='ARMED'
        if self.model == 'S5B' and next_level_hit:
            self.cancel('NEXT_STRONG_LEVEL_REACHED')
            return None
        if self.phase != 'ARMED':
            return None
        anchor=L
        if self.model=='S2B':
            anchor=max(L,self.frozen_bounds[1]) if s==1 else min(L,self.frozen_bounds[0])
        entry=round_price(anchor+s*c.delta,c.tick,up=s==1)
        if self.model=='S4' and abs(price-entry)>c.atr:
            self.cancel('AWAY_MORE_THAN_ATR')
            return None
        if not s*(previous_price-entry)<0<=s*(price-entry) or fraction>=1:
            return None
        current = observed
        if self.structure:
            current=Bar(observed.open,max([b.high for b in self.structure]+[observed.high]),
                        min([b.low for b in self.structure]+[observed.low]),observed.close)
        if self.model in ('S4','S5A','S5B'):
            depth=L-current.low if s==1 else current.high-L
            if depth>c.atr/3:
                self.cancel('FALSE_BREAK_DEPTH')
                return None
        sample=history[-1] if self.model.startswith('S2') else observed
        preceding=history[:-1] if self.model.startswith('S2') else history
        reasons=gates(c,self.model,history[-1].close,sample,preceding)
        if reasons:
            self.cancel(','.join(reasons))
            return None
        self.order=make_order(c,self.model,observed,structure=current,bounds=self.frozen_bounds)
        self.phase='PENDING'
        return self.order
