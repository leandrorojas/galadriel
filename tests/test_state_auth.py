"""Tests for galadriel.auth.state — Session role lookup and access guards."""

import pytest
from unittest.mock import PropertyMock, patch, MagicMock
from sqlmodel import select

from galadriel.auth.state import Session
from galadriel.user.model import GaladrielUser, GaladrielUserRole
from galadriel.user.state import UserRole
from conftest import init_state

pytestmark = pytest.mark.integration


class TestSessionRole:
    def test_role_lookup_with_user(self, patch_rx_session, seeded_db):
        """When a GaladrielUser exists with user_role=0, the role should be ADMIN."""
        session = patch_rx_session
        user = GaladrielUser(email="admin@test.com", user_id=1, user_role=0)
        session.add(user)
        session.commit()
        session.refresh(user)

        # Look up the user and verify role mapping
        found = session.exec(
            select(GaladrielUser).where(GaladrielUser.user_id == 1)
        ).one_or_none()
        assert found is not None
        assert UserRole(found.user_role) == UserRole.ADMIN

    def test_viewer_role(self, patch_rx_session, seeded_db):
        session = patch_rx_session
        user = GaladrielUser(email="viewer@test.com", user_id=2, user_role=1)
        session.add(user)
        session.commit()

        found = session.exec(
            select(GaladrielUser).where(GaladrielUser.user_id == 2)
        ).one_or_none()
        assert UserRole(found.user_role) == UserRole.VIEWER

    def test_editor_role(self, patch_rx_session, seeded_db):
        session = patch_rx_session
        user = GaladrielUser(email="editor@test.com", user_id=3, user_role=2)
        session.add(user)
        session.commit()

        found = session.exec(
            select(GaladrielUser).where(GaladrielUser.user_id == 3)
        ).one_or_none()
        assert UserRole(found.user_role) == UserRole.EDITOR

    def test_role_from_seeded_roles(self, patch_rx_session, seeded_db):
        """Verify seeded GaladrielUserRole rows exist."""
        session = patch_rx_session
        roles = session.exec(select(GaladrielUserRole)).all()
        role_names = {r.name for r in roles}
        assert "admin" in role_names
        assert "viewer" in role_names
        assert "editor" in role_names
        assert "user manager" in role_names

    def test_user_admin_role(self, patch_rx_session, seeded_db):
        """user_admin role should map correctly."""
        session = patch_rx_session
        user = GaladrielUser(email="useradmin@test.com", user_id=4, user_role=3)
        session.add(user)
        session.commit()

        found = session.exec(
            select(GaladrielUser).where(GaladrielUser.user_id == 4)
        ).one_or_none()
        assert UserRole(found.user_role) == UserRole.USER_ADMIN


class TestRequireAdminGuard:
    """Tests for Session.require_admin server-side on_load guard."""

    @staticmethod
    def _redirect_path(event_spec):
        """Extract the redirect path from an rx.redirect EventSpec."""
        return event_spec.args[0][1]._var_value

    def _make_session_state(self, *, is_admin):
        state = MagicMock()
        state.is_admin = is_admin
        return state

    def test_require_admin_allows_admin(self):
        """Admin/user_admin users should not be redirected."""
        state = self._make_session_state(is_admin=True)
        result = Session.require_admin.fn(state)
        assert result is None

    def test_require_admin_redirects_non_admin_to_dashboard(self):
        """Non-admin users should be redirected to /dashboard."""
        state = self._make_session_state(is_admin=False)
        result = Session.require_admin.fn(state)
        assert self._redirect_path(result) == "/dashboard"

    def test_require_non_admin_allows_non_admin(self):
        """Non-admin users should not be redirected."""
        state = self._make_session_state(is_admin=False)
        result = Session.require_non_admin.fn(state)
        assert result is None

    def test_require_non_admin_redirects_admin_to_users(self):
        """Admin/user_admin users should be redirected to /users."""
        state = self._make_session_state(is_admin=True)
        result = Session.require_non_admin.fn(state)
        assert self._redirect_path(result) == "/users"


class TestRequireEditorGuard:
    """Tests for Session.require_editor server-side on_load guard."""

    @staticmethod
    def _redirect_path(event_spec):
        """Extract the redirect path from an rx.redirect EventSpec."""
        return event_spec.args[0][1]._var_value

    def _make_session_state(self, *, role, is_authenticated=True):
        state = MagicMock()
        state.role = role
        state.is_authenticated = is_authenticated
        return state

    def test_require_editor_allows_editor(self):
        """Editor users should not be redirected."""
        state = self._make_session_state(role=UserRole.EDITOR)
        result = Session.require_editor.fn(state)
        assert result is None

    def test_require_editor_allows_admin(self):
        """Admin users should not be redirected."""
        state = self._make_session_state(role=UserRole.ADMIN)
        result = Session.require_editor.fn(state)
        assert result is None

    def test_require_editor_allows_user_admin(self):
        """User admin users should not be redirected."""
        state = self._make_session_state(role=UserRole.USER_ADMIN)
        result = Session.require_editor.fn(state)
        assert result is None

    def test_require_editor_redirects_viewer_to_dashboard(self):
        """Viewer users should be redirected to /dashboard."""
        state = self._make_session_state(role=UserRole.VIEWER)
        result = Session.require_editor.fn(state)
        assert self._redirect_path(result) == "/dashboard"

    def test_require_editor_redirects_unauthenticated_to_login(self):
        """Unauthenticated users should be redirected to login."""
        from reflex_local_auth.login import LoginState
        state = self._make_session_state(role=None, is_authenticated=False)
        result = Session.require_editor.fn(state)
        assert result == LoginState.redir
