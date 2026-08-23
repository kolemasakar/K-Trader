#!/usr/bin/env sh
set -eu

RUNNER_VERSION="2.336.0"
RUNNER_DIR="${KTRADER_RUNNER_DIR:-/opt/k-trader/runner}"
RUNNER_USER="${KTRADER_RUNNER_USER:-ktrader}"
RUNNER_NAME="${KTRADER_RUNNER_NAME:-$(hostname)-k-trader}"

case "$(uname -m)" in
    x86_64|amd64)
        RUNNER_ARCH="x64"
        RUNNER_SHA256="04cf0be1aff4c3ec3554466c39124ca250e3effd8873bb7e8d68535aa9505d5d"
        ARCH_LABEL="k-trader-prod-x64"
        ;;
    aarch64|arm64)
        RUNNER_ARCH="arm64"
        RUNNER_SHA256="58b758e420b87093fbd4bfddd368074960053e2f1388f01848c82624b90f27d1"
        ARCH_LABEL="k-trader-prod-arm64"
        ;;
    *)
        echo "unsupported runner architecture: $(uname -m)" >&2
        exit 1
        ;;
esac

RUNNER_ARCHIVE="actions-runner-linux-${RUNNER_ARCH}-${RUNNER_VERSION}.tar.gz"
RUNNER_LABELS="${KTRADER_RUNNER_LABELS:-k-trader-prod,$ARCH_LABEL}"

if [ "$(id -u)" -ne 0 ]; then
    echo "run as root" >&2
    exit 1
fi
: "${GITHUB_RUNNER_URL:?set GITHUB_RUNNER_URL, for example https://github.com/OWNER/K-Trader}"
: "${GITHUB_RUNNER_TOKEN:?set the short-lived repository runner registration token}"

id "$RUNNER_USER" >/dev/null 2>&1 || { echo "runner user $RUNNER_USER does not exist" >&2; exit 1; }
mkdir -p "$RUNNER_DIR"

if [ -f "$RUNNER_DIR/.runner" ]; then
    echo "runner is already configured in $RUNNER_DIR" >&2
    exit 1
fi

archive="$RUNNER_DIR/$RUNNER_ARCHIVE"
curl -fL --retry 3 \
    "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_ARCHIVE}" \
    -o "$archive"
printf '%s  %s\n' "$RUNNER_SHA256" "$archive" | sha256sum -c -

tar -xzf "$archive" -C "$RUNNER_DIR"
rm -f "$archive"
"$RUNNER_DIR/bin/installdependencies.sh"
chown -R "$RUNNER_USER:$RUNNER_USER" "$RUNNER_DIR"

runuser -u "$RUNNER_USER" -- env \
    GITHUB_RUNNER_URL="$GITHUB_RUNNER_URL" \
    GITHUB_RUNNER_TOKEN="$GITHUB_RUNNER_TOKEN" \
    RUNNER_NAME="$RUNNER_NAME" \
    RUNNER_DIR="$RUNNER_DIR" \
    RUNNER_LABELS="$RUNNER_LABELS" \
    sh -c 'cd "$RUNNER_DIR" && ./config.sh --url "$GITHUB_RUNNER_URL" --token "$GITHUB_RUNNER_TOKEN" --name "$RUNNER_NAME" --labels "$RUNNER_LABELS" --work _work --unattended --replace'

cd "$RUNNER_DIR"
./svc.sh install "$RUNNER_USER"
./svc.sh start
./svc.sh status

printf '%s\n' "PASS GitHub Actions runner ${RUNNER_VERSION} (${RUNNER_ARCH}) registered with labels ${RUNNER_LABELS}"
