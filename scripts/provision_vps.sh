#!/usr/bin/env sh
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "run as root" >&2
    exit 1
fi

if [ ! -f /etc/os-release ]; then
    echo "unsupported Linux: /etc/os-release missing" >&2
    exit 1
fi

. /etc/os-release
if [ "${ID:-}" != "ubuntu" ]; then
    echo "this provisioning baseline supports Ubuntu only" >&2
    exit 1
fi

DEB_ARCH="$(dpkg --print-architecture)"
case "$DEB_ARCH" in
    arm64|amd64) ;;
    *)
        echo "unsupported Ubuntu architecture: $DEB_ARCH" >&2
        exit 1
        ;;
esac

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y ca-certificates curl gnupg git tar

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=${DEB_ARCH} signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu ${VERSION_CODENAME} stable" \
    > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker

if ! id ktrader >/dev/null 2>&1; then
    useradd --create-home --shell /bin/bash ktrader
fi
usermod -aG docker ktrader

install -d -o ktrader -g ktrader /opt/k-trader
install -d -o ktrader -g ktrader -m 0755 /opt/k-trader/releases
install -d -o ktrader -g ktrader -m 0750 /opt/k-trader/data
install -d -o ktrader -g ktrader -m 0755 /opt/k-trader/runner

# The Caddy container starts as uid 0 with all Linux capabilities dropped.
# Without CAP_DAC_OVERRIDE it must own its bind-mounted /data and /config trees
# to persist ACME accounts/certificates and autosave configuration.
install -d -o root -g root -m 0700 /opt/k-trader/caddy_data
install -d -o root -g root -m 0700 /opt/k-trader/caddy_config

printf '%s\n' "PASS Ubuntu/Docker provisioning complete on ${DEB_ARCH}"
printf '%s\n' "Next: obtain a repository Actions runner registration token and run scripts/register_runner.sh as root."
printf '%s\n' "Firewall/SSH policy is intentionally not changed automatically; apply the documented VPS security checklist before exposing HTTPS."
