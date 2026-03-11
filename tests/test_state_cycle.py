"""Tests for galadriel.cycle.state — CycleState business logic."""

import pytest
from unittest.mock import PropertyMock
from sqlmodel import select

from galadriel.cycle.state import CycleState, format_iteration_status
from galadriel.cycle.model import CycleModel, CycleChildModel
from galadriel.case.model import CaseModel, StepModel
from galadriel.scenario.model import ScenarioModel, ScenarioCaseModel
from galadriel.suite.model import SuiteModel, SuiteChildModel
from galadriel.iteration.model import IterationModel, IterationStatusModel, IterationSnapshotModel
from galadriel.utils import consts
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

    def test_empty_name_returns_none(self, patch_rx_session):
        state = _make_state()
        result = state.add_cycle({"name": "", "threshold": "80"})
        assert result is None

    def test_empty_threshold_returns_none(self, patch_rx_session):
        state = _make_state()
        result = state.add_cycle({"name": "C", "threshold": ""})
        assert result is None


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
        assert result is None

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
        child = CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=case.id, order=1)
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
        result = state.get_max_child_order(99, consts.CHILD_TYPE_CASE)
        assert result == 1

    def test_get_max_child_order_duplicate_returns_neg1(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        session.add(CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=5, order=1))
        session.commit()
        state = _make_state(cycle_id_value=str(cycle.id))
        result = state.get_max_child_order(5, consts.CHILD_TYPE_CASE)
        assert result is None

    def test_get_max_child_order_increments(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        session.add(CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=1, order=1))
        session.add(CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=2, order=2))
        session.commit()
        state = _make_state(cycle_id_value=str(cycle.id))
        result = state.get_max_child_order(3, consts.CHILD_TYPE_CASE)
        assert result == 3

    def test_unlink_child_reorders(self, patch_rx_session, make_cycle):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        c1 = CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=1, order=1)
        c2 = CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=2, order=2)
        c3 = CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=3, order=3)
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
        c1 = CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=1, order=1)
        c2 = CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=2, order=2)
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
        c1 = CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=1, order=1)
        c2 = CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=2, order=2)
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

    def test_not_started_iteration_returns_true(self, patch_rx_session, make_cycle, seeded_db):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        iteration = IterationModel(cycle_id=cycle.id, iteration_status_id=consts.ITERATION_STATUS_NOT_STARTED, iteration_number=1)
        session.add(iteration)
        session.commit()

        state = _make_state(cycle_id_value=str(cycle.id))
        assert state.can_edit_iteration(cycle.id) is True

    def test_on_hold_iteration_returns_true(self, patch_rx_session, make_cycle, seeded_db):
        cycle = make_cycle(name="C")
        session = patch_rx_session
        iteration = IterationModel(cycle_id=cycle.id, iteration_status_id=consts.ITERATION_STATUS_ON_HOLD, iteration_number=1)
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
                iteration_id=iteration.id, order=i, child_type=consts.CHILD_TYPE_STEP, child_status_id=consts.SNAPSHOT_STATUS_PASS
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
            iteration_id=iteration.id, order=0, child_type=consts.CHILD_TYPE_STEP, child_status_id=consts.SNAPSHOT_STATUS_PASS
        ))
        session.add(IterationSnapshotModel(
            iteration_id=iteration.id, order=1, child_type=consts.CHILD_TYPE_STEP, child_status_id=consts.SNAPSHOT_STATUS_FAILED
        ))
        session.commit()

        state = _make_state(cycle_id_value=str(cycle.id))
        assert state.can_edit_iteration(cycle.id) is True


class TestLinkCase:
    def test_link_case_success(self, patch_rx_session, make_cycle, make_case, make_step):
        cycle = make_cycle(name="C")
        case = make_case(name="TC")
        make_step(case_id=case.id, order=1)

        state = _make_state(cycle_id_value=str(cycle.id))
        state.cases_for_search = [case]
        state.link_case(case.id)

        session = patch_rx_session
        children = session.exec(select(CycleChildModel).where(CycleChildModel.cycle_id == cycle.id)).all()
        assert len(children) == 1
        assert children[0].child_id == case.id
        assert children[0].child_type_id == consts.CHILD_TYPE_CASE

    def test_link_case_without_steps_rejected(self, patch_rx_session, make_cycle, make_case):
        cycle = make_cycle(name="C")
        case = make_case(name="No Steps")

        state = _make_state(cycle_id_value=str(cycle.id))
        state.link_case(case.id)

        session = patch_rx_session
        children = session.exec(select(CycleChildModel).where(CycleChildModel.cycle_id == cycle.id)).all()
        assert len(children) == 0

    def test_link_duplicate_case_rejected(self, patch_rx_session, make_cycle, make_case, make_step):
        cycle = make_cycle(name="C")
        case = make_case(name="TC")
        make_step(case_id=case.id, order=1)

        state = _make_state(cycle_id_value=str(cycle.id))
        state.cases_for_search = [case]
        state.link_case(case.id)
        state.cases_for_search = [case]
        state.link_case(case.id)

        session = patch_rx_session
        children = session.exec(select(CycleChildModel).where(CycleChildModel.cycle_id == cycle.id)).all()
        assert len(children) == 1


