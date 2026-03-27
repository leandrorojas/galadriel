"""Action log domain model."""

from datetime import datetime
from typing import Optional

import reflex as rx
from sqlmodel import Field

from ..utils import timing
from ..utils.mixins import TimestampMixin


class ActionLogModel(TimestampMixin, rx.Model, table=True):
    """Represents an auditable user action."""

    user_id: int = Field(nullable=False)
    username: str = Field(nullable=False)
    action: str = Field(nullable=False)
    entity_type: str = Field(default="", nullable=False)
    entity_name: str = Field(default="", nullable=False)
    detail: str = Field(default="", nullable=False)
    created: datetime = timing.created_field()


class ActionLogDisplay(rx.Model):
    """Read-only view model for displaying action log entries."""

    log_id: int
    user_id: int
    username: str
    action: str
    entity_type: str
    entity_name: str
    detail: str
    created: datetime
