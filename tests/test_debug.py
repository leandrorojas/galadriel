import importlib.util
from pathlib import Path


def _load_debug_module():
    module_path = Path(__file__).resolve().parents[1] / "galadriel" / "utils" / "debug.py"
    spec = importlib.util.spec_from_file_location("debug", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_logging_remains_enabled_until_final(capsys):
    debug = _load_debug_module()
    debug.set_log(True)
    debug.set_module("TEST")
    debug.log("first")
    debug.log("second")
    out = capsys.readouterr().out.splitlines()
    assert out == ["[TEST] first", "[TEST] second"]

    debug.log("third", True)
    out = capsys.readouterr().out.splitlines()
    assert out == ["[TEST] third"]

    debug.log("fourth")
    out = capsys.readouterr().out.splitlines()
    assert out == []