class TestLinkScenario:
    def test_link_scenario_success(self, patch_rx_session, make_cycle, make_scenario):
        cycle = make_cycle(name="C")
        scenario = make_scenario(name="S")

        state = _make_state(cycle_id_value=str(cycle.id))
        state.scenarios_for_search = [scenario]
        state.link_scenario(scenario.id)

        session = patch_rx_session
        children = session.exec(select(CycleChildModel).where(CycleChildModel.cycle_id == cycle.id)).all()
        assert len(children) == 1
        assert children[0].child_type_id == consts.CHILD_TYPE_SCENARIO

    def test_link_duplicate_scenario_rejected(self, patch_rx_session, make_cycle, make_scenario):
        cycle = make_cycle(name="C")
        scenario = make_scenario(name="S")

        state = _make_state(cycle_id_value=str(cycle.id))
        state.scenarios_for_search = [scenario]
        state.link_scenario(scenario.id)
        state.scenarios_for_search = [scenario]
        state.link_scenario(scenario.id)

        session = patch_rx_session
        children = session.exec(select(CycleChildModel).where(CycleChildModel.cycle_id == cycle.id)).all()
        assert len(children) == 1


class TestLinkSuite:
    def test_link_suite_success(self, patch_rx_session, make_cycle, make_suite):
        cycle = make_cycle(name="C")
        suite = make_suite(name="Suite")

        state = _make_state(cycle_id_value=str(cycle.id))
        state.suites_for_search = [suite]
        state.link_suite(suite.id)

        session = patch_rx_session
        children = session.exec(select(CycleChildModel).where(CycleChildModel.cycle_id == cycle.id)).all()
        assert len(children) == 1
        assert children[0].child_type_id == consts.CHILD_TYPE_SUITE


def _create_snapshot(session, make_cycle, make_case, make_step, num_steps=1):
    """Helper: create a cycle with one case and N steps, then generate its snapshot."""
    cycle = make_cycle(name="C")
    case = make_case(name="TC")
    for i in range(1, num_steps + 1):
        make_step(case_id=case.id, order=i, action=f"Step {i}", expected=f"E{i}")
    session.add(CycleChildModel(cycle_id=cycle.id, child_type_id=consts.CHILD_TYPE_CASE, child_id=case.id, order=1))
    session.commit()
    state = _make_state(cycle_id_value=str(cycle.id))
    state.add_iteration_snapshot(cycle.id)
    iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == cycle.id)).first()
    return state, iteration


