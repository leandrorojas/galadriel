"""Shared fixtures for the Galadriel test suite."""

# Force reflex.model to resolve before the lazy loader is triggered by
# galadriel's own imports.  Without this, pytest's import machinery can
# hit a metaclass conflict inside reflex/model.py.
import reflex.model  # noqa: F401, E402 — must be first

import pytest
from unittest.mock import patch, MagicMock
from contextlib import contextmanager
from datetime import datetime, timezone

from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import StaticPool

import reflex as rx

from galadriel.case.model import CaseModel, StepModel, PrerequisiteModel
from galadriel.scenario.model import ScenarioModel, ScenarioCaseModel
from galadriel.suite.model import SuiteModel, SuiteChildModel, SuiteChildTypeModel
from galadriel.cycle.model import CycleModel, CycleChildModel, CycleChildTypeModel, CycleStatusModel
from galadriel.iteration.model import (
    IterationModel, IterationStatusModel,
    IterationSnapshotModel, IterationSnapshotStatusModel,
    IterationSnapshotLinkedIssues,
)
from galadriel.user.model import GaladrielUser, GaladrielUserRole
from galadriel.config.model import ConfigModel
from galadriel.audit.model import ActionLogModel


# ---------------------------------------------------------------------------
# Engine & session fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_engine():
    """In-memory SQLite engine with all tables created."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(test_engine):
    """Transactional DB session that rolls back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def patch_rx_session(db_session):
    """Patch ``rx.session()`` so state methods use the test DB session.

    The context manager yields the *same* session every time, so all
    operations within a single test share the same transaction.
    """

    @contextmanager
    def _fake_session():
        yield db_session

    with patch("reflex.session", _fake_session):
        yield db_session


# ---------------------------------------------------------------------------
# Seed / reference-data fixture
# ---------------------------------------------------------------------------

@pytest.fixture()
def seeded_db(patch_rx_session):
    """Insert the minimal reference data that seed.py normally provides."""
    session = patch_rx_session

    # Cycle child types
    for item in [
        {"id": 0, "type_name": "suite"},
        {"id": 1, "type_name": "scenario"},
        {"id": 2, "type_name": "case"},
        {"id": 3, "type_name": "step"},
    ]:
        session.add(CycleChildTypeModel(**item))

    # Cycle statuses
    for item in [
        {"id": 0, "status_name": "passed"},
        {"id": 1, "status_name": "failed"},
    ]:
        session.add(CycleStatusModel(**item))

    # Iteration snapshot statuses
    for item in [
        {"id": 0, "status_name": "to do"},
        {"id": 1, "status_name": "failed"},
        {"id": 2, "status_name": "pass"},
        {"id": 3, "status_name": "skipped"},
        {"id": 4, "status_name": "blocked"},
    ]:
        session.add(IterationSnapshotStatusModel(**item))

    # Iteration statuses
    for item in [
        {"id": 0, "name": "not started"},
        {"id": 1, "name": "in progress"},
        {"id": 2, "name": "on hold"},
        {"id": 3, "name": "closed"},
        {"id": 4, "name": "completed"},
    ]:
        session.add(IterationStatusModel(**item))

    # Suite child types
    for item in [
        {"id": 0, "type_name": "scenario"},
        {"id": 1, "type_name": "case"},
    ]:
        session.add(SuiteChildTypeModel(**item))

    # User roles
    for item in [
        {"id": 0, "name": "admin", "description": "Manages user access"},
        {"id": 1, "name": "viewer", "description": "Can navigate through the galadriel instance"},
        {"id": 2, "name": "editor", "description": "Can perform any task in the galadriel instance, but manage users"},
        {"id": 3, "name": "user manager", "description": "Can manage users but cannot assign or modify the admin role"},
    ]:
        session.add(GaladrielUserRole(**item))

    session.commit()
    yield session


# ---------------------------------------------------------------------------
# Factory helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def make_case(patch_rx_session):
    """Factory that inserts a CaseModel and returns it."""
    _created = []

    def _factory(name="Test Case", **kwargs):
        session = patch_rx_session
        case = CaseModel(name=name, **kwargs)
        session.add(case)
        session.commit()
        session.refresh(case)
        _created.append(case)
        return case

    return _factory


