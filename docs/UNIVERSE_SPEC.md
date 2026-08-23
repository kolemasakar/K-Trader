# Universe Specification v1.0

## Goal

Build a configurable derivatives universe from public provider metadata.

## Canonical filters

For a provider/instrument to be eligible:
- trading status is active;
- derivative is perpetual/swap equivalent;
- configured quote asset matches, default USDT;
- instrument metadata is complete enough for normalized analysis;
- price limit passes when enabled.

Default configuration:

```yaml
universe:
  quote_asset: USDT
  perpetual_only: true
  price_limit:
    enabled: true
    max_price: 3.0
  max_candidates: 50
```

`price_limit.enabled: false` means all eligible assets.

## Refresh

Universe metadata is refreshed periodically and on provider reconnect/restart. Delisted, suspended or stale instruments are removed from active scanning.

## Output

Universe rows include provider, canonical/provider symbol, status, contract type, last price, liquidity inputs, eligibility reason and exclusion reason when filtered out.
