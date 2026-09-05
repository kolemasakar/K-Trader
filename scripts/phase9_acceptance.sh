#!/usr/bin/env sh
set -eu

providers="$(printf '%s' "${KTRADER_PROVIDERS:-binance_usdm,bybit_linear}" | tr ',' ' ')"

echo "[1/3] Public provider REST/WebSocket acceptance"
# shellcheck disable=SC2086
docker compose exec -T ktrader python scripts/vps_acceptance.py --providers $providers

echo "[2/3] Waiting for scanner data readiness"
KTRADER_ACCEPTANCE_ATTEMPTS="${KTRADER_ACCEPTANCE_ATTEMPTS:-180}" python3 - <<'PY'
import json
import os
import time
import urllib.parse
import urllib.request

base = "http://127.0.0.1:8000"
attempts = int(os.environ.get("KTRADER_ACCEPTANCE_ATTEMPTS", "180"))
action_api_key = os.environ.get("KTRADER_ACTION_API_KEY", "").strip() or None


def request_json(url: str):
    headers = {"Accept": "application/json"}
    if action_api_key:
        headers["Authorization"] = f"Bearer {action_api_key}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=5) as response:
        return json.load(response)


last = None
for _ in range(attempts):
    try:
        last = request_json(base + "/v1/scanner/status")
        if last.get("data_ready"):
            break
    except Exception as exc:
        last = {"error": f"{type(exc).__name__}: {exc}"}
    time.sleep(5)
else:
    raise SystemExit(f"scanner did not become data_ready: {last}")

candidates = request_json(base + "/v1/candidates?limit=1").get("items", [])
if not candidates:
    raise SystemExit("data_ready scanner published no candidates")

item = candidates[0]
symbol = item["canonical_symbol"]
provider = item["provider_id"]
for interval in ("5m", "15m", "1h", "4h", "1d"):
    query = urllib.parse.urlencode(
        {"provider_id": provider, "interval": interval, "limit": 5}
    )
    url = f"{base}/v1/candles/{urllib.parse.quote(symbol)}?{query}"
    payload = request_json(url)
    if payload.get("count", 0) < 1:
        raise SystemExit(f"runtime published no {interval} candles for {provider}:{symbol}")

print(
    "PASS runtime "
    f"status={last.get('status')} provider={last.get('provider_id')} "
    f"symbols_ready={last.get('symbols_ready')} symbols_failed={last.get('symbols_failed')}"
)
print(f"PASS MTF API provider={provider} symbol={symbol} intervals=5m,15m,1h,4h,1d")
PY

echo "[3/3] Container state"
docker compose ps