@pytest.fixture()
def make_step(patch_rx_session):
    """Factory that inserts a StepModel and returns it."""

    def _factory(case_id, order=1, action="Do something", expected="Something happens", **kwargs):
        session = patch_rx_session
        step = StepModel(case_id=case_id, order=order, action=action, expected=expected, **kwargs)
        session.add(step)
        session.commit()
        session.refresh(step)
        return step

    return _factory


@pytest.fixture()
def make_scenario(patch_rx_session):
    """Factory that inserts a ScenarioModel and returns it."""

    def _factory(name="Test Scenario", **kwargs):
        session = patch_rx_session
        scenario = ScenarioModel(name=name, **kwargs)
        session.add(scenario)
        session.commit()
        session.refresh(scenario)
        return scenario

    return _factory


@pytest.fixture()
def make_suite(patch_rx_session):
    """Factory that inserts a SuiteModel and returns it."""

    def _factory(name="Test Suite", **kwargs):
        session = patch_rx_session
        suite = SuiteModel(name=name, **kwargs)
        session.add(suite)
        session.commit()
        session.refresh(suite)
        return suite

    return _factory


@pytest.fixture()
def make_cycle(patch_rx_session):
    """Factory that inserts a CycleModel and returns it."""

    def _factory(name="Test Cycle", threshold="80", **kwargs):
        session = patch_rx_session
        cycle = CycleModel(name=name, threshold=threshold, **kwargs)
        session.add(cycle)
        session.commit()
        session.refresh(cycle)
        return cycle

    return _factory


# ---------------------------------------------------------------------------
# State instantiation helper
# ---------------------------------------------------------------------------

def init_state(state_cls, **field_values):
    """Create a Reflex State subclass instance suitable for testing.

    Uses ``__new__`` to skip Reflex's internal ``__init__`` and then
    bootstraps the bookkeeping attributes (``dirty_vars``, etc.) that
    ``__setattr__`` relies on.  After that, caller-supplied field values
    are written via normal attribute assignment so the state sees them.
    """
    state = state_cls.__new__(state_cls)
    # Bootstrap internal tracking sets that __setattr__ expects
    object.__setattr__(state, "dirty_vars", set())
    object.__setattr__(state, "dirty_substates", set())
    object.__setattr__(state, "_was_touched", False)

    for name, value in field_values.items():
        setattr(state, name, value)

    return state


# ---------------------------------------------------------------------------
# Shared test helpers for linkable/empty cases search split
# ---------------------------------------------------------------------------

class LinkableEmptyCasesTests:
    """Mixin with shared tests for the linkable/empty cases search split.

    Subclasses must define ``_make_and_load(self, patch_rx_session, make_case, make_step, cases)``
    that creates the given cases, calls the appropriate load method, and returns the state.
    Each entry in ``cases`` is a dict with ``name`` and optional ``steps`` (int count).
    """

    def _make_and_load(self, patch_rx_session, make_case, make_step, cases):
        raise NotImplementedError

    def test_linkable_cases_have_steps(self, patch_rx_session, make_case, make_step):
        """Cases with steps appear only in linkable list."""
        state = self._make_and_load(patch_rx_session, make_case, make_step,
                                    [{"name": "Has Steps", "steps": 1}])
        assert len(state.linkable_cases_for_search) == 1
        assert len(state.empty_cases_for_search) == 0

    def test_empty_cases_have_no_steps(self, patch_rx_session, make_case, make_step):
        """Cases without steps appear only in empty list."""
        state = self._make_and_load(patch_rx_session, make_case, make_step,
                                    [{"name": "No Steps"}])
        assert len(state.empty_cases_for_search) == 1
        assert len(state.linkable_cases_for_search) == 0

    def test_mixed_cases_split(self, patch_rx_session, make_case, make_step):
        """Mixed cases split correctly between linkable and empty."""
        state = self._make_and_load(patch_rx_session, make_case, make_step,
                                    [{"name": "With", "steps": 1}, {"name": "Without"}])
        assert [c.name for c in state.linkable_cases_for_search] == ["With"]
        assert [c.name for c in state.empty_cases_for_search] == ["Without"]
