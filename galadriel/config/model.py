"""Application configuration domain models."""

from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from ..utils import timing
from ..utils.mixins import TimestampMixin

class ConfigModel(TimestampMixin, rx.Model, table=True):
    """Represents a key-value configuration entry."""

    name:str
    value:str
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )