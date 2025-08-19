"""Tests for YAML utility helpers."""

from importlib import util
from pathlib import Path
import yaml

# Import the YAML utils module directly to avoid executing package side effects
spec = util.spec_from_file_location(
    "yaml_utils", Path(__file__).resolve().parents[1] / "galadriel" / "utils" / "yaml.py"
)
yaml_utils = util.module_from_spec(spec)
spec.loader.exec_module(yaml_utils)


def test_write_setting_creates_file_and_section(tmp_path):
    cfg_path = tmp_path / "config.yaml"
    # No file exists yet, so reading the setting should return None
    assert yaml_utils.read_setting(str(cfg_path), "galadriel", "first_run") is None

    # After writing, the file and section should be created with the value
    yaml_utils.write_setting(str(cfg_path), "galadriel", "first_run", 1)
    assert yaml_utils.read_setting(str(cfg_path), "galadriel", "first_run") == 1

    with cfg_path.open() as f:
        data = yaml.safe_load(f)
    assert data["galadriel"]["first_run"] == 1
