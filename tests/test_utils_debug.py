"""Tests for galadriel.utils.debug."""

import pytest
from galadriel.utils import debug

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def reset_debug_state():
    """Reset global debug state before every test."""
    debug.enabled = False
    debug.global_module = ""
    yield
    debug.enabled = False
    debug.global_module = ""


class TestSetLog:
    def test_enable(self):
        debug.set_log(True)
        assert debug.enabled is True

    def test_disable(self):
        debug.set_log(True)
        debug.set_log(False)
        assert debug.enabled is False


class TestSetModule:
    def test_sets_module(self):
        debug.set_module("MY_MOD")
        assert debug.global_module == "MY_MOD"


class TestLog:
    def test_prints_when_enabled(self, capsys):
        debug.set_log(True)
        debug.set_module("TEST")
        debug.log("hello")
        captured = capsys.readouterr()
        assert "[TEST] hello" in captured.out

    def test_silent_when_disabled(self, capsys):
        debug.set_log(False)
        debug.log("should not print")
        captured = capsys.readouterr()
        assert captured.out == ""

    def test_default_module_label(self, capsys):
        debug.set_log(True)
        debug.global_module = ""
        debug.log("msg")
        captured = capsys.readouterr()
        assert "[DEBUG] msg" in captured.out

    def test_final_log_disables(self, capsys):
        debug.set_log(True)
        debug.set_module("X")
        debug.log("last", True)
        assert debug.enabled is False
        assert debug.global_module == ""
        captured = capsys.readouterr()
        assert "[X] last" in captured.out