class TestIterationSnapshot:
    def test_add_iteration_snapshot_creates_iteration(self, patch_rx_session, make_cycle, make_case, make_step, seeded_db):
        _, iteration = _create_snapshot(patch_rx_session, make_cycle, make_case, make_step)
        assert iteration is not None
        assert iteration.iteration_status_id == consts.ITERATION_STATUS_NOT_STARTED

    def test_snapshot_contains_case_and_steps(self, patch_rx_session, make_cycle, make_case, make_step, seeded_db):
        _, iteration = _create_snapshot(patch_rx_session, make_cycle, make_case, make_step, num_steps=2)
        snapshots = patch_rx_session.exec(
            select(IterationSnapshotModel).where(IterationSnapshotModel.iteration_id == iteration.id)
            .order_by(IterationSnapshotModel.order)
        ).all()

        # 1 case header + 2 steps
        assert len(snapshots) == 3
        assert snapshots[0].child_type == consts.CHILD_TYPE_CASE
        assert snapshots[0].child_name == "TC"
        assert snapshots[1].child_type == consts.CHILD_TYPE_STEP
        assert snapshots[1].child_status_id == consts.SNAPSHOT_STATUS_TO_DO
        assert snapshots[2].child_type == consts.CHILD_TYPE_STEP

    def test_pass_step_updates_status(self, patch_rx_session, make_cycle, make_case, make_step, seeded_db):
        state, iteration = _create_snapshot(patch_rx_session, make_cycle, make_case, make_step)
        session = patch_rx_session
        step = session.exec(select(IterationSnapshotModel).where(
            IterationSnapshotModel.iteration_id == iteration.id,
            IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP
        )).first()

        state.pass_iteration_snapshot_step(step.id)

        session.expire_all()
        updated = session.exec(select(IterationSnapshotModel).where(IterationSnapshotModel.id == step.id)).first()
        assert updated.child_status_id == consts.SNAPSHOT_STATUS_PASS

    def test_fail_step_blocks_following_steps(self, patch_rx_session, make_cycle, make_case, make_step, seeded_db):
        state, iteration = _create_snapshot(patch_rx_session, make_cycle, make_case, make_step, num_steps=2)
        session = patch_rx_session
        steps = session.exec(select(IterationSnapshotModel).where(
            IterationSnapshotModel.iteration_id == iteration.id,
            IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP
        ).order_by(IterationSnapshotModel.order)).all()

        state.fail_iteration_snapshot_step(steps[0].id)

        session.expire_all()
        failed = session.exec(select(IterationSnapshotModel).where(IterationSnapshotModel.id == steps[0].id)).first()
        blocked = session.exec(select(IterationSnapshotModel).where(IterationSnapshotModel.id == steps[1].id)).first()
        assert failed.child_status_id == consts.SNAPSHOT_STATUS_FAILED
        assert blocked.child_status_id == consts.SNAPSHOT_STATUS_BLOCKED

    def test_skip_step_updates_status(self, patch_rx_session, make_cycle, make_case, make_step, seeded_db):
        state, iteration = _create_snapshot(patch_rx_session, make_cycle, make_case, make_step)
        session = patch_rx_session
        step = session.exec(select(IterationSnapshotModel).where(
            IterationSnapshotModel.iteration_id == iteration.id,
            IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP
        )).first()

        state.skip_iteration_snapshot_step(step.id)

        session.expire_all()
        updated = session.exec(select(IterationSnapshotModel).where(IterationSnapshotModel.id == step.id)).first()
        assert updated.child_status_id == consts.SNAPSHOT_STATUS_SKIPPED

    def test_empty_cycle_no_snapshot(self, patch_rx_session, make_cycle, seeded_db):
        cycle = make_cycle(name="Empty")
        state = _make_state(cycle_id_value=str(cycle.id))
        state.add_iteration_snapshot(cycle.id)

        iterations = patch_rx_session.exec(select(IterationModel).where(IterationModel.cycle_id == cycle.id)).all()
        assert len(iterations) == 0


class TestSearchFilter:
    def test_filter_test_cases(self, patch_rx_session, make_case):
        make_case(name="Login Test")
        make_case(name="Logout Test")
        make_case(name="Signup Flow")

        state = _make_state()
        state.load_cases_for_search("login")
        assert len(state.cases_for_search) == 1
        assert state.cases_for_search[0].name == "Login Test"

    def test_filter_scenarios(self, patch_rx_session, make_scenario):
        make_scenario(name="Checkout Flow")
        make_scenario(name="Login Flow")

        state = _make_state()
        state.load_scenarios_for_search("checkout")
        assert len(state.scenarios_for_search) == 1

    def test_filter_suites(self, patch_rx_session, make_suite):
        make_suite(name="Regression Suite")
        make_suite(name="Smoke Suite")

        state = _make_state()
        state.load_suites_for_search("smoke")
        assert len(state.suites_for_search) == 1


class TestFormatIterationStatus:
    def test_none_status_returns_empty(self):
        assert format_iteration_status(None, can_edit=False) == ""

    def test_regular_status_returns_name(self):
        status = IterationStatusModel(id=consts.ITERATION_STATUS_IN_PROGRESS, name="in progress")
        assert format_iteration_status(status, can_edit=False) == "in progress"

    def test_completed_all_passed_returns_completed(self):
        status = IterationStatusModel(id=consts.ITERATION_STATUS_COMPLETED, name="completed")
        assert format_iteration_status(status, can_edit=False) == "completed"

    def test_completed_with_failures_returns_prefixed(self):
        status = IterationStatusModel(id=consts.ITERATION_STATUS_COMPLETED, name="completed")
        assert format_iteration_status(status, can_edit=True) == "[F] completed"

    def test_closed_status_returns_name(self):
        status = IterationStatusModel(id=consts.ITERATION_STATUS_CLOSED, name="closed")
        assert format_iteration_status(status, can_edit=True) == "closed"
