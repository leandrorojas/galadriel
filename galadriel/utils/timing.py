"""UTC-aware datetime helpers and SQLModel timestamp field factories."""

from datetime import datetime, timezone
from dateutil import tz
import sqlalchemy as sa
from sqlmodel import Field

def get_utc_now() -> datetime:
    """Return the current datetime in UTC."""
    return datetime.now(timezone.utc)

def ensure_utc(dt: datetime) -> datetime:
    """Ensure the datetime is in UTC."""
    return_dt = datetime.fromisoformat(str(dt).replace('Z', '+00:00'))
    if return_dt.tzinfo is None:
        return_dt = return_dt.replace(tzinfo=timezone.utc)
    return return_dt

def format_datetime(dt: datetime) -> str:
    """Format a datetime as a human-readable UTC ISO string."""
    return ensure_utc(dt).replace(microsecond=0).isoformat(sep=" ")

def convert_utc_to_local(utc_dt: datetime) -> datetime:
    """Convert a UTC datetime to the local timezone."""
    utc_dt = utc_dt.replace(tzinfo=tz.tzutc())
    return utc_dt.astimezone(tz.tzlocal())


def created_field():
    """Standard 'created' timestamp field for models."""
    return Field(
        default_factory=get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={'server_default': sa.func.now()},
        nullable=False
    )


def updated_field(nullable=True):
    """Standard 'updated' timestamp field for models."""
    return Field(
        default_factory=get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={'onupdate': sa.func.now(), 'server_default': sa.func.now()},
        nullable=nullable
    )