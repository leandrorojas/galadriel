"""Tests for galadriel.audit — action log model, helpers, and state."""

import pytest
from sqlmodel import select

from galadriel.audit.model import ActionLogModel
from galadriel.audit.helpers import log_action
from galadriel.audit.state import ActionLogState
from conftest import init_state

pytestmark = pytest.mark.integration


class TestLogAction:
    """Tests for the log_action helper."""

    def test_creates_entry(self, patch_rx_session, seeded_db):
        """log_action should insert a new ActionLogModel row."""
        log_action(
            user_id=1,
            username="admin",
            action="created",
            entity_type="suite",
            entity_name="Smoke Tests",
        )
        session = patch_rx_session
        rows = session.exec(select(ActionLogModel)).all()
        assert len(rows) == 1
        assert rows[0].username == "admin"
        assert rows[0].action == "created"
        assert rows[0].entity_type == "suite"
        assert rows[0].entity_name == "Smoke Tests"

    def test_creates_entry_with_detail(self, patch_rx_session, seeded_db):
        """log_action should store the detail field."""
        log_action(
            user_id=1,
            username="admin",
            action="updated",
            entity_type="case",
            entity_name="Login Test",
            detail="Changed name from 'Login' to 'Login Test'",
        )
        session = patch_rx_session
        row = session.exec(select(ActionLogModel)).one()
        assert row.detail == "Changed name from 'Login' to 'Login Test'"

    def test_creates_entry_minimal(self, patch_rx_session, seeded_db):
        """log_action should work with only required fields."""
        log_action(user_id=2, username="editor", action="logged_in")
        session = patch_rx_session
        row = session.exec(select(ActionLogModel)).one()
        assert row.entity_type == ""
        assert row.entity_name == ""
        assert row.detail == ""

    def test_created_timestamp_set(self, patch_rx_session, seeded_db):
        """log_action entries should have a created timestamp."""
        log_action(user_id=1, username="admin", action="test")
        session = patch_rx_session
        row = session.exec(select(ActionLogModel)).one()
        assert row.created is not None


class TestActionLogState:
    """Tests for ActionLogState load and selection."""

    def _seed_entries(self, session):
        """Insert sample action log entries."""
        entries = [
            ActionLogModel(user_id=1, username="admin", action="created", entity_type="suite", entity_name="Suite A"),
            ActionLogModel(user_id=2, username="editor", action="updated", entity_type="case", entity_name="Case B"),
            ActionLogModel(user_id=1, username="admin", action="deleted", entity_type="scenario", entity_name="Scenario C"),
        ]
        for e in entries:
            session.add(e)
        session.commit()

    def test_load_entries(self, patch_rx_session, seeded_db):
        """load_entries should populate the entries list."""
        self._seed_entries(patch_rx_session)
        state = init_state(ActionLogState, search_value="")
        ActionLogState.load_entries.fn(state)
        assert len(state.entries) == 3

    def test_load_entries_clears_selection(self, patch_rx_session, seeded_db):
        """load_entries should clear any selected entry."""
        self._seed_entries(patch_rx_session)
        state = init_state(ActionLogState, search_value="")
        ActionLogState.load_entries.fn(state)
        # Select first entry, then reload
        ActionLogState.select_entry.fn(state, state.entries[0].log_id)
        assert state.selected_entry is not None
        ActionLogState.load_entries.fn(state)
        assert state.selected_entry is None

    def test_select_entry(self, patch_rx_session, seeded_db):
        """select_entry should set the selected_entry."""
        self._seed_entries(patch_rx_session)
        state = init_state(ActionLogState, search_value="")
        ActionLogState.load_entries.fn(state)
        first_id = state.entries[0].log_id
        ActionLogState.select_entry.fn(state, first_id)
        assert state.selected_entry is not None
        assert state.selected_entry.log_id == first_id

    def test_clear_selection(self, patch_rx_session, seeded_db):
        """clear_selection should set selected_entry to None."""
        self._seed_entries(patch_rx_session)
        state = init_state(ActionLogState, search_value="")
        ActionLogState.load_entries.fn(state)
        ActionLogState.select_entry.fn(state, state.entries[0].log_id)
        ActionLogState.clear_selection.fn(state)
        assert state.selected_entry is None

    def test_filter_entries_by_username(self, patch_rx_session, seeded_db):
        """filter_entries should narrow results by username."""
        self._seed_entries(patch_rx_session)
        state = init_state(ActionLogState, search_value="")
        ActionLogState.filter_entries.fn(state, "editor")
        assert len(state.entries) == 1
        assert state.entries[0].username == "editor"

    def test_filter_entries_by_action(self, patch_rx_session, seeded_db):
        """filter_entries should narrow results by action."""
        self._seed_entries(patch_rx_session)
        state = init_state(ActionLogState, search_value="")
        ActionLogState.filter_entries.fn(state, "deleted")
        assert len(state.entries) == 1
        assert state.entries[0].action == "deleted"

    def test_filter_entries_empty_returns_all(self, patch_rx_session, seeded_db):
        """Empty filter should return all entries."""
        self._seed_entries(patch_rx_session)
        state = init_state(ActionLogState, search_value="")
        ActionLogState.filter_entries.fn(state, "")
        assert len(state.entries) == 3
