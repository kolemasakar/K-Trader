from pathlib import Path

from fastapi.testclient import TestClient
import pytest
import yaml

from ktrader.action_package import (
    REQUIRED_OPERATION_IDS,
    render_action_schema,
    validate_action_schema_text,
    validate_server_url,
)
from ktrader.api.app import create_app


SCHEMA_PATH = Path("custom_gpt/openapi.yaml")
PRODUCTION_SERVER = "https://ktrader-api.duckdns.org"


def test_canonical_action_schema_is_valid_yaml_read_only_and_complete():
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    operation_ids = set(validate_action_schema_text(text, allow_placeholder=False))
    schema = yaml.safe_load(text)
    assert schema["openapi"].startswith("3.")
    assert schema["servers"][0]["url"] == PRODUCTION_SERVER
    assert operation_ids == REQUIRED_OPERATION_IDS
    for operations in schema["paths"].values():
        assert set(operations).issubset({"get", "parameters"})


def test_gpt_builder_operation_parameters_are_inline_and_named():
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    for path_item in schema["paths"].values():
        operation = path_item.get("get")
        if not operation:
            continue
        for parameter in operation.get("parameters", []):
            assert "$ref" not in parameter
            assert isinstance(parameter.get("name"), str)
            assert parameter["name"]
            assert parameter.get("in") in {"path", "query"}


def test_public_action_schema_endpoint_returns_exact_canonical_bytes_without_auth():
    app = create_app(action_api_key="test-secret", action_openapi_path=SCHEMA_PATH)
    response = TestClient(app).get("/action-openapi.yaml")

    assert response.status_code == 200
    assert response.content == SCHEMA_PATH.read_bytes()
    assert response.headers["content-type"].startswith("application/yaml")


def test_render_action_schema_replaces_current_server_origin():
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    rendered = render_action_schema(text, "https://ktrader.example.com/")
    schema = yaml.safe_load(rendered)
    assert schema["servers"][0]["url"] == "https://ktrader.example.com"
    assert PRODUCTION_SERVER not in rendered


@pytest.mark.parametrize("url", ["http://example.com", "https://example.com/path", "https://user:pass@example.com"])
def test_action_server_rejects_unsafe_origin(url):
    with pytest.raises(ValueError):
        validate_server_url(url)
