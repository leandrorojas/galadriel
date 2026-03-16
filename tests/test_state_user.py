"""Tests for galadriel.user.state — UserState business logic."""

import pytest
import string
from unittest.mock import PropertyMock, patch, MagicMock
from sqlmodel import select

from galadriel.user.state import UserState, AddUserState, EditUserState, generate_password, PASSWORD_LENGTH, EMAIL_RE, USERNAME_RE
from galadriel.user.model import GaladrielUser, GaladrielUserRole, GaladrielUserDisplay
from conftest import init_state

pytestmark = pytest.mark.integration


def _make_state(user_id_value=0):
    state = init_state(UserState, users=[], user=None)
    type(state).user_id = PropertyMock(return_value=user_id_value)
    return state


class TestLoadUsers:
    """Tests for loading and listing users."""

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
    """Tests for retrieving a single user's details."""

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


class TestGeneratePassword:
    """Tests for secure password generation."""

    pytestmark = pytest.mark.unit

    def test_length(self):
        """Generated password should have the expected length."""
        pw = generate_password()
        assert len(pw) == PASSWORD_LENGTH

    def test_has_upper(self):
        """Generated password should contain at least one uppercase letter."""
        pw = generate_password()
        assert any(c in string.ascii_uppercase for c in pw)

    def test_has_lower(self):
        """Generated password should contain at least one lowercase letter."""
        pw = generate_password()
        assert any(c in string.ascii_lowercase for c in pw)

    def test_has_digit(self):
        """Generated password should contain at least one digit."""
        pw = generate_password()
        assert any(c in string.digits for c in pw)

    def test_has_symbol(self):
        """Generated password should contain at least one symbol."""
        pw = generate_password()
        assert any(c in string.punctuation for c in pw)

    def test_unique(self):
        """Two generated passwords should differ."""
        assert generate_password() != generate_password()


class TestAddUser:
    """Tests for user creation logic and validation."""

    def _make_add_state(self):
        parent = init_state(UserState, users=[], user=None)
        state = init_state(AddUserState, form_data={}, generated_password="", show_password_dialog=False)
        object.__setattr__(state, "parent_state", parent)
        return state

    def test_add_user_empty_username(self, patch_rx_session, seeded_db):
        """Empty username should return error."""
        state = self._make_add_state()
        password, error = state.add_user({"username": "", "email": "test@t.com", "role": "viewer"})
        assert password is None
        assert "Username" in error

    def test_add_user_empty_email(self, patch_rx_session, seeded_db):
        """Empty email should return error."""
        state = self._make_add_state()
        password, error = state.add_user({"username": "testuser", "email": "", "role": "viewer"})
        assert password is None
        assert "Email" in error

    def test_add_user_duplicate_email(self, patch_rx_session, seeded_db):
        """Duplicate email should return error."""
        session = patch_rx_session
        session.add(GaladrielUser(email="taken@test.com", user_id=100, user_role=1))
        session.commit()

        state = self._make_add_state()
        with patch("galadriel.user.state.reflex_local_auth") as mock_auth:
            mock_auth.LocalUser.select.return_value.where.return_value = MagicMock()
            original_exec = session.exec

            def patched_exec(query):
                query_str = str(query)
                if "localuser" in query_str.lower():
                    result = MagicMock()
                    result.one_or_none.return_value = None
                    return result
                return original_exec(query)

            session.exec = patched_exec
            password, error = state.add_user({"username": "newuser", "email": "taken@test.com", "role": "viewer"})
            assert password is None
            assert "Email" in error

    def test_add_user_admin_role_rejected(self, patch_rx_session, seeded_db):
        """Attempting to assign admin role should return error."""
        session = patch_rx_session
        state = self._make_add_state()
        with patch("galadriel.user.state.reflex_local_auth") as mock_auth:
            mock_auth.LocalUser.select.return_value.where.return_value = MagicMock()
            mock_auth.LocalUser.hash_password.return_value = b"hash"
            original_exec = session.exec

            def patched_exec(query):
                query_str = str(query)
                if "localuser" in query_str.lower():
                    result = MagicMock()
                    result.one_or_none.return_value = None
                    return result
                return original_exec(query)

            session.exec = patched_exec
            password, error = state.add_user({"username": "newuser", "email": "new@t.com", "role": "admin"})
            assert password is None
            assert "Invalid role" in error

            # Verify no GaladrielUser was created for this username
            created = session.exec(
                GaladrielUser.select().where(GaladrielUser.email == "new@t.com")
            ).one_or_none()
            assert created is None

    def test_add_user_invalid_role(self, patch_rx_session, seeded_db):
        """Nonexistent role should return error."""
        session = patch_rx_session
        state = self._make_add_state()
        with patch("galadriel.user.state.reflex_local_auth") as mock_auth:
            mock_auth.LocalUser.select.return_value.where.return_value = MagicMock()

            original_exec = session.exec

            def patched_exec(query):
                query_str = str(query)
                if "localuser" in query_str.lower():
                    result = MagicMock()
                    result.one_or_none.return_value = None
                    return result
                return original_exec(query)

            session.exec = patched_exec
            password, error = state.add_user({"username": "newuser", "email": "new@t.com", "role": "nonexistent"})
            assert password is None
            assert "Invalid role" in error

            # Verify no GaladrielUser was created for this username
            created = session.exec(
                GaladrielUser.select().where(GaladrielUser.email == "new@t.com")
            ).one_or_none()
            assert created is None


