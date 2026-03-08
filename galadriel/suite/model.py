"""Test suite domain models."""

from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from ..utils import timing, consts
from ..utils.mixins import TimestampMixin

class SuiteModel(TimestampMixin, rx.Model, table=True):
    """Represents a test suite."""

    name: str
    created: datetime = timing.created_field()
    deleted: datetime = Field(
        sa_type=sa.DateTime(timezone=True),
        nullable=True
    )

class SuiteChildTypeModel(TimestampMixin, rx.Model, table=True):
    """Represents a type of child that can belong to a suite."""

    type_name:str
    created: datetime = timing.created_field()

class SuiteChildModel(TimestampMixin, rx.Model, table=True):
    """Represents a child item belonging to a suite."""

    suite_id:int = Field(foreign_key="suitemodel.id")
    child_type_id:int = Field(foreign_key="suitechildtypemodel.id")
    child_id:int
    order:int
    child_name:str = Field(nullable=True)
    child_type_name:str = Field(nullable=True)
    created: datetime = timing.created_field()