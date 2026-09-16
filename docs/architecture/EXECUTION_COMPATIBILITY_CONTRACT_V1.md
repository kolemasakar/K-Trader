# K-Trader Execution Compatibility Contract v1

Status: **DESIGN CONTRACT / NO ORDER EXECUTION AUTHORIZED**

## Purpose

Define the minimum normalized instrument and execution metadata that any future K-Trader risk/execution layer must possess before it can safely transform a canonical trading decision into an order request.

The current production boundary remains read-only. This contract does not add order endpoints, credentials or trading permissions.

## Existing normalized instrument fields

The current model already exposes:

- `provider_id`;
- `symbol`;
- `base_asset`;
- `quote_asset`;
- `market_type`;
- `contract_type`;
- `status`;
- `price_tick`;
- `quantity_step`;
- `provider_symbol`;
- provider metadata.

`price_tick` and `quantity_step` are necessary but not sufficient for future execution.

## Required execution-spec fields

A future versioned `NormalizedExecutionSpec` should include, where applicable:

### Identity / market

- `provider_id`;
- `symbol`;
- `provider_symbol`;
- `market_type`;
- `contract_type`;
- `status`;
- `settlement_asset` / margin asset;
- contract multiplier / contract size.

### Price constraints

- `price_tick`;
- minimum price, if exchange-enforced;
- maximum price, if exchange-enforced;
- price precision only as display/serialization metadata when tick size is authoritative.

### Quantity constraints

- `quantity_step`;
- `min_quantity`;
- `max_quantity`;
- quantity precision only when needed for transport;
- minimum notional / order value;
- maximum notional where applicable.

### Order constraints

- supported order types;
- supported time-in-force values;
- market-order availability;
- stop/conditional-order availability;
- reduce-only support;
- close-position semantics where applicable;
- client-order-id limits if used;
- provider-specific trigger/working-price modes if required.

### Margin / position constraints

- supported margin modes;
- current required margin mode when account-bound execution is introduced;
- supported position modes (`ONE_WAY`, `HEDGE`, etc.);
- leverage minimum/maximum/step or discrete allowed values;
- leverage brackets / notional tiers where applicable;
- maintenance-margin information needed by risk calculations.

## Normalization rules

- price normalization must use `price_tick`, never decimal-display precision alone;
- quantity normalization must use `quantity_step`;
- rounding direction must be explicit and safe for each field;
- normalized SL/TP must be revalidated after rounding;
- minimum quantity/notional checks occur after rounding;
- maximum quantity/notional/leverage checks occur before authorization;
- all Decimal-sensitive values must avoid binary-float order construction;
- provider-native symbol mapping must be explicit;
- spot, perpetual and dated futures contracts must never be silently substituted.

## Fail-closed pre-trade gates

A future executor must refuse authorization when any required execution metadata is missing or stale.

Minimum gates:

1. instrument is currently tradable;
2. market/contract type matches the strategy decision;
3. price tick and quantity step are known;
4. min/max quantity constraints are known and passed;
5. minimum notional is known and passed where applicable;
6. normalized Entry/SL/TP remain logically valid;
7. margin/position mode is compatible;
8. leverage/notional tier is compatible;
9. portfolio-risk caps pass;
10. available margin check passes;
11. idempotency/authorization identifier is valid;
12. provider/execution metadata freshness passes.

Any failed or unknown mandatory gate => `EXECUTION_REJECTED`, not silent coercion.

## Separation from strategy

Execution normalization must not alter strategy meaning.

Examples:

- if tick rounding destroys the required stop distance, reject rather than silently widen risk;
- if minimum notional requires a position larger than the authorized risk, reject;
- if max quantity prevents the intended position size, reject or explicitly re-size only under a separately authorized sizing policy;
- broker/exchange constraints must never be interpreted as evidence that a setup is statistically better or worse.

## Provider adapter responsibility

Each provider adapter should translate native exchange filters into this normalized contract and retain raw provider metadata for audit.

The core RiskManager/Executor should depend on the normalized contract, not provider-specific filter names.

## Testing requirements

Before any execution phase can be activated, tests must cover at minimum:

- exact tick normalization;
- exact quantity-step normalization;
- min quantity;
- max quantity;
- min notional;
- conflicting price/quantity precision;
- insufficient margin;
- leverage bracket boundary;
- one-way vs hedge mode mismatch;
- reduce-only semantics;
- duplicate/idempotent authorization;
- stale execution spec;
- unsupported order type;
- post-rounding SL/TP invalidation.

## Current state

This contract is architecture preparation only.

Current K-Trader production remains:

- read-only;
- no exchange-account access;
- no order create/modify/cancel endpoint;
- no execution credential;
- no production trading authorization.
