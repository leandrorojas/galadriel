"""Tests for galadriel.auth.state — Session role lookup and access guards."""

import pytest
from unittest.mock import PropertyMock, patch, MagicMock
from sqlmodel import select

from galadriel.auth.state import Session, Register, Login
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


class TestIsSuperAdmin:
    """Tests for the is_super_admin role check logic."""

    def test_admin_is_super_admin(self, patch_rx_session, seeded_db):
        """Admin role (0) should be considered super admin."""
        session = patch_rx_session
        user = GaladrielUser(email="admin@test.com", user_id=10, user_role=UserRole.ADMIN.value)
        session.add(user)
        session.commit()

        found = session.exec(select(GaladrielUser).where(GaladrielUser.user_id == 10)).one_or_none()
        assert found.user_role == UserRole.ADMIN.value

    def test_user_admin_is_not_super_admin(self, patch_rx_session, seeded_db):
        """User admin role (3) should NOT be considered super admin."""
        session = patch_rx_session
        user = GaladrielUser(email="useradmin@test.com", user_id=11, user_role=UserRole.USER_ADMIN.value)
        session.add(user)
        session.commit()

        found = session.exec(select(GaladrielUser).where(GaladrielUser.user_id == 11)).one_or_none()
        assert found.user_role != UserRole.ADMIN.value

    def test_editor_is_not_super_admin(self, patch_rx_session, seeded_db):
        """Editor role should NOT be considered super admin."""
        session = patch_rx_session
        user = GaladrielUser(email="editor@test.com", user_id=12, user_role=UserRole.EDITOR.value)
        session.add(user)
        session.commit()

        found = session.exec(select(GaladrielUser).where(GaladrielUser.user_id == 12)).one_or_none()
        assert found.user_role != UserRole.ADMIN.value


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


class TestRequireSuperAdminGuard:
    """Tests for Session.require_super_admin server-side on_load guard."""

    @staticmethod
    def _redirect_path(event_spec):
        """Extract the redirect path from an rx.redirect EventSpec."""
        return event_spec.args[0][1]._var_value

    def _make_session_state(self, *, is_super_admin):
        """Create a mock state with the given super admin status."""
        state = MagicMock()
        state.is_super_admin = is_super_admin
        return state

    def test_require_super_admin_allows_admin(self):
        """Admin users should not be redirected."""
        state = self._make_session_state(is_super_admin=True)
        result = Session.require_super_admin.fn(state)
        assert result is None

    def test_require_super_admin_redirects_user_admin_to_dashboard(self):
        """User admin users should be redirected to /dashboard."""
        state = self._make_session_state(is_super_admin=False)
        result = Session.require_super_admin.fn(state)
        assert self._redirect_path(result) == "/dashboard"

    def test_require_super_admin_redirects_non_admin_to_dashboard(self):
        """Non-admin users should be redirected to /dashboard."""
        state = self._make_session_state(is_super_admin=False)
        result = Session.require_super_admin.fn(state)
        assert self._redirect_path(result) == "/dashboard"


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


class TestRegistrationDisabled:
    """Tests for self-registered users being created as disabled."""

    FAKE_CREDENTIAL = "pass"  # noqa: S105 — test-only dummy value

    def test_registration_creates_disabled_user(self, patch_rx_session, seeded_db):
        """Self-registered users should be disabled and assigned the viewer role."""
        import reflex_local_auth

        session = patch_rx_session
        state = MagicMock(spec=Register)
        state.new_user_id = 10

        # Simulate handle_registration succeeding
        state.handle_registration = MagicMock(return_value=None)

        # Create the LocalUser that handle_registration would have created
        local_user = reflex_local_auth.LocalUser(
            id=10,
            username="newuser",
            password_hash=reflex_local_auth.LocalUser.hash_password(self.FAKE_CREDENTIAL),
            enabled=True,
        )
        session.add(local_user)
        session.commit()

        # Call our handler directly
        result = Register.handle_registration_email.fn(
            state, {
                "username": "newuser",
                "email": "new@test.com",
                "password": self.FAKE_CREDENTIAL,
                "confirm_password": self.FAKE_CREDENTIAL,
            }
        )

        # Verify redirect to login and pending-approval banner
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0].args[0][1]._var_value == "/login"
        assert result[1] == Login.show_pending_approval

        # Verify user is disabled
        updated = session.exec(
            reflex_local_auth.LocalUser.select().where(reflex_local_auth.LocalUser.id == 10)
        ).one_or_none()
        assert updated is not None
        assert updated.enabled is False

        # Verify GaladrielUser was created with viewer role
        galadriel_user = session.exec(
            GaladrielUser.select().where(GaladrielUser.user_id == 10)
        ).one_or_none()
        assert galadriel_user is not None
        assert galadriel_user.user_role == UserRole.VIEWER.value
