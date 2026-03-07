"""Tests for galadriel.case.state — CaseState business logic."""

import pytest
from unittest.mock import PropertyMock
from sqlmodel import select

from galadriel.case.state import CaseState
from galadriel.case.model import CaseModel, StepModel, PrerequisiteModel
from conftest import init_state

pytestmark = pytest.mark.integration


def _make_state(case_id_value=0):
    state = init_state(
        CaseState,
        cases=[], case=None, steps=[], prerequisites=[],
        search_value="", show_search=False,
    )
    type(state).case_id = PropertyMock(return_value=case_id_value)
    return state


class TestAddCase:
    def test_add_case_success(self, patch_rx_session):
        state = _make_state()
        result = state.add_case({"name": "New Case"})
        assert result == 0
        assert state.case is not None
        assert state.case.name == "New Case"

    def test_add_case_empty_name_returns_none(self, patch_rx_session):
        state = _make_state()
        result = state.add_case({"name": ""})
        assert result is None

    def test_add_case_persisted(self, patch_rx_session):
        state = _make_state()
        state.add_case({"name": "Persisted"})
        session = patch_rx_session
        cases = session.exec(select(CaseModel)).all()
        assert len(cases) == 1
        assert cases[0].name == "Persisted"


class TestSaveCaseEdits:
    def test_edit_case(self, patch_rx_session, make_case):
        case = make_case(name="Original")
        state = _make_state(case_id_value=case.id)
        result = state.save_case_edits(case.id, {"name": "Updated"})
        assert result == 0
        assert state.case.name == "Updated"

    def test_edit_empty_name_returns_none(self, patch_rx_session, make_case):
        case = make_case(name="Original")
        state = _make_state(case_id_value=case.id)
        result = state.save_case_edits(case.id, {"name": ""})
        assert result is None

    def test_edit_nonexistent_case(self, patch_rx_session):
        state = _make_state()
        result = state.save_case_edits(9999, {"name": "Nope"})
        assert result is None


