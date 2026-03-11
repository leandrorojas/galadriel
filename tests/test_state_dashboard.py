"""Tests for galadriel.dashboard.state — DashboardState business logic."""

import pytest
from sqlmodel import select

from galadriel.dashboard.state import DashboardState
from galadriel.iteration.model import IterationModel, IterationSnapshotModel
from galadriel.cycle.model import CycleModel
from galadriel.utils import consts
from conftest import init_state

pytestmark = pytest.mark.integration


def _make_state():
    return init_state(DashboardState, linked_bugs=[], pie_chart_data=[], trend_data=[])


class TestPieChartData:
    def test_empty_data_returns_zeroes(self, patch_rx_session):
        state = _make_state()
        state.load_dashboard()
        assert state.pie_chart_data == []

    def test_with_data(self, patch_rx_session, seeded_db):
        session = patch_rx_session
        cycle = CycleModel(name="C", threshold="80")
        session.add(cycle)
        session.commit()
        session.refresh(cycle)

        iteration = IterationModel(cycle_id=cycle.id, iteration_status_id=1, iteration_number=1)
        session.add(iteration)
        session.commit()
        session.refresh(iteration)

        for status_id in [consts.SNAPSHOT_STATUS_PASS, consts.SNAPSHOT_STATUS_PASS, consts.SNAPSHOT_STATUS_FAILED, consts.SNAPSHOT_STATUS_BLOCKED]:
            session.add(IterationSnapshotModel(
                iteration_id=iteration.id, order=0, child_type=consts.CHILD_TYPE_STEP, child_status_id=status_id
            ))
        session.commit()

        state = _make_state()
        state.load_dashboard()
        names = {d["name"]: d["value"] for d in state.pie_chart_data}
        assert names["Passed"] == pytest.approx(50.0)
        assert names["Failed"] == pytest.approx(25.0)
        assert names["Blocked"] == pytest.approx(25.0)


class TestCaseCountByStatus:
    def test_cycle_count_zero_when_empty(self, patch_rx_session):
        state = _make_state()
        state.load_dashboard()
        assert state.cycle_count == 0

    def test_blocked_cases_count(self, patch_rx_session, seeded_db):
        session = patch_rx_session
        cycle = CycleModel(name="C", threshold="80")
        session.add(cycle)
        session.commit()
        session.refresh(cycle)

        iteration = IterationModel(cycle_id=cycle.id, iteration_status_id=1, iteration_number=1)
        session.add(iteration)
        session.commit()
        session.refresh(iteration)

        session.add(IterationSnapshotModel(
            iteration_id=iteration.id, order=0, child_type=consts.CHILD_TYPE_STEP, child_status_id=consts.SNAPSHOT_STATUS_BLOCKED
        ))
        session.add(IterationSnapshotModel(
            iteration_id=iteration.id, order=1, child_type=consts.CHILD_TYPE_STEP, child_status_id=consts.SNAPSHOT_STATUS_BLOCKED
        ))
        session.commit()

        state = _make_state()
        state.load_dashboard()
        assert state.blocked_cases == 2
