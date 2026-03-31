"""Tests for galadriel.scenario.state — ScenarioState business logic."""

import asyncio
import pytest
from unittest.mock import PropertyMock, patch
from sqlmodel import select

from galadriel.scenario.state import ScenarioState, AddScenarioState, EditScenarioState
from galadriel.scenario.model import ScenarioModel, ScenarioCaseModel
from conftest import init_state, LinkableEmptyCasesTests

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def mock_audit():
    """Patch async user info lookup and log_action for all scenario tests."""
    async def fake_get_user_info(self):
        return (0, "test")

    with patch.object(ScenarioState, "_get_user_info", fake_get_user_info), \
         patch("galadriel.scenario.state.log_action"):
        yield


def _run(coro):
    """Run an async event handler synchronously."""
    return asyncio.run(coro)


def _make_state(scenario_id_value=""):
    state = init_state(
        ScenarioState,
        scenarios=[], scenario=None,
        test_cases=[], test_cases_for_search=[],
        show_search=False, search_value="",
        sort_by="", sort_asc=True,
        search_sort_by="", search_sort_asc=True,
    )
    type(state).scenario_id = PropertyMock(return_value=scenario_id_value)
    return state


class TestAddScenario:
    def test_success(self, patch_rx_session):
        state = _make_state()
        result = state.add_scenario({"name": "Checkout"})
        assert result == 0
        assert state.scenario.name == "Checkout"

    def test_empty_name(self, patch_rx_session):
        state = _make_state()
        result = state.add_scenario({"name": ""})
        assert result is None


class TestSaveScenarioEdits:
    def test_edit_success(self, patch_rx_session, make_scenario):
        sc = make_scenario(name="Old")
        state = _make_state(scenario_id_value=str(sc.id))
        result = state.save_scenario_edits(sc.id, {"name": "New"})
        assert result == 0
        assert state.scenario.name == "New"

    def test_edit_empty_name(self, patch_rx_session, make_scenario):
        sc = make_scenario(name="S")
        state = _make_state(scenario_id_value=str(sc.id))
        result = state.save_scenario_edits(sc.id, {"name": ""})
        assert result is None


class TestLinkCase:
    def test_requires_steps(self, patch_rx_session, make_scenario, make_case):
        sc = make_scenario(name="S")
        case = make_case(name="No steps")
        state = _make_state(scenario_id_value=str(sc.id))
        result = _run(state.link_case(case.id))
        assert result is not None

    def test_link_success(self, patch_rx_session, make_scenario, make_case, make_step):
        sc = make_scenario(name="S")
        case = make_case(name="C")
        make_step(case_id=case.id, order=1)
        state = _make_state(scenario_id_value=str(sc.id))
        state.test_cases = []
        _run(state.link_case(case.id))
        session = patch_rx_session
        links = session.exec(select(ScenarioCaseModel).where(ScenarioCaseModel.scenario_id == sc.id)).all()
        assert len(links) == 1
        assert links[0].case_id == case.id

    def test_duplicate_case_rejected(self, patch_rx_session, make_scenario, make_case, make_step):
        sc = make_scenario(name="S")
        case = make_case(name="C")
        make_step(case_id=case.id, order=1)

        state = _make_state(scenario_id_value=str(sc.id))
        state.test_cases = []
        _run(state.link_case(case.id))
        state.load_cases()
        result = _run(state.link_case(case.id))
        assert result is not None


class TestUnlinkCase:
    def test_unlink_reorders(self, patch_rx_session, make_scenario):
        sc = make_scenario(name="S")
        session = patch_rx_session
        l1 = ScenarioCaseModel(scenario_id=sc.id, case_id=1, order=1, case_name="a")
        l2 = ScenarioCaseModel(scenario_id=sc.id, case_id=2, order=2, case_name="b")
        l3 = ScenarioCaseModel(scenario_id=sc.id, case_id=3, order=3, case_name="c")
        session.add_all([l1, l2, l3])
        session.commit()
        session.refresh(l1)

        state = _make_state(scenario_id_value=str(sc.id))
        _run(state.unlink_case(l1.id))

        remaining = session.exec(
            select(ScenarioCaseModel).where(ScenarioCaseModel.scenario_id == sc.id).order_by(ScenarioCaseModel.order)
        ).all()
        assert len(remaining) == 2
        assert remaining[0].order == 1
        assert remaining[1].order == 2


