#!/usr/bin/env sh
set -eu

ROOT="${KTRADER_ROOT:-/opt/k-trader}"
SHA="$(git rev-parse HEAD)"
RELEASE="$ROOT/releases/$SHA"
CURRENT="$ROOT/current"
PREVIOUS=""

command -v docker >/dev/null 2>&1 || { echo "docker is required" >&2; exit 1; }
docker compose version >/dev/null 2>&1 || { echo "docker compose plugin is required" >&2; exit 1; }

for path in "$ROOT" "$ROOT/releases" "$ROOT/data" "$ROOT/caddy_data" "$ROOT/caddy_config"; do
    mkdir -p "$path" 2>/dev/null || {
        echo "cannot create $path; pre-provision /opt/k-trader for the runner user" >&2
        exit 1
    }
done

if [ ! -w "$ROOT/data" ]; then
    echo "runner user cannot write $ROOT/data; fix production data ownership before deployment" >&2
    exit 1
fi

if [ -L "$CURRENT" ]; then
    PREVIOUS="$(readlink -f "$CURRENT" || true)"
fi

rm -rf "$RELEASE"
mkdir -p "$RELEASE"
git archive --format=tar HEAD | tar -xf - -C "$RELEASE"

cd "$RELEASE"
export KTRADER_ROOT="$ROOT"
export KTRADER_IMAGE_TAG="$SHA"
export KTRADER_RUNTIME_UID="${KTRADER_RUNTIME_UID:-$(id -u)}"
export KTRADER_RUNTIME_GID="${KTRADER_RUNTIME_GID:-$(id -g)}"

PROFILE_ARGS=""
if [ -n "${KTRADER_DOMAIN:-}" ]; then
    PROFILE_ARGS="--profile https"
fi

rollback() {
    if [ -n "$PREVIOUS" ] && [ -d "$PREVIOUS" ]; then
        prev_sha="$(basename "$PREVIOUS")"
        echo "rolling back to $prev_sha" >&2
        cd "$PREVIOUS"
        export KTRADER_IMAGE_TAG="$prev_sha"
        docker compose $PROFILE_ARGS up -d --remove-orphans
    else
        cd "$RELEASE"
        docker compose $PROFILE_ARGS down || true
    fi
}

echo "Building K-Trader release $SHA for runtime uid:gid ${KTRADER_RUNTIME_UID}:${KTRADER_RUNTIME_GID}"
docker compose $PROFILE_ARGS build --pull

echo "Starting K-Trader release $SHA"
docker compose $PROFILE_ARGS up -d --remove-orphans

healthy=0
attempt=1
while [ "$attempt" -le 24 ]; do
    if python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3).read()" >/dev/null 2>&1; then
        healthy=1
        break
    fi
    sleep 5
    attempt=$((attempt + 1))
done

if [ "$healthy" -ne 1 ]; then
    echo "new release failed process health check" >&2
    rollback
    exit 1
fi

if ! ./scripts/phase9_acceptance.sh; then
    echo "new release failed market/runtime acceptance" >&2
    rollback
    exit 1
fi

if [ -n "${KTRADER_DOMAIN:-}" ]; then
    if [ -z "${KTRADER_ACTION_API_KEY:-}" ]; then
        echo "public HTTPS deployment requires KTRADER_ACTION_API_KEY" >&2
        rollback
        exit 1
    fi

    action_url="https://${KTRADER_DOMAIN}"
    echo "Waiting for public HTTPS and Phase 10 Action acceptance at $action_url"
    action_ready=0
    attempt=1
    while [ "$attempt" -le 24 ]; do
        if python3 ./scripts/phase10_action_acceptance.py --base-url "$action_url"; then
            action_ready=1
            break
        fi
        sleep 5
        attempt=$((attempt + 1))
    done

    if [ "$action_ready" -ne 1 ]; then
        echo "new release failed public HTTPS/Action acceptance" >&2
        rollback
        exit 1
    fi
fi

ln -sfn "$RELEASE" "$CURRENT"
printf '%s\n' "$SHA" > "$ROOT/DEPLOYED_SHA"

echo "Deployed $SHA"
docker compose $PROFILE_ARGS ps
