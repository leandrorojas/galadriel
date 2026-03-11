"""Tests for YAML utility helpers."""

import pytest
from importlib import util
from pathlib import Path
import yaml

# Import the YAML utils module directly to avoid executing package side effects
spec = util.spec_from_file_location(
    "yaml_utils", Path(__file__).resolve().parents[1] / "galadriel" / "utils" / "yaml.py"
)
yaml_utils = util.module_from_spec(spec)
spec.loader.exec_module(yaml_utils)

pytestmark = pytest.mark.unit


def test_write_setting_creates_file_and_section(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    assert yaml_utils.read_setting(str(cfg_path), "galadriel", "first_run") is None

    yaml_utils.write_setting(str(cfg_path), "galadriel", "first_run", 1)
    assert yaml_utils.read_setting(str(cfg_path), "galadriel", "first_run") == 1

    with cfg_path.open() as f:
        data = yaml.safe_load(f)
    assert data["galadriel"]["first_run"] == 1


def test_read_setting_missing_file(tmp_path):
    result = yaml_utils.read_setting(str(tmp_path / "nope.yaml"), "sec", "key")
    assert result is None


def test_read_setting_missing_section(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(yaml.safe_dump({"other": {"k": "v"}}))
    assert yaml_utils.read_setting(str(cfg), "missing", "k") is None


def test_read_setting_missing_key(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(yaml.safe_dump({"sec": {"a": 1}}))
    assert yaml_utils.read_setting(str(cfg), "sec", "missing") is None


def test_write_setting_overwrites(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    yaml_utils.write_setting(str(cfg), "s", "k", "old")
    yaml_utils.write_setting(str(cfg), "s", "k", "new")
    assert yaml_utils.read_setting(str(cfg), "s", "k") == "new"


def test_write_setting_preserves_other_sections(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    yaml_utils.write_setting(str(cfg), "a", "x", 1)
    yaml_utils.write_setting(str(cfg), "b", "y", 2)
    assert yaml_utils.read_setting(str(cfg), "a", "x") == 1
    assert yaml_utils.read_setting(str(cfg), "b", "y") == 2


def test_write_setting_type_preservation(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    yaml_utils.write_setting(str(cfg), "s", "bool_val", True)
    yaml_utils.write_setting(str(cfg), "s", "int_val", 42)
    yaml_utils.write_setting(str(cfg), "s", "str_val", "hello")
    assert yaml_utils.read_setting(str(cfg), "s", "bool_val") is True
    assert yaml_utils.read_setting(str(cfg), "s", "int_val") == 42
    assert yaml_utils.read_setting(str(cfg), "s", "str_val") == "hello"


def test_write_setting_creates_section_in_existing_file(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(yaml.safe_dump({"existing": {"k": "v"}}))
    yaml_utils.write_setting(str(cfg), "new_section", "key", "value")
    assert yaml_utils.read_setting(str(cfg), "new_section", "key") == "value"
    assert yaml_utils.read_setting(str(cfg), "existing", "k") == "v"


def test_read_site_url_from_config(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    yaml_utils.write_setting(str(cfg), "galadriel", "site_url", "https://my-instance.com")
    result = yaml_utils.read_setting(str(cfg), "galadriel", "site_url")
    assert result == "https://my-instance.com"


def test_read_site_url_fallback_when_missing(tmp_path):
    cfg = tmp_path / "cfg.yaml"
    yaml_utils.write_setting(str(cfg), "galadriel", "first_run", 0)
    result = yaml_utils.read_setting(str(cfg), "galadriel", "site_url") or "http://localhost:3000"
    assert result == "http://localhost:3000"


def test_read_site_url_fallback_when_no_file(tmp_path):
    result = yaml_utils.read_setting(str(tmp_path / "nope.yaml"), "galadriel", "site_url") or "http://localhost:3000"
    assert result == "http://localhost:3000"
