# Security Specification v1.0

## v1 trust boundary

K-Trader v1 is read-only and uses public exchange market-data APIs only.

Prohibited in v1:
- exchange API secrets
- account access
- order endpoints
- withdrawal/deposit endpoints
- automated execution

## Public K-Trader API

- HTTPS only.
- GET/read-only operations only.
- Input validation for symbols/query parameters.
- Rate limiting.
- Bounded response sizes.
- No arbitrary URL fetching from API parameters.
- No shell/command execution surfaces.

## VPS

- Minimal exposed ports.
- SSH key authentication; disable password login where operationally appropriate.
- Regular OS/container updates.
- Docker volumes with least-required permissions.
- Firewall/reverse proxy configuration documented.

## GitHub runner

- Private repo only.
- Do not execute untrusted PR/fork code on production runner.
- Keep runner updated.
- Separate future secrets from repository contents.

## Fail-closed rules

Any uncertainty in provider freshness, data integrity or engine readiness prevents tradable signal output.
