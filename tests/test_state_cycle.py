"""Tests for galadriel.cycle.state — CycleState business logic."""

import pytest
from unittest.mock import PropertyMock
from sqlmodel import select

from galadriel.cycle.state import CycleState
from galadriel.cycle.model import CycleModel, CycleChildModel
from galadriel.iteration.model import IterationModel, IterationSnapshotModel
from conftest import init_state

pytestmark = pytest.mark.integration


def _make_state(cycle_id_value=""):
    state = init_state(
        CycleState,
        cycles=[], cycle=None, children=[], child=None,
        show_case_search=False, search_case_value="", cases_for_search=[],
        show_scenario_search=False, search_scenario_value="", scenarios_for_search=[],
        show_suite_search=False, search_suite_value="", suites_for_search=[],
        iteration_snapshot_items=[],
    )
    object.__setattr__(state, "_CycleState__fail_checkbox", False)
    type(state).cycle_id = PropertyMock(return_value=cycle_id_value)
    return state


class TestAddCycle:
    def test_success(self, patch_rx_session):
        state = _make_state()
        result = state.add_cycle({"name": "Sprint 1", "threshold": "80"})
        assert result == 0
        assert state.cycle is not None
        assert state.cycle.name == "Sprint 1"

    def test_empty_name_returns_name(self, patch_rx_session):
        state = _make_state()
        result = state.add_cycle({"name": "", "threshold": "80"})
        assert result == "name"

    def test_empty_threshold_returns_threshold(self, patch_rx_session):
        state = _make_state()
        result = state.add_cycle({"name": "C", "threshold": ""})
        assert result == "threshold"


class TestSaveCycleEdits:
    def test_edit_success(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="Original")
        state = _make_state(cycle_id_value=str(cycle.id))
        result = state.save_cycle_edits(cycle.id, {"name": "Updated", "threshold": "90"})
        assert result == 0
        assert state.cycle.name == "Updated"

    def test_edit_empty_name(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        state = _make_state(cycle_id_value=str(cycle.id))
        result = state.save_cycle_edits(cycle.id, {"name": "", "threshold": "80"})
        assert result == "name"

    def test_edit_nonexistent(self, patch_rx_session):
        state = _make_state()
        result = state.save_cycle_edits(9999, {"name": "X", "threshold": "80"})
        assert result is None


class TestDuplicateCycle:
    def test_duplicate_creates_copy(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="Original", threshold="75")
        state = _make_state(cycle_id_value=str(cycle.id))
        state.duplicate_cycle(cycle.id)
        session = patch_rx_session
        all_cycles = session.exec(select(CycleModel)).all()
        assert len(all_cycles) == 2
        copy = [c for c in all_cycles if c.id != cycle.id][0]
        assert copy.name == "copy of Original"
        assert copy.threshold == "75"

    def test_duplicate_copies_children(self, patch_rx_session, make_cycle, make_case, make_step):
        cycle = make_cycle(name="C")
        case = make_case(name="TC")
        make_step(case_id=case.id, order=1)
        session = patch_rx_session
        child = CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=case.id, order=1)
        session.add(child)
        session.commit()

        state = _make_state(cycle_id_value=str(cycle.id))
        state.duplicate_cycle(cycle.id)

        new_cycle = [c for c in session.exec(select(CycleModel)).all() if c.id != cycle.id][0]
        children = session.exec(select(CycleChildModel).where(CycleChildModel.cycle_id == new_cycle.id)).all()
        assert len(children) == 1
        assert children[0].child_id == case.id


