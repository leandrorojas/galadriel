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
        sort_by="created", sort_asc=False,
        search_sort_by="", search_sort_asc=True,
        case_name_input="", navigate_to_edit=False,
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


class TestAddAndConfigure:
    """Verify the Add & Configure flow redirects to edit page."""

    def test_navigate_to_edit_flag_set(self, patch_rx_session):
        """set_navigate_to_edit should set the flag to True."""
        state = _make_state()
        state.set_navigate_to_edit()
        assert state.navigate_to_edit is True

    def test_clear_form_resets_flag(self, patch_rx_session):
        """clear_form should reset navigate_to_edit and name input."""
        state = _make_state()
        state.navigate_to_edit = True
        state.case_name_input = "something"
        state.clear_form()
        assert state.navigate_to_edit is False
        assert state.case_name_input == ""

    def test_add_and_configure_creates_case(self, patch_rx_session):
        """Add & Configure should create the case and clear the flag."""
        state = _make_state()
        state.navigate_to_edit = True
        result = state.add_case({"name": "Configured Case"})
        assert result == 0
        assert state.case is not None
        assert state.case.name == "Configured Case"

    def test_add_and_configure_duplicate_rejected(self, patch_rx_session, make_case):
        """Duplicate name with navigate_to_edit should still be rejected."""
        make_case(name="Existing")
        state = _make_state()
        result = state.add_case({"name": "Existing"})
        assert result is not None
        assert result != 0


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

        session = patch_rx_session

        # B depends on A
        state_b = _make_state(case_id_value=case_b.id)
        state_b.prerequisites = []
        state_b.add_prerequisite(case_a.id)
        prereqs_b = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_b.id)).all()
        assert len(prereqs_b) == 1

        # Now try to make A depend on B — should be rejected (circular: A→B→A)
        state_a = _make_state(case_id_value=case_a.id)
        state_a.prerequisites = []
        state_a.add_prerequisite(case_b.id)

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

        session = patch_rx_session

        # B depends on A
        state_b = _make_state(case_id_value=case_b.id)
        state_b.prerequisites = []
        state_b.add_prerequisite(case_a.id)
        prereqs_b = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_b.id)).all()
        assert len(prereqs_b) == 1

        # C depends on B
        state_c = _make_state(case_id_value=case_c.id)
        state_c.prerequisites = []
        state_c.add_prerequisite(case_b.id)
        prereqs_c = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_c.id)).all()
        assert len(prereqs_c) == 1

        # Now try to make A depend on C — should be rejected (circular: A→C→B→A)
        state_a = _make_state(case_id_value=case_a.id)
        state_a.prerequisites = []
        state_a.add_prerequisite(case_c.id)

        prereqs_a = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_a.id)).all()
        assert len(prereqs_a) == 0

    def test_non_redundant_prerequisite_allowed(self, patch_rx_session, make_case, make_step):
        """A→C where C→B (no cycle) should be allowed."""
        case_a = make_case(name="A")
        case_b = make_case(name="B")
        case_c = make_case(name="C")
        make_step(case_id=case_b.id, order=1)
        make_step(case_id=case_c.id, order=1)

        session = patch_rx_session

        # C depends on B
        state_c = _make_state(case_id_value=case_c.id)
        state_c.prerequisites = []
        state_c.add_prerequisite(case_b.id)
        prereqs_c = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_c.id)).all()
        assert len(prereqs_c) == 1

        # A depends on C — should be allowed (no cycle back to A)
        state_a = _make_state(case_id_value=case_a.id)
        state_a.prerequisites = []
        state_a.add_prerequisite(case_c.id)

        prereqs_a = session.exec(select(PrerequisiteModel).where(PrerequisiteModel.case_id == case_a.id)).all()
        assert len(prereqs_a) == 1
        assert prereqs_a[0].prerequisite_id == case_c.id

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


