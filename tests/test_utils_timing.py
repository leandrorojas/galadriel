"""Tests for galadriel.utils.timing."""

import pytest
from datetime import datetime, timezone, timedelta
from dateutil import tz

from galadriel.utils.timing import get_utc_now, ensure_utc, convert_utc_to_local

pytestmark = pytest.mark.unit


class TestGetUtcNow:
    def test_returns_datetime(self):
        result = get_utc_now()
        assert isinstance(result, datetime)

    def test_has_utc_tzinfo(self):
        result = get_utc_now()
        assert result.tzinfo is not None
        assert result.tzinfo == timezone.utc

    def test_is_close_to_now(self):
        before = datetime.now(timezone.utc)
        result = get_utc_now()
        after = datetime.now(timezone.utc)
        assert before <= result <= after


class TestEnsureUtc:
    def test_naive_datetime_gets_utc(self):
        naive = datetime(2024, 1, 15, 12, 0, 0)
        result = ensure_utc(naive)
        assert result.tzinfo == timezone.utc

    def test_aware_datetime_preserved(self):
        aware = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
        result = ensure_utc(aware)
        assert result.tzinfo is not None
        assert result == aware

    def test_z_suffix_parsed(self):
        result = ensure_utc("2024-01-15T12:00:00Z")
        assert result.year == 2024
        assert result.tzinfo is not None

    def test_offset_string_parsed(self):
        result = ensure_utc("2024-01-15T12:00:00+05:00")
        assert result.year == 2024
        assert result.tzinfo is not None


class TestConvertUtcToLocal:
    def test_returns_local_tz(self):
        utc_dt = datetime(2024, 6, 15, 12, 0, 0)
        result = convert_utc_to_local(utc_dt)
        assert result.tzinfo is not None
        # The local timezone should be applied
        assert result.tzinfo == tz.tzlocal()

    def test_conversion_preserves_instant(self):
        utc_dt = datetime(2024, 6, 15, 12, 0, 0)
        result = convert_utc_to_local(utc_dt)
        # Converting back to UTC should give the same instant
        back_to_utc = result.astimezone(tz.tzutc())
        assert back_to_utc.replace(tzinfo=None) == utc_dt
