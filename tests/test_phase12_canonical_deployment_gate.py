from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_production_workflow_and_docs_target_arm64_runner() -> None:
    workflow = read(".github/workflows/deploy.yml")
    deployment = read("docs/DEPLOYMENT.md")

    assert "k-trader-prod-arm64" in workflow
    assert "k-trader-prod-arm64" in deployment
    assert "Verify Oracle production architecture" in workflow


def test_public_https_release_requires_action_key_and_phase10_acceptance() -> None:
    deploy = read("scripts/deploy.sh")

    domain_gate = deploy.index('if [ -n "${KTRADER_DOMAIN:-}" ]')
    api_key_gate = deploy.index('public HTTPS deployment requires KTRADER_ACTION_API_KEY')
    phase10 = deploy.index("phase10_action_acceptance.py")
    mark_current = deploy.index('ln -sfn "$RELEASE" "$CURRENT"')

    assert domain_gate < api_key_gate < phase10 < mark_current
    assert 'action_url="https://${KTRADER_DOMAIN}"' in deploy
    assert "new release failed public HTTPS/Action acceptance" in deploy
    assert "rollback" in deploy


def test_phase9_acceptance_authenticates_local_v1_checks_when_action_auth_is_enabled() -> None:
    phase9 = read("scripts/phase9_acceptance.sh")

    assert 'os.environ.get("KTRADER_ACTION_API_KEY", "")' in phase9
    assert 'headers["Authorization"] = f"Bearer {action_api_key}"' in phase9
    assert 'request_json(base + "/v1/scanner/status")' in phase9
    assert 'request_json(base + "/v1/candidates?limit=1")' in phase9
    assert "payload = request_json(url)" in phase9


def test_environment_example_documents_action_and_operational_controls() -> None:
    env_example = read("deploy/.env.example")

    assert "KTRADER_ACTION_API_KEY=" in env_example
    assert "KTRADER_DOMAIN=" in env_example
    assert "KTRADER_BACKUP_ENABLED=true" in env_example
    assert "KTRADER_HEALTH_MAX_SCAN_AGE_SECONDS=180" in env_example
    assert "Do not commit populated secrets" in env_example


def test_openapi_stays_placeholder_until_real_https_acceptance() -> None:
    openapi = read("custom_gpt/openapi.yaml")
    assert "https://api.k-trader.invalid" in openapi