class TestEditUser:
    """Tests for editing existing users."""

    def _make_edit_state(self, user_id_value=0):
        parent = init_state(UserState, users=[], user=None)
        type(parent).user_id = PropertyMock(return_value=user_id_value)
        state = init_state(
            EditUserState,
            edit_email="", edit_role="", edit_enabled=True,
        )
        object.__setattr__(state, "parent_state", parent)
        type(state).user_id = PropertyMock(return_value=user_id_value)
        return state

    def _seed_user(self, session, email="edit@test.com", user_role=1):
        """Create a GaladrielUser and return it refreshed."""
        user = GaladrielUser(email=email, user_id=200, user_role=user_role)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    def test_edit_user_empty_email(self, patch_rx_session, seeded_db):
        """Empty email should return error toast."""
        user = self._seed_user(patch_rx_session)
        state = self._make_edit_state(user_id_value=user.id)
        result = state.handle_submit({"email": "", "role": "viewer", "enabled": "on"})
        assert "empty" in str(result).lower()

    def test_edit_user_invalid_email(self, patch_rx_session, seeded_db):
        """Invalid email should return error toast."""
        user = self._seed_user(patch_rx_session)
        state = self._make_edit_state(user_id_value=user.id)
        result = state.handle_submit({"email": "bad", "role": "viewer", "enabled": "on"})
        assert "valid email" in str(result).lower()

    def test_edit_user_invalid_role(self, patch_rx_session, seeded_db):
        """Nonexistent role should return error toast."""
        user = self._seed_user(patch_rx_session)
        state = self._make_edit_state(user_id_value=user.id)

        with patch("galadriel.user.state.reflex_local_auth") as mock_auth:
            mock_auth.LocalUser.select.return_value.where.return_value = MagicMock()
            original_exec = patch_rx_session.exec

            def patched_exec(query):
                query_str = str(query)
                if "localuser" in query_str.lower():
                    result = MagicMock()
                    result.one_or_none.return_value = None
                    return result
                return original_exec(query)

            patch_rx_session.exec = patched_exec
            result = state.handle_submit({"email": "new@test.com", "role": "nonexistent", "enabled": "on"})
            assert "Invalid role" in str(result)

    def test_edit_user_admin_role_rejected(self, patch_rx_session, seeded_db):
        """Assigning admin role via edit should return error."""
        user = self._seed_user(patch_rx_session)
        state = self._make_edit_state(user_id_value=user.id)

        with patch("galadriel.user.state.reflex_local_auth") as mock_auth:
            mock_auth.LocalUser.select.return_value.where.return_value = MagicMock()
            original_exec = patch_rx_session.exec

            def patched_exec(query):
                query_str = str(query)
                if "localuser" in query_str.lower():
                    result = MagicMock()
                    result.one_or_none.return_value = None
                    return result
                return original_exec(query)

            patch_rx_session.exec = patched_exec
            result = state.handle_submit({"email": "new@test.com", "role": "admin", "enabled": "on"})
            assert "Invalid role" in str(result)

    def test_edit_admin_email_allowed(self, patch_rx_session, seeded_db):
        """Changing the admin email should succeed."""
        session = patch_rx_session
        user = self._seed_user(session, email="admin@test.com", user_role=0)
        state = self._make_edit_state(user_id_value=user.id)
        result = state.handle_submit({"email": "newadmin@test.com", "role": "admin", "enabled": "on"})
        # Should redirect (success)
        assert result is not None
        updated = session.exec(
            GaladrielUser.select().where(GaladrielUser.id == user.id)
        ).one_or_none()
        assert updated.email == "newadmin@test.com"

    def test_edit_admin_role_change_rejected(self, patch_rx_session, seeded_db):
        """Changing the admin role should return error toast."""
        user = self._seed_user(patch_rx_session, email="admin@test.com", user_role=0)
        state = self._make_edit_state(user_id_value=user.id)
        result = state.handle_submit({"email": "admin@test.com", "role": "viewer", "enabled": "on"})
        assert "cannot be changed" in str(result).lower()

    def test_edit_admin_deactivation_rejected(self, patch_rx_session, seeded_db):
        """Deactivating the admin account should return error toast."""
        user = self._seed_user(patch_rx_session, email="admin@test.com", user_role=0)
        state = self._make_edit_state(user_id_value=user.id)
        result = state.handle_submit({"email": "admin@test.com", "role": "admin", "enabled": ""})
        assert "cannot be changed" in str(result).lower()

    def test_edit_user_duplicate_email(self, patch_rx_session, seeded_db):
        """Duplicate email (from another user) should return error."""
        session = patch_rx_session
        self._seed_user(session, email="taken@test.com", user_role=1)
        target = GaladrielUser(email="target@test.com", user_id=201, user_role=1)
        session.add(target)
        session.commit()
        session.refresh(target)

        state = self._make_edit_state(user_id_value=target.id)

        with patch("galadriel.user.state.reflex_local_auth") as mock_auth:
            mock_auth.LocalUser.select.return_value.where.return_value = MagicMock()
            original_exec = session.exec

            def patched_exec(query):
                query_str = str(query)
                if "localuser" in query_str.lower():
                    result = MagicMock()
                    result.one_or_none.return_value = None
                    return result
                return original_exec(query)

            session.exec = patched_exec
            result = state.handle_submit({"email": "taken@test.com", "role": "viewer", "enabled": "on"})
            assert "Email" in str(result)

    def test_edit_user_success(self, patch_rx_session, seeded_db):
        """Valid edit should update the user and redirect."""
        session = patch_rx_session
        user = self._seed_user(session, email="old@test.com", user_role=1)
        state = self._make_edit_state(user_id_value=user.id)

        with patch("galadriel.user.state.reflex_local_auth") as mock_auth:
            mock_local_user = MagicMock()
            mock_local_user.id = 200
            mock_local_user.enabled = True
            mock_auth.LocalUser.select.return_value.where.return_value = MagicMock()
            original_exec = session.exec

            def patched_exec(query):
                query_str = str(query)
                if "localuser" in query_str.lower():
                    result = MagicMock()
                    result.one_or_none.return_value = mock_local_user
                    return result
                return original_exec(query)

            session.exec = patched_exec
            result = state.handle_submit({"email": "new@test.com", "role": "editor", "enabled": "on"})

            # Should redirect to user detail
            assert "redirect" in str(type(result)).lower() or result is not None

            # Verify DB was updated
            session.exec = original_exec
            updated = session.exec(
                GaladrielUser.select().where(GaladrielUser.id == user.id)
            ).one_or_none()
            assert updated.email == "new@test.com"
            assert updated.user_role == 2  # editor