class TestCycleChildren:
    def test_get_max_child_order_empty(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        state = _make_state(cycle_id_value=str(cycle.id))
        result = state.get_max_child_order(99, 3)
        assert result == 1

    def test_get_max_child_order_duplicate_returns_neg1(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        session.add(CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=5, order=1))
        session.commit()
        state = _make_state(cycle_id_value=str(cycle.id))
        result = state.get_max_child_order(5, 3)
        assert result == -1

    def test_get_max_child_order_increments(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        session.add(CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=1, order=1))
        session.add(CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=2, order=2))
        session.commit()
        state = _make_state(cycle_id_value=str(cycle.id))
        result = state.get_max_child_order(3, 3)
        assert result == 3

    def test_unlink_child_reorders(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        c1 = CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=1, order=1)
        c2 = CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=2, order=2)
        c3 = CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=3, order=3)
        session.add_all([c1, c2, c3])
        session.commit()
        session.refresh(c1)
        session.refresh(c2)
        session.refresh(c3)

        state = _make_state(cycle_id_value=str(cycle.id))
        state.unlink_child(c1.id)

        remaining = session.exec(
            select(CycleChildModel).where(CycleChildModel.cycle_id == cycle.id).order_by(CycleChildModel.order)
        ).all()
        assert len(remaining) == 2
        assert remaining[0].order == 1
        assert remaining[1].order == 2

    def test_move_child_up(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        c1 = CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=1, order=1)
        c2 = CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=2, order=2)
        session.add_all([c1, c2])
        session.commit()
        session.refresh(c1)
        session.refresh(c2)

        state = _make_state(cycle_id_value=str(cycle.id))
        state.move_child_up(c2.id)

        session.expire_all()
        assert session.exec(select(CycleChildModel).where(CycleChildModel.id == c2.id)).first().order == 1
        assert session.exec(select(CycleChildModel).where(CycleChildModel.id == c1.id)).first().order == 2

    def test_move_child_down(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        c1 = CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=1, order=1)
        c2 = CycleChildModel(cycle_id=cycle.id, child_type_id=3, child_id=2, order=2)
        session.add_all([c1, c2])
        session.commit()
        session.refresh(c1)
        session.refresh(c2)

        state = _make_state(cycle_id_value=str(cycle.id))
        state.move_child_down(c1.id)

        session.expire_all()
        assert session.exec(select(CycleChildModel).where(CycleChildModel.id == c1.id)).first().order == 2
        assert session.exec(select(CycleChildModel).where(CycleChildModel.id == c2.id)).first().order == 1


class TestCanEditIteration:
    def test_no_iteration_returns_false(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        state = _make_state(cycle_id_value=str(cycle.id))
        assert state.can_edit_iteration(cycle.id) is False

    def test_closed_iteration_returns_false(self, patch_rx_session, make_cycle, seeded_db):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        iteration = IterationModel(cycle_id=cycle.id, iteration_status_id=3, iteration_number=1)
        session.add(iteration)
        session.commit()

        state = _make_state(cycle_id_value=str(cycle.id))
        assert state.can_edit_iteration(cycle.id) is False

    def test_in_progress_iteration_returns_true(self, patch_rx_session, make_cycle, seeded_db):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        iteration = IterationModel(cycle_id=cycle.id, iteration_status_id=1, iteration_number=1)
        session.add(iteration)
        session.commit()

        state = _make_state(cycle_id_value=str(cycle.id))
        assert state.can_edit_iteration(cycle.id) is True

    def test_completed_all_passed_returns_false(self, patch_rx_session, make_cycle, seeded_db):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        iteration = IterationModel(cycle_id=cycle.id, iteration_status_id=4, iteration_number=1)
        session.add(iteration)
        session.commit()
        session.refresh(iteration)

        for i in range(3):
            session.add(IterationSnapshotModel(
                iteration_id=iteration.id, order=i, child_type=4, child_status_id=3
            ))
        session.commit()

        state = _make_state(cycle_id_value=str(cycle.id))
        assert state.can_edit_iteration(cycle.id) is False

    def test_completed_with_failures_returns_true(self, patch_rx_session, make_cycle, seeded_db):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        iteration = IterationModel(cycle_id=cycle.id, iteration_status_id=4, iteration_number=1)
        session.add(iteration)
        session.commit()
        session.refresh(iteration)

        session.add(IterationSnapshotModel(
            iteration_id=iteration.id, order=0, child_type=4, child_status_id=3
        ))
        session.add(IterationSnapshotModel(
            iteration_id=iteration.id, order=1, child_type=4, child_status_id=2
        ))
        session.commit()

        state = _make_state(cycle_id_value=str(cycle.id))
        assert state.can_edit_iteration(cycle.id) is True