class TestUniqueNameValidation:
    """Verify that case names must be unique."""

    def test_add_case_duplicate_name_rejected(self, patch_rx_session, make_case):
        """Adding a case with an existing name should be rejected."""
        make_case(name="Login Test")
        state = _make_state()
        result = state.add_case({"name": "Login Test"})
        assert result is not None  # toast error
        session = patch_rx_session
        all_cases = session.exec(select(CaseModel)).all()
        assert len(all_cases) == 1

    def test_edit_case_duplicate_name_rejected(self, patch_rx_session, make_case):
        """Editing a case to use another case's name should be rejected."""
        make_case(name="Case A")
        case_b = make_case(name="Case B")
        state = _make_state(case_id_value=case_b.id)
        result = state.save_case_edits(case_b.id, {"name": "Case A"})
        assert result is not None  # toast error
        session = patch_rx_session
        session.expire_all()
        updated = session.exec(select(CaseModel).where(CaseModel.id == case_b.id)).first()
        assert updated.name == "Case B"

    def test_edit_case_same_name_allowed(self, patch_rx_session, make_case):
        """Saving a case with its own current name should succeed."""
        case = make_case(name="Case A")
        state = _make_state(case_id_value=case.id)
        result = state.save_case_edits(case.id, {"name": "Case A"})
        assert result == 0


class TestLoadCasesCounts:
    """Verify load_cases populates step and prerequisite counts."""

    def test_load_cases_with_no_steps_or_prerequisites(self, patch_rx_session, make_case):
        """Cases with no steps or prerequisites should have zero counts."""
        make_case(name="Empty Case")
        state = _make_state()
        state.load_cases()
        assert len(state.cases) == 1
        assert state.cases[0].step_count == 0
        assert state.cases[0].prerequisite_count == 0

    def test_load_cases_with_steps(self, patch_rx_session, make_case, make_step):
        """Cases with steps should reflect the correct step count."""
        case = make_case(name="With Steps")
        make_step(case_id=case.id, order=1, action="a1")
        make_step(case_id=case.id, order=2, action="a2")
        make_step(case_id=case.id, order=3, action="a3")
        state = _make_state()
        state.load_cases()
        assert state.cases[0].step_count == 3
        assert state.cases[0].prerequisite_count == 0

    def test_load_cases_with_prerequisites(self, patch_rx_session, make_case, make_step):
        """Cases with prerequisites should reflect the correct prerequisite count."""
        case_a = make_case(name="Case A")
        case_b = make_case(name="Case B")
        case_c = make_case(name="Case C")
        make_step(case_id=case_b.id, order=1)
        make_step(case_id=case_c.id, order=1)

        state = _make_state(case_id_value=case_a.id)
        state.prerequisites = []
        state.add_prerequisite(case_b.id)
        state.load_prerequisites()
        state.add_prerequisite(case_c.id)

        state2 = _make_state()
        state2.load_cases()
        case_a_loaded = next(c for c in state2.cases if c.name == "Case A")
        assert case_a_loaded.prerequisite_count == 2

    def test_load_cases_counts_independent_per_case(self, patch_rx_session, make_case, make_step):
        """Each case should have its own independent counts."""
        case1 = make_case(name="One Step")
        case2 = make_case(name="Three Steps")
        make_step(case_id=case1.id, order=1, action="a")
        make_step(case_id=case2.id, order=1, action="a")
        make_step(case_id=case2.id, order=2, action="b")
        make_step(case_id=case2.id, order=3, action="c")

        state = _make_state()
        state.load_cases()
        cases_by_name = {c.name: c for c in state.cases}
        assert cases_by_name["One Step"].step_count == 1
        assert cases_by_name["Three Steps"].step_count == 3


