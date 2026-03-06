"""Tests for galadriel.user.state — UserState business logic."""

import pytest
from unittest.mock import PropertyMock, patch, MagicMock
from sqlmodel import select

from galadriel.user.state import UserState
from galadriel.user.model import GaladrielUser, GaladrielUserRole, GaladrielUserDisplay
from conftest import init_state

pytestmark = pytest.mark.integration


def _make_state(user_id_value=0):
    state = init_state(UserState, users=[], user=None)
    type(state).user_id = PropertyMock(return_value=user_id_value)
    return state


class TestLoadUsers:
    def test_empty_db(self, patch_rx_session, seeded_db):
        state = _make_state()
        with patch("galadriel.user.state.reflex_local_auth") as mock_auth:
            mock_local_user = MagicMock()
            mock_local_user.id = 0
            mock_local_user.username = "admin"
            mock_local_user.enabled = True
            mock_auth.LocalUser.select.return_value.where.return_value = MagicMock()
            state.load_users()
            assert isinstance(state.users, list)


class TestGetUserDetail:
    def test_invalid_user_id_sets_none(self, patch_rx_session):
        state = _make_state(user_id_value=-1)
        state.get_user_detail()
        assert state.user is None

    def test_nonexistent_user_sets_none(self, patch_rx_session, seeded_db):
        state = _make_state(user_id_value=9999)
        state.get_user_detail()
        assert state.user is None

    def test_existing_user(self, patch_rx_session, seeded_db):
        session = patch_rx_session
        user = GaladrielUser(email="test@test.com", user_id=100, user_role=0)
        session.add(user)
        session.commit()
        session.refresh(user)

        state = _make_state(user_id_value=user.id)

        with patch("galadriel.user.state.reflex_local_auth") as mock_auth:
            mock_local_user = MagicMock()
            mock_local_user.id = 100
            mock_local_user.username = "testuser"
            mock_local_user.enabled = True

            mock_select = MagicMock()
            mock_auth.LocalUser.select.return_value.where.return_value = mock_select

            original_exec = session.exec

            def patched_exec(query):
                query_str = str(query)
                if "localuser" in query_str.lower():
                    result = MagicMock()
                    result.one_or_none.return_value = mock_local_user
                    return result
                return original_exec(query)

            session.exec = patched_exec
            state.get_user_detail()

            assert state.user is not None
            assert state.user.email == "test@test.com"
