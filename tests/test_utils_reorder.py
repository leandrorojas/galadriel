"""Tests for galadriel.utils.mixins — reorder helper functions."""

import pytest
from sqlmodel import select

from galadriel.case.model import StepModel
from galadriel.utils.mixins import reorder_move_up, reorder_move_down, reorder_delete

pytestmark = pytest.mark.integration


class TestReorderMoveUp:
    def test_swaps_with_neighbor_above(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s1 = make_step(case_id=case.id, order=1, action="first")
        s2 = make_step(case_id=case.id, order=2, action="second")

        result = reorder_move_up(StepModel, s2.id, "case_id", case.id, "step")

        session = patch_rx_session
        session.expire_all()
        assert session.exec(select(StepModel).where(StepModel.id == s2.id)).first().order == 1
        assert session.exec(select(StepModel).where(StepModel.id == s1.id)).first().order == 2
        assert result is None

    def test_returns_toast_at_min_boundary(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s1 = make_step(case_id=case.id, order=1, action="first")

        result = reorder_move_up(StepModel, s1.id, "case_id", case.id, "step")

        assert result is not None

    def test_nonexistent_item_returns_error(self, patch_rx_session):
        result = reorder_move_up(StepModel, 9999, "case_id", 1, "step")
        assert result is not None

    def test_does_not_affect_other_parents(self, patch_rx_session, make_case, make_step):
        case_a = make_case(name="A")
        case_b = make_case(name="B")
        make_step(case_id=case_a.id, order=1, action="a1")
        sa2 = make_step(case_id=case_a.id, order=2, action="a2")
        sb1 = make_step(case_id=case_b.id, order=1, action="b1")

        reorder_move_up(StepModel, sa2.id, "case_id", case_a.id, "step")

        session = patch_rx_session
        session.expire_all()
        assert session.exec(select(StepModel).where(StepModel.id == sb1.id)).first().order == 1


class TestReorderMoveDown:
    def test_swaps_with_neighbor_below(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s1 = make_step(case_id=case.id, order=1, action="first")
        s2 = make_step(case_id=case.id, order=2, action="second")

        result = reorder_move_down(StepModel, s1.id, "case_id", case.id, "step")

        session = patch_rx_session
        session.expire_all()
        assert session.exec(select(StepModel).where(StepModel.id == s1.id)).first().order == 2
        assert session.exec(select(StepModel).where(StepModel.id == s2.id)).first().order == 1
        assert result is None

    def test_returns_toast_at_max_boundary(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        make_step(case_id=case.id, order=1, action="first")
        s2 = make_step(case_id=case.id, order=2, action="second")

        result = reorder_move_down(StepModel, s2.id, "case_id", case.id, "step")

        assert result is not None

    def test_nonexistent_item_returns_error(self, patch_rx_session):
        result = reorder_move_down(StepModel, 9999, "case_id", 1, "step")
        assert result is not None

    def test_three_items_middle_down(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s1 = make_step(case_id=case.id, order=1, action="first")
        s2 = make_step(case_id=case.id, order=2, action="second")
        s3 = make_step(case_id=case.id, order=3, action="third")

        reorder_move_down(StepModel, s2.id, "case_id", case.id, "step")

        session = patch_rx_session
        session.expire_all()
        assert session.exec(select(StepModel).where(StepModel.id == s1.id)).first().order == 1
        assert session.exec(select(StepModel).where(StepModel.id == s2.id)).first().order == 3
        assert session.exec(select(StepModel).where(StepModel.id == s3.id)).first().order == 2


class TestReorderDelete:
    def test_deletes_and_reorders(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s1 = make_step(case_id=case.id, order=1, action="first")
        make_step(case_id=case.id, order=2, action="second")
        make_step(case_id=case.id, order=3, action="third")

        result = reorder_delete(StepModel, s1.id, "case_id", case.id, "step")

        session = patch_rx_session
        remaining = session.exec(
            select(StepModel).where(StepModel.case_id == case.id).order_by(StepModel.order)
        ).all()
        assert len(remaining) == 2
        assert remaining[0].order == 1
        assert remaining[1].order == 2
        assert result is not None  # returns info toast

    def test_delete_middle_reorders(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        make_step(case_id=case.id, order=1, action="first")
        s2 = make_step(case_id=case.id, order=2, action="second")
        make_step(case_id=case.id, order=3, action="third")

        reorder_delete(StepModel, s2.id, "case_id", case.id, "step")

        session = patch_rx_session
        remaining = session.exec(
            select(StepModel).where(StepModel.case_id == case.id).order_by(StepModel.order)
        ).all()
        assert len(remaining) == 2
        assert remaining[0].order == 1
        assert remaining[0].action == "first"
        assert remaining[1].order == 2
        assert remaining[1].action == "third"

    def test_min_count_prevents_deletion(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s1 = make_step(case_id=case.id, order=1, action="only")

        result = reorder_delete(StepModel, s1.id, "case_id", case.id, "step", min_count=1)

        session = patch_rx_session
        steps = session.exec(select(StepModel).where(StepModel.case_id == case.id)).all()
        assert len(steps) == 1
        assert result is not None  # returns error toast

    def test_nonexistent_item_returns_error(self, patch_rx_session):
        result = reorder_delete(StepModel, 9999, "case_id", 1, "step")
        assert result is not None  # returns error toast

    def test_delete_last_item_no_min_count(self, patch_rx_session, make_case, make_step):
        case = make_case(name="C")
        s1 = make_step(case_id=case.id, order=1, action="only")

        reorder_delete(StepModel, s1.id, "case_id", case.id, "step", min_count=0)

        session = patch_rx_session
        steps = session.exec(select(StepModel).where(StepModel.case_id == case.id)).all()
        assert len(steps) == 0