class TestMoveCase:
    def test_move_up(self, patch_rx_session, make_scenario):
        sc = make_scenario(name="S")
        session = patch_rx_session
        l1 = ScenarioCaseModel(scenario_id=sc.id, case_id=1, order=1, case_name="a")
        l2 = ScenarioCaseModel(scenario_id=sc.id, case_id=2, order=2, case_name="b")
        session.add_all([l1, l2])
        session.commit()
        session.refresh(l1)
        session.refresh(l2)

        state = _make_state(scenario_id_value=str(sc.id))
        _run(state.move_case_up(l2.id))

        session.expire_all()
        assert session.exec(select(ScenarioCaseModel).where(ScenarioCaseModel.id == l2.id)).first().order == 1
        assert session.exec(select(ScenarioCaseModel).where(ScenarioCaseModel.id == l1.id)).first().order == 2

    def test_move_down(self, patch_rx_session, make_scenario):
        sc = make_scenario(name="S")
        session = patch_rx_session
        l1 = ScenarioCaseModel(scenario_id=sc.id, case_id=1, order=1, case_name="a")
        l2 = ScenarioCaseModel(scenario_id=sc.id, case_id=2, order=2, case_name="b")
        session.add_all([l1, l2])
        session.commit()
        session.refresh(l1)
        session.refresh(l2)

        state = _make_state(scenario_id_value=str(sc.id))
        _run(state.move_case_down(l1.id))

        session.expire_all()
        assert session.exec(select(ScenarioCaseModel).where(ScenarioCaseModel.id == l1.id)).first().order == 2
        assert session.exec(select(ScenarioCaseModel).where(ScenarioCaseModel.id == l2.id)).first().order == 1


class TestLinkableAndEmptyCasesForSearch(LinkableEmptyCasesTests):
    """Verify search results split into linkable and empty cases."""

    def _make_and_load(self, patch_rx_session, make_case, make_step, cases):
        for c in cases:
            case = make_case(name=c["name"])
            for i in range(c.get("steps", 0)):
                make_step(case_id=case.id, order=i + 1, action=f"a{i}")
        state = _make_state()
        state.load_cases_for_search()
        return state


_PARENT_FIELDS = {
    "scenarios": [], "scenario": None,
    "test_cases": [], "test_cases_for_search": [],
    "show_search": False, "search_value": "",
    "sort_by": "", "sort_asc": True,
    "search_sort_by": "", "search_sort_asc": True,
}


def _make_child_state(child_cls, scenario_id_value="", **extra):
    """Create a child state (AddScenarioState/EditScenarioState) with a wired parent."""
    parent = init_state(ScenarioState, **_PARENT_FIELDS)
    state = init_state(child_cls, **extra)
    object.__setattr__(state, "parent_state", parent)
    if scenario_id_value:
        type(state).scenario_id = PropertyMock(return_value=scenario_id_value)
    return state


class TestAddScenarioHandleSubmit:
    """Tests for AddScenarioState.handle_submit with audit logging."""

    def test_creates_scenario_and_logs(self, patch_rx_session):
        """handle_submit should create the scenario and call log_action."""
        state = _make_child_state(AddScenarioState, form_data={})
        with patch("galadriel.scenario.state.log_action") as mock_log:
            _run(state.handle_submit({"name": "New Scenario"}))
            assert state.parent_state.scenario is not None
            assert state.parent_state.scenario.name == "New Scenario"
            mock_log.assert_called_once_with(0, "test", "created", "scenario", "New Scenario")

    def test_empty_name_does_not_log(self, patch_rx_session):
        """handle_submit with empty name should not call log_action."""
        state = _make_child_state(AddScenarioState, form_data={})
        with patch("galadriel.scenario.state.log_action") as mock_log:
            _run(state.handle_submit({"name": ""}))
            mock_log.assert_not_called()


class TestEditScenarioHandleSubmit:
    """Tests for EditScenarioState.handle_submit with audit logging."""

    def test_edits_scenario_and_logs(self, patch_rx_session, make_scenario):
        """handle_submit should save edits and call log_action."""
        sc = make_scenario(name="Old")
        state = _make_child_state(EditScenarioState, scenario_id_value=str(sc.id), form_data={})
        with patch("galadriel.scenario.state.log_action") as mock_log:
            _run(state.handle_submit({"scenario_id": sc.id, "name": "Renamed"}))
            assert state.parent_state.scenario.name == "Renamed"
            mock_log.assert_called_once_with(0, "test", "updated", "scenario", "Renamed")

    def test_empty_name_does_not_log(self, patch_rx_session, make_scenario):
        """handle_submit with empty name should not call log_action."""
        sc = make_scenario(name="S")
        state = _make_child_state(EditScenarioState, scenario_id_value=str(sc.id), form_data={})
        with patch("galadriel.scenario.state.log_action") as mock_log:
            _run(state.handle_submit({"scenario_id": sc.id, "name": ""}))
            mock_log.assert_not_called()