class TestEmailValidation:
    """Tests for email regex validation."""

    pytestmark = pytest.mark.unit

    def test_valid_email(self):
        """Standard email should match."""
        assert EMAIL_RE.fullmatch("user@example.com")

    def test_missing_at(self):
        """Email without @ should not match."""
        assert not EMAIL_RE.fullmatch("userexample.com")

    def test_missing_domain(self):
        """Email without domain should not match."""
        assert not EMAIL_RE.fullmatch("user@")

    def test_spaces_rejected(self):
        """Email with spaces should not match."""
        assert not EMAIL_RE.fullmatch("mor di o!!@ doiadioaij")

    def test_missing_tld(self):
        """Email without TLD should not match."""
        assert not EMAIL_RE.fullmatch("user@example")


class TestUsernameValidation:
    """Tests for username regex validation."""

    pytestmark = pytest.mark.unit

    def test_valid_alphanumeric(self):
        """Simple alphanumeric username should match."""
        assert USERNAME_RE.fullmatch("john123")

    def test_valid_with_dots_hyphens_underscores(self):
        """Username with dots, hyphens, and underscores should match."""
        assert USERNAME_RE.fullmatch("john.doe-smith_jr")

    def test_spaces_rejected(self):
        """Username with spaces should not match."""
        assert not USERNAME_RE.fullmatch("rick sanchez")

    def test_special_chars_rejected(self):
        """Username with special characters should not match."""
        assert not USERNAME_RE.fullmatch("user<script>")
        assert not USERNAME_RE.fullmatch("user'; DROP TABLE")
        assert not USERNAME_RE.fullmatch("user@name")

    def test_empty_rejected(self):
        """Empty username should not match."""
        assert not USERNAME_RE.fullmatch("")
