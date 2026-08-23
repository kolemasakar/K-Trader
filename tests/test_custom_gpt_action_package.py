from pathlib import Path

import pytest
import yaml

from ktrader.action_package import (
    PLACEHOLDER_SERVER,
    REQUIRED_OPERATION_IDS,
    render_action_schema,
    validate_action_schema_text,
    validate_server_url,
)


SCHEMA_PATH = Path("custom_gpt/openapi.yaml")


def test_canonical_action_schema_is_valid_yaml_read_only_and_complete():
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    operation_ids = set(validate_action_schema_text(text, allow_placeholder=True))
    schema = yaml.safe_load(text)
    assert schema["openapi"].startswith("3.")
    assert schema["servers"][0]["url"] == PLACEHOLDER_SERVER
    assert operation_ids == REQUIRED_OPERATION_IDS
    for operations in schema["paths"].values():
        assert set(operations).issubset({"get", "parameters"})


def test_render_action_schema_replaces_only_server_placeholder():
    text = SCHEMA_PATH.read_text(encoding="utf-8")
    rendered = render_action_schema(text, "https://ktrader.example.com/")
    schema = yaml.safe_load(rendered)
    assert schema["servers"][0]["url"] == "https://ktrader.example.com"
    assert PLACEHOLDER_SERVER not in rendered


@pytest.mark.parametrize("url", ["http://example.com", "https://example.com/path", "https://user:pass@example.com"])
def test_action_server_rejects_unsafe_origin(url):
    with pytest.raises(ValueError):
        validate_server_url(url)
