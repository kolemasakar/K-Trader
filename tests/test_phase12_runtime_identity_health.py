from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_container_runtime_identity_matches_deployment_user() -> None:
    dockerfile = read("Dockerfile")
    compose = read("docker-compose.yml")
    deploy = read("scripts/deploy.sh")

    assert "ARG KTRADER_RUNTIME_UID=1000" in dockerfile
    assert "ARG KTRADER_RUNTIME_GID=1000" in dockerfile
    assert 'useradd --uid "${KTRADER_RUNTIME_UID}"' in dockerfile
    assert "KTRADER_RUNTIME_UID: ${KTRADER_RUNTIME_UID:-1000}" in compose
    assert "KTRADER_RUNTIME_GID: ${KTRADER_RUNTIME_GID:-1000}" in compose
    assert 'export KTRADER_RUNTIME_UID="${KTRADER_RUNTIME_UID:-$(id -u)}"' in deploy
    assert 'export KTRADER_RUNTIME_GID="${KTRADER_RUNTIME_GID:-$(id -g)}"' in deploy


def test_deployment_fails_closed_when_data_directory_is_not_writable() -> None:
    deploy = read("scripts/deploy.sh")

    writable_gate = deploy.index('if [ ! -w "$ROOT/data" ]')
    build = deploy.index("docker compose $PROFILE_ARGS build --pull")
    assert writable_gate < build
    assert "fix production data ownership before deployment" in deploy


def test_service_health_allows_fresh_partial_scanner_degradation() -> None:
    api = read("src/ktrader/api/app.py")
    compose = read("docker-compose.yml")
    dockerfile = read("Dockerfile")

    assert '"watchdog_ok": watchdog_ok' in api
    for source in (compose, dockerfile):
        assert "p.get('data_ready')" in source
        assert "p.get('watchdog_ok')" in source
        assert "p.get('scanner_status') in {'READY','DEGRADED'}" in source
