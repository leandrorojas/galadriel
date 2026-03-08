"""Test case domain models."""

import reflex as rx

from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field

from ..utils import timing, consts
from ..utils.mixins import TimestampMixin

class CaseModel(TimestampMixin, rx.Model, table=True):
    """Represents a test case."""

    name: str
    created: datetime = timing.created_field()
    deleted: datetime = Field(
        sa_type=sa.DateTime(timezone=True),
        nullable=True
    )

class StepModel(TimestampMixin, rx.Model, table=True):
    """Represents a single step within a test case."""

    case_id:int = Field(foreign_key=consts.CASE_MODEL_ID)
    order:int
    action:str
    expected:str
    created: datetime = timing.created_field()

class PrerequisiteModel(TimestampMixin, rx.Model, table=True):
    """Represents a prerequisite dependency between test cases."""

    case_id:int = Field(foreign_key=consts.CASE_MODEL_ID)
    prerequisite_id:int = Field(foreign_key=consts.CASE_MODEL_ID)
    order:int
    prerequisite_name:str = Field(nullable=True)
    created: datetime = timing.created_field()