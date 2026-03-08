"""Test cycle domain models."""

from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from ..utils import timing, consts
from ..utils.mixins import TimestampMixin

class CycleModel(TimestampMixin, rx.Model, table=True):
    """Represents a test cycle."""

    name: str
    threshold:str = Field(nullable = True)
    iteration_status_name:str = Field(nullable=True)
    cycle_status_name: str = Field(nullable=True)
    created: datetime = timing.created_field()
    deleted: datetime = Field(
        sa_type=sa.DateTime(timezone=True),
        nullable=True
    )

class CycleChildTypeModel(TimestampMixin, rx.Model, table=True):
    """Represents a type of child that can belong to a cycle."""

    type_name:str
    created: datetime = timing.created_field()

class CycleStatusModel(TimestampMixin, rx.Model, table=True):
    """Represents a cycle status option."""

    status_name: str
    created: datetime = timing.created_field()

class CycleChildModel(TimestampMixin, rx.Model, table=True):
    """Represents a child item belonging to a cycle."""

    cycle_id:int = Field(foreign_key="cyclemodel.id")
    child_type_id:int = Field(foreign_key="cyclechildtypemodel.id")
    child_id:int
    order:int
    child_name:str = Field(nullable=True)
    created: datetime = timing.created_field()