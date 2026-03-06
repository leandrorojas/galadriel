"""Tests for galadriel.suite.state — SuiteState business logic."""

import pytest
from unittest.mock import PropertyMock
from sqlmodel import select

from galadriel.suite.state import SuiteState
from galadriel.suite.model import SuiteModel, SuiteChildModel
from conftest import init_state

pytestmark = pytest.mark.integration


def _make_state(suite_id_value=""):
    state = init_state(
        SuiteState,
        suites=[], suite=None, children=[], child=None,
        cases_for_search=[], show_case_search=False, search_case_value="",
        scenarios_for_search=[], show_scenario_search=False, search_scenario_value="",
    )
    type(state).suite_id = PropertyMock(return_value=suite_id_value)
    return state


class TestAddSuite:
    def test_success(self, patch_rx_session):
        state = _make_state()
        result = state.add_suite({"name": "Regression"})
        assert result == 0
        assert state.suite.name == "Regression"

    def test_empty_name(self, patch_rx_session):
        state = _make_state()
        result = state.add_suite({"name": ""})
        assert result is None


class TestSaveSuiteEdits:
    def test_edit_success(self, patch_rx_session, make_suite):
        suite = make_suite(name="Old")
        state = _make_state(suite_id_value=str(suite.id))
        result = state.save_suite_edits(suite.id, {"name": "New"})
        assert result == 0
        assert state.suite.name == "New"

    def test_edit_empty_name(self, patch_rx_session, make_suite):
        suite = make_suite(name="S")
        state = _make_state(suite_id_value=str(suite.id))
        result = state.save_suite_edits(suite.id, {"name": ""})
        assert result is None


class TestSuiteChildren:
    def test_link_case_requires_steps(self, patch_rx_session, make_suite, make_case):
        suite = make_suite(name="S")
        case = make_case(name="No Steps")
        state = _make_state(suite_id_value=str(suite.id))
        result = state.link_case(case.id)
        assert result is not None

    def test_link_case_success(self, patch_rx_session, make_suite, make_case, make_step):
        suite = make_suite(name="S")
        case = make_case(name="C")
        make_step(case_id=case.id, order=1)
        state = _make_state(suite_id_value=str(suite.id))
        state.cases_for_search = []
        state.link_case(case.id)
        session = patch_rx_session
        children = session.exec(select(SuiteChildModel).where(SuiteChildModel.suite_id == suite.id)).all()
        assert len(children) == 1
        assert children[0].child_type_id == 2
        assert children[0].child_id == case.id

    def test_link_scenario_success(self, patch_rx_session, make_suite, make_scenario):
        suite = make_suite(name="S")
        scenario = make_scenario(name="SC")
        state = _make_state(suite_id_value=str(suite.id))
        state.scenarios_for_search = []
        state.link_scenario(scenario.id)
        session = patch_rx_session
        children = session.exec(select(SuiteChildModel).where(SuiteChildModel.suite_id == suite.id)).all()
        assert len(children) == 1
        assert children[0].child_type_id == 1

    def test_unlink_child_reorders(self, patch_rx_session, make_suite):
        suite = make_suite(name="S")
        session = patch_rx_session
        c1 = SuiteChildModel(suite_id=suite.id, child_type_id=1, child_id=1, order=1, child_name="a", child_type_name="t")
        c2 = SuiteChildModel(suite_id=suite.id, child_type_id=1, child_id=2, order=2, child_name="b", child_type_name="t")
        c3 = SuiteChildModel(suite_id=suite.id, child_type_id=1, child_id=3, order=3, child_name="c", child_type_name="t")
        session.add_all([c1, c2, c3])
        session.commit()
        session.refresh(c1)

        state = _make_state(suite_id_value=str(suite.id))
        state.unlink_child(c1.id)

        remaining = session.exec(
            select(SuiteChildModel).where(SuiteChildModel.suite_id == suite.id).order_by(SuiteChildModel.order)
        ).all()
        assert len(remaining) == 2
        assert remaining[0].order == 1
        assert remaining[1].order == 2

    def test_move_child_up(self, patch_rx_session, make_suite):
        suite = make_suite(name="S")
        session = patch_rx_session
        c1 = SuiteChildModel(suite_id=suite.id, child_type_id=1, child_id=1, order=1, child_name="a", child_type_name="t")
        c2 = SuiteChildModel(suite_id=suite.id, child_type_id=1, child_id=2, order=2, child_name="b", child_type_name="t")
        session.add_all([c1, c2])
        session.commit()
        session.refresh(c1)
        session.refresh(c2)

        state = _make_state(suite_id_value=str(suite.id))
        state.move_child_up(c2.id)

        session.expire_all()
        assert session.exec(select(SuiteChildModel).where(SuiteChildModel.id == c2.id)).first().order == 1
        assert session.exec(select(SuiteChildModel).where(SuiteChildModel.id == c1.id)).first().order == 2

    def test_move_child_down(self, patch_rx_session, make_suite):
        suite = make_suite(name="S")
        session = patch_rx_session
        c1 = SuiteChildModel(suite_id=suite.id, child_type_id=1, child_id=1, order=1, child_name="a", child_type_name="t")
        c2 = SuiteChildModel(suite_id=suite.id, child_type_id=1, child_id=2, order=2, child_name="b", child_type_name="t")
        session.add_all([c1, c2])
        session.commit()
        session.refresh(c1)
        session.refresh(c2)

        state = _make_state(suite_id_value=str(suite.id))
        state.move_child_down(c1.id)

        session.expire_all()
        assert session.exec(select(SuiteChildModel).where(SuiteChildModel.id == c1.id)).first().order == 2
        assert session.exec(select(SuiteChildModel).where(SuiteChildModel.id == c2.id)).first().order == 1

    def test_get_max_child_order_duplicate(self, patch_rx_session, make_suite):
        suite = make_suite(name="S")
        session = patch_rx_session
        session.add(SuiteChildModel(suite_id=suite.id, child_type_id=1, child_id=5, order=1, child_name="n", child_type_name="t"))
        session.commit()
        state = _make_state(suite_id_value=str(suite.id))
        assert state.get_max_child_order(5, 1) == -1
