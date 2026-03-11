"""Tests for all Galadriel model classes."""

import pytest
from datetime import datetime, timezone

from galadriel.case.model import CaseModel, StepModel, PrerequisiteModel
from galadriel.scenario.model import ScenarioModel, ScenarioCaseModel
from galadriel.suite.model import SuiteModel, SuiteChildModel, SuiteChildTypeModel
from galadriel.cycle.model import CycleModel, CycleChildModel, CycleChildTypeModel, CycleStatusModel
from galadriel.iteration.model import (
    IterationModel, IterationStatusModel,
    IterationSnapshotModel, IterationSnapshotStatusModel,
    IterationSnapshotLinkedIssues,
)
from galadriel.user.model import GaladrielUser, GaladrielUserRole, GaladrielUserDisplay
from galadriel.config.model import ConfigModel

pytestmark = pytest.mark.integration

NOW = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# Parametrized: models that can be inserted and serialized
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("model_cls,kwargs", [
    (CaseModel, {"name": "Login test"}),
    (StepModel, {"case_id": 1, "order": 1, "action": "click", "expected": "page loads"}),
    (PrerequisiteModel, {"case_id": 1, "prerequisite_id": 2, "order": 1, "prerequisite_name": "Setup"}),
    (ScenarioModel, {"name": "Checkout flow"}),
    (ScenarioCaseModel, {"scenario_id": 1, "case_id": 1, "order": 1, "case_name": "c"}),
    (SuiteModel, {"name": "Regression"}),
    (SuiteChildTypeModel, {"type_name": "scenario"}),
    (SuiteChildModel, {"suite_id": 1, "child_type_id": 1, "child_id": 1, "order": 1, "child_name": "n", "child_type_name": "t"}),
    (CycleModel, {"name": "Sprint 1", "threshold": "80"}),
    (CycleChildTypeModel, {"type_name": "case"}),
    (CycleStatusModel, {"status_name": "passed"}),
    (CycleChildModel, {"cycle_id": 1, "child_type_id": 1, "child_id": 1, "order": 1}),
    (IterationStatusModel, {"name": "in progress"}),
    (IterationModel, {"cycle_id": 1, "iteration_status_id": 0, "iteration_number": 1}),
    (IterationSnapshotStatusModel, {"status_name": "to do"}),
    (IterationSnapshotModel, {"iteration_id": 1, "order": 1, "child_type": 4}),
    (IterationSnapshotLinkedIssues, {"iteration_snapshot_id": 1, "issue_key": "PROJ-1"}),
    (GaladrielUserRole, {"name": "admin", "description": "Admin role"}),
    (ConfigModel, {"name": "first_run", "value": "1"}),
])
def test_model_insert_and_retrieve(db_session, model_cls, kwargs):
    """Every model can be inserted, committed, and retrieved."""
    obj = model_cls(**kwargs)
    db_session.add(obj)
    db_session.commit()
    db_session.refresh(obj)
    assert obj.id is not None
    for field, value in kwargs.items():
        assert getattr(obj, field) == value


@pytest.mark.parametrize("model_cls,kwargs", [
    (CaseModel, {"name": "c"}),
    (StepModel, {"case_id": 1, "order": 1, "action": "a", "expected": "e"}),
    (PrerequisiteModel, {"case_id": 1, "prerequisite_id": 2, "order": 1, "prerequisite_name": "p"}),
    (ScenarioModel, {"name": "s"}),
    (ScenarioCaseModel, {"scenario_id": 1, "case_id": 1, "order": 1, "case_name": "c"}),
    (SuiteModel, {"name": "s"}),
    (SuiteChildTypeModel, {"type_name": "t"}),
    (SuiteChildModel, {"suite_id": 1, "child_type_id": 1, "child_id": 1, "order": 1, "child_name": "n", "child_type_name": "t"}),
    (CycleModel, {"name": "c", "threshold": "80"}),
    (CycleChildTypeModel, {"type_name": "t"}),
    (CycleStatusModel, {"status_name": "s"}),
    (CycleChildModel, {"cycle_id": 1, "child_type_id": 1, "child_id": 1, "order": 1}),
    (IterationStatusModel, {"name": "n"}),
    (IterationModel, {"cycle_id": 1, "iteration_status_id": 0, "iteration_number": 1}),
    (IterationSnapshotStatusModel, {"status_name": "s"}),
    (IterationSnapshotLinkedIssues, {"iteration_snapshot_id": 1, "issue_key": "K"}),
    (GaladrielUserRole, {"name": "r"}),
    (ConfigModel, {"name": "n", "value": "v"}),
])
def test_model_dict_has_created(db_session, model_cls, kwargs):
    """dict() serialization includes a formatted 'created' field."""
    obj = model_cls(**kwargs)
    db_session.add(obj)
    db_session.commit()
    db_session.refresh(obj)
    d = obj.model_dump()
    assert "created" in d
    assert isinstance(d["created"], str)
    # Should be ISO-formatted with space separator
    assert " " in d["created"]


# ---------------------------------------------------------------------------
# Special cases
# ---------------------------------------------------------------------------

class TestIterationSnapshotModelDict:
    def test_updated_default_serialized_as_string(self, db_session):
        obj = IterationSnapshotModel(
            iteration_id=1, order=1, child_type=4,
        )
        db_session.add(obj)
        db_session.commit()
        db_session.refresh(obj)
        d = obj.model_dump()
        assert "updated" in d
        assert isinstance(d["updated"], str)

    def test_updated_present_serialized_as_string(self, db_session):
        obj = IterationSnapshotModel(
            iteration_id=1, order=1, child_type=4,
            updated=datetime(2024, 3, 1, 10, 0, 0, tzinfo=timezone.utc),
        )
        db_session.add(obj)
        db_session.commit()
        db_session.refresh(obj)
        d = obj.model_dump()
        assert d["updated"] is not None
        assert isinstance(d["updated"], str)


class TestCaseModelDict:
    def test_created_is_iso_format(self, db_session):
        case = CaseModel(name="test")
        db_session.add(case)
        db_session.commit()
        db_session.refresh(case)
        d = case.model_dump()
        # Should not have microseconds
        assert "." not in d["created"]

    def test_deleted_defaults_to_none(self, db_session):
        case = CaseModel(name="test")
        db_session.add(case)
        db_session.commit()
        db_session.refresh(case)
        assert case.deleted is None


class TestGaladrielUserDict:
    def test_serializes_both_timestamps(self, db_session):
        user = GaladrielUser(email="test@test.com", user_id=1, user_role=0)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        d = user.model_dump()
        assert "created" in d
        assert "updated" in d
        assert isinstance(d["created"], str)
        assert isinstance(d["updated"], str)


class TestGaladrielUserDisplay:
    def test_instantiation_without_db(self):
        display = GaladrielUserDisplay(
            local_user_id=1,
            galadriel_user_id=1,
            username="admin",
            email="a@b.com",
            role="admin",
            enabled=True,
            created=NOW,
            updated=NOW,
        )
        assert display.username == "admin"
        assert display.enabled is True