class TestSteps:
    def test_add_step(self, patch_rx_session, make_case):
        case = make_case(name="C")
        state = _make_state(case_id_value=case.id)
        state.add_step(case.id, {"action": "Click button", "expected": "Page loads"})
        session = patch_rx_session
        steps = session.exec(select(StepModel).where(StepModel.case_id == case.id)).all()
        assert len(steps) == 1
        assert steps[0].order == 1

    def test_add_second_step_increments_order(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        make_step(case_id=case.id, order=1)
        state = _make_state(case_id_value=case.id)
        state.steps = [StepModel(case_id=case.id, order=1, action="a", expected="e")]
        state.add_step(case.id, {"action": "Second", "expected": "result"})
        session = patch_rx_session
        steps = session.exec(select(StepModel).where(StepModel.case_id == case.id).order_by(StepModel.order)).all()
        assert len(steps) == 2
        assert steps[1].order == 2

    def test_add_step_empty_action_rejected(self, patch_rx_session, make_case):
        case = make_case(name="C")
        state = _make_state(case_id_value=case.id)
        result = state.add_step(case.id, {"action": "", "expected": "e"})
        assert result is not None

    def test_delete_step_reorders(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s1 = make_step(case_id=case.id, order=1, action="first")
        make_step(case_id=case.id, order=2, action="second")
        make_step(case_id=case.id, order=3, action="third")

        state = _make_state(case_id_value=case.id)
        state.delete_step(s1.id)

        session = patch_rx_session
        remaining = session.exec(select(StepModel).where(StepModel.case_id == case.id).order_by(StepModel.order)).all()
        assert len(remaining) == 2
        assert remaining[0].order == 1
        assert remaining[1].order == 2

    def test_cannot_delete_last_step(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s = make_step(case_id=case.id, order=1)
        state = _make_state(case_id_value=case.id)
        state.delete_step(s.id)
        session = patch_rx_session
        steps = session.exec(select(StepModel).where(StepModel.case_id == case.id)).all()
        assert len(steps) == 1

    def test_move_step_up(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s1 = make_step(case_id=case.id, order=1, action="first")
        s2 = make_step(case_id=case.id, order=2, action="second")

        state = _make_state(case_id_value=case.id)
        state.move_step_up(s2.id)

        session = patch_rx_session
        session.expire_all()
        updated_s1 = session.exec(select(StepModel).where(StepModel.id == s1.id)).first()
        updated_s2 = session.exec(select(StepModel).where(StepModel.id == s2.id)).first()
        assert updated_s2.order == 1
        assert updated_s1.order == 2

    def test_move_step_down(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s1 = make_step(case_id=case.id, order=1, action="first")
        s2 = make_step(case_id=case.id, order=2, action="second")

        state = _make_state(case_id_value=case.id)
        state.move_step_down(s1.id)

        session = patch_rx_session
        session.expire_all()
        updated_s1 = session.exec(select(StepModel).where(StepModel.id == s1.id)).first()
        updated_s2 = session.exec(select(StepModel).where(StepModel.id == s2.id)).first()
        assert updated_s1.order == 2
        assert updated_s2.order == 1


class TestPrerequisites:
    def test_add_prerequisite(self, patch_rx_session, make_case, make_step):
        case_a = make_case(name="Case A")
        case_b = make_case(name="Case B")
        make_step(case_id=case_b.id, order=1)

        state = _make_state(case_id_value=case_a.id)
        state.prerequisites = []
        state.add_prerequisite(case_b.id)

        session = patch_rx_session
        prereqs = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_a.id)).all()
        assert len(prereqs) == 1
        assert prereqs[0].prerequisite_id == case_b.id

    def test_self_prerequisite_rejected(self, patch_rx_session, make_case):
        case = make_case(name="Self")
        state = _make_state(case_id_value=case.id)
        result = state.add_prerequisite(case.id)
        assert result is not None

    def test_prerequisite_without_steps_rejected(self, patch_rx_session, make_case):
        case_a = make_case(name="A")
        case_b = make_case(name="B (no steps)")

        state = _make_state(case_id_value=case_a.id)
        result = state.add_prerequisite(case_b.id)
        assert result is not None

    def test_duplicate_prerequisite_rejected(self, patch_rx_session, make_case, make_step):
        case_a = make_case(name="A")
        case_b = make_case(name="B")
        make_step(case_id=case_b.id, order=1)

        state = _make_state(case_id_value=case_a.id)
        state.prerequisites = []
        state.add_prerequisite(case_b.id)
        state.load_prerequisites()
        result = state.add_prerequisite(case_b.id)
        assert result is not None

    def test_redundant_prerequisite_rejected(self, patch_rx_session, make_case, make_step):
        """A→B where B already has prerequisite A should be rejected as redundant."""
        case_a = make_case(name="A")
        case_b = make_case(name="B")
        make_step(case_id=case_a.id, order=1)
        make_step(case_id=case_b.id, order=1)

        # B depends on A
        state_b = _make_state(case_id_value=case_b.id)
        state_b.prerequisites = []
        state_b.add_prerequisite(case_a.id)

        # Now try to make A depend on B — should be rejected (circular: A→B→A)
        state_a = _make_state(case_id_value=case_a.id)
        state_a.prerequisites = []
        state_a.add_prerequisite(case_b.id)

        session = patch_rx_session
        prereqs_a = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_a.id)).all()
        assert len(prereqs_a) == 0

    def test_deep_redundant_prerequisite_rejected(self, patch_rx_session, make_case, make_step):
        """A→C where C→B→A should be rejected (transitive circular)."""
        case_a = make_case(name="A")
        case_b = make_case(name="B")
        case_c = make_case(name="C")
        make_step(case_id=case_a.id, order=1)
        make_step(case_id=case_b.id, order=1)
        make_step(case_id=case_c.id, order=1)

        # B depends on A
        state_b = _make_state(case_id_value=case_b.id)
        state_b.prerequisites = []
        state_b.add_prerequisite(case_a.id)

        # C depends on B
        state_c = _make_state(case_id_value=case_c.id)
        state_c.prerequisites = []
        state_c.add_prerequisite(case_b.id)

        # Now try to make A depend on C — should be rejected (circular: A→C→B→A)
        state_a = _make_state(case_id_value=case_a.id)
        state_a.prerequisites = []
        state_a.add_prerequisite(case_c.id)

        session = patch_rx_session
        prereqs_a = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_a.id)).all()
        assert len(prereqs_a) == 0

    def test_non_redundant_prerequisite_allowed(self, patch_rx_session, make_case, make_step):
        """A→C where C→B (no cycle) should be allowed."""
        case_a = make_case(name="A")
        case_b = make_case(name="B")
        case_c = make_case(name="C")
        make_step(case_id=case_b.id, order=1)
        make_step(case_id=case_c.id, order=1)

        # C depends on B
        state_c = _make_state(case_id_value=case_c.id)
        state_c.prerequisites = []
        state_c.add_prerequisite(case_b.id)

        # A depends on C — should be allowed (no cycle back to A)
        state_a = _make_state(case_id_value=case_a.id)
        state_a.prerequisites = []
        state_a.add_prerequisite(case_c.id)

        session = patch_rx_session
        prereqs = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_a.id)).all()
        assert len(prereqs) == 1
        assert prereqs[0].prerequisite_id == case_c.id

    def test_delete_prerequisite_reorders(self, patch_rx_session, make_case, make_step):
        case_a = make_case(name="A")
        case_b = make_case(name="B")
        case_c = make_case(name="C")
        make_step(case_id=case_b.id, order=1)
        make_step(case_id=case_c.id, order=1)

        state = _make_state(case_id_value=case_a.id)
        state.prerequisites = []
        state.add_prerequisite(case_b.id)
        state.load_prerequisites()
        state.add_prerequisite(case_c.id)
        state.load_prerequisites()

        session = patch_rx_session
        prereqs = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_a.id).order_by(PrerequisiteModel.order)).all()
        first_id = prereqs[0].id
        state.delete_prerequisite(first_id)

        remaining = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_a.id).order_by(PrerequisiteModel.order)).all()
        assert len(remaining) == 1
        assert remaining[0].order == 1
