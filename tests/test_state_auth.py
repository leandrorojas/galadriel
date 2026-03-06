"""Tests for galadriel.auth.state — Session role lookup."""

import pytest
from unittest.mock import PropertyMock, patch, MagicMock
from sqlmodel import select

from galadriel.user.model import GaladrielUser, GaladrielUserRole
from galadriel.user.state import UserRole

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