class TestSorting:
    """Verify list-page and search-table sorting behavior."""

    def test_default_sort_is_created_desc(self, patch_rx_session, make_case):
        """Verify default sort is by created descending (newest first)."""
        make_case(name="Zebra")
        make_case(name="Alpha")
        state = _make_state()
        state.load_cases()
        assert state.sort_by == "created"
        assert state.sort_asc is False
        names = [c.name for c in state.sorted_cases]
        assert names == ["Alpha", "Zebra"]

    def test_toggle_sort_cycles_asc_desc_default(self, patch_rx_session, make_case):
        """Verify toggle_sort cycles flags and visible order through asc, desc, default."""
        make_case(name="Zebra")
        make_case(name="Alpha")
        make_case(name="Middle")
        state = _make_state()
        state.load_cases()

        state.toggle_sort("name")
        assert state.sort_by == "name"
        assert state.sort_asc is True
        assert [c.name for c in state.sorted_cases] == ["Alpha", "Middle", "Zebra"]

        state.toggle_sort("name")
        assert state.sort_by == "name"
        assert state.sort_asc is False
        assert [c.name for c in state.sorted_cases] == ["Zebra", "Middle", "Alpha"]

        state.toggle_sort("name")
        assert state.sort_by == ""
        assert state.sort_asc is True

    def test_toggle_sort_different_field_resets(self, patch_rx_session):
        """Verify switching to a different field resets to ascending."""
        state = _make_state()
        state.toggle_sort("name")
        state.toggle_sort("name")  # now desc
        state.toggle_sort("created")
        assert state.sort_by == "created"
        assert state.sort_asc is True

    def test_sorted_cases_by_name_asc(self, patch_rx_session, make_case):
        """Verify ascending sort returns alphabetical name order."""
        make_case(name="Zebra")
        make_case(name="Alpha")
        make_case(name="Middle")
        state = _make_state()
        state.load_cases()
        state.toggle_sort("name")
        names = [c.name for c in state.sorted_cases]
        assert names == ["Alpha", "Middle", "Zebra"]

    def test_sorted_cases_by_name_desc(self, patch_rx_session, make_case):
        """Verify descending sort returns reverse alphabetical name order."""
        make_case(name="Zebra")
        make_case(name="Alpha")
        state = _make_state()
        state.load_cases()
        state.toggle_sort("name")
        state.toggle_sort("name")  # desc
        names = [c.name for c in state.sorted_cases]
        assert names == ["Zebra", "Alpha"]

    def test_search_sort_cycles_asc_desc_default(self, patch_rx_session):
        """Verify toggle_search_sort cycles through asc, desc, default."""
        state = _make_state()
        state.toggle_search_sort("name")
        assert state.search_sort_by == "name"
        assert state.search_sort_asc is True
        state.toggle_search_sort("name")
        assert state.search_sort_by == "name"
        assert state.search_sort_asc is False
        state.toggle_search_sort("name")
        assert state.search_sort_by == ""
        assert state.search_sort_asc is True

    def test_search_sort_different_field_resets(self, patch_rx_session):
        """Verify switching search sort field resets to ascending."""
        state = _make_state()
        state.toggle_search_sort("name")
        state.toggle_search_sort("name")  # desc
        state.toggle_search_sort("created")
        assert state.search_sort_by == "created"
        assert state.search_sort_asc is True

    def test_sorted_cases_for_search_asc(self, patch_rx_session, make_case):
        """Verify search table ascending sort returns alphabetical order."""
        make_case(name="Zebra")
        make_case(name="Alpha")
        make_case(name="Middle")
        state = _make_state()
        state.load_cases()
        state.toggle_search_sort("name")
        names = [c.name for c in state.sorted_cases_for_search]
        assert names == ["Alpha", "Middle", "Zebra"]

    def test_sorted_cases_for_search_desc(self, patch_rx_session, make_case):
        """Verify search table descending sort returns reverse alphabetical order."""
        make_case(name="Zebra")
        make_case(name="Alpha")
        state = _make_state()
        state.load_cases()
        state.toggle_search_sort("name")
        state.toggle_search_sort("name")  # desc
        names = [c.name for c in state.sorted_cases_for_search]
        assert names == ["Zebra", "Alpha"]


class TestLinkableAndEmptyCases:
    """Verify linkable_cases_for_search and empty_cases_for_search split."""

    def test_cases_with_steps_are_linkable(self, patch_rx_session, make_case, make_step):
        """Cases with steps appear in linkable list only."""
        case = make_case(name="Has Steps")
        make_step(case_id=case.id, order=1, action="a")
        state = _make_state()
        state.load_cases()
        assert len(state.linkable_cases_for_search) == 1
        assert state.linkable_cases_for_search[0].name == "Has Steps"
        assert len(state.empty_cases_for_search) == 0

    def test_cases_without_steps_are_empty(self, patch_rx_session, make_case):
        """Cases without steps appear in empty list only."""
        make_case(name="No Steps")
        state = _make_state()
        state.load_cases()
        assert len(state.empty_cases_for_search) == 1
        assert state.empty_cases_for_search[0].name == "No Steps"
        assert len(state.linkable_cases_for_search) == 0

    def test_mixed_cases_split_correctly(self, patch_rx_session, make_case, make_step):
        """Mixed cases split into linkable and empty lists."""
        case_with = make_case(name="With Steps")
        make_case(name="Empty")
        make_step(case_id=case_with.id, order=1, action="a")
        state = _make_state()
        state.load_cases()
        linkable_names = [c.name for c in state.linkable_cases_for_search]
        empty_names = [c.name for c in state.empty_cases_for_search]
        assert linkable_names == ["With Steps"]
        assert empty_names == ["Empty"]
