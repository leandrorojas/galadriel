"""Tests for galadriel.install.seed."""

import pytest
from sqlmodel import select

from galadriel.config.model import ConfigModel
from galadriel.cycle.model import CycleChildTypeModel, CycleStatusModel
from galadriel.iteration.model import IterationStatusModel, IterationSnapshotStatusModel
from galadriel.suite.model import SuiteChildTypeModel
from galadriel.user.model import GaladrielUserRole
from galadriel.install import seed

pytestmark = pytest.mark.integration


class TestIsFirstRun:
    def test_true_when_no_config(self, patch_rx_session):
        assert seed.is_first_run() is True

    def test_false_after_set(self, patch_rx_session):
        seed.set_first_run()
        assert seed.is_first_run() is False


class TestSetFirstRun:
    def test_inserts_config_row(self, patch_rx_session):
        session = patch_rx_session
        seed.set_first_run()
        result = session.exec(select(ConfigModel).where(ConfigModel.name == "first_run")).one_or_none()
        assert result is not None
        assert result.value == "1"
