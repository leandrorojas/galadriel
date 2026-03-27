"""Tests for galadriel.config.helpers — get_setting and set_setting."""

import pytest
from galadriel.config.helpers import get_setting, set_setting
from galadriel.config.model import ConfigModel

pytestmark = pytest.mark.integration


class TestGetSetting:
    def test_returns_default_when_missing(self, patch_rx_session, seeded_db):
        """Missing key should return the default value."""
        result = get_setting("nonexistent", "fallback")
        assert result == "fallback"

    def test_returns_empty_default(self, patch_rx_session, seeded_db):
        """Missing key with no default should return empty string."""
        result = get_setting("nonexistent")
        assert result == ""

    def test_returns_stored_value(self, patch_rx_session, seeded_db):
        """Stored setting should be returned."""
        session = patch_rx_session
        session.add(ConfigModel(name="test_key", value="test_value"))
        session.commit()

        result = get_setting("test_key")
        assert result == "test_value"


class TestSetSetting:
    def test_creates_new_setting(self, patch_rx_session, seeded_db):
        """set_setting should create a new row when key doesn't exist."""
        set_setting("new_key", "new_value")
        result = get_setting("new_key")
        assert result == "new_value"

    def test_updates_existing_setting(self, patch_rx_session, seeded_db):
        """set_setting should update the value when key already exists."""
        set_setting("update_key", "old_value")
        set_setting("update_key", "new_value")
        result = get_setting("update_key")
        assert result == "new_value"

    def test_round_trip(self, patch_rx_session, seeded_db):
        """Multiple settings should be independent."""
        set_setting("key_a", "value_a")
        set_setting("key_b", "value_b")
        assert get_setting("key_a") == "value_a"
        assert get_setting("key_b") == "value_b"
