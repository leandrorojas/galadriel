"""Test scenario domain models."""

from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from ..utils import timing, consts
from ..utils.mixins import TimestampMixin

class ScenarioModel(TimestampMixin, rx.Model, table=True):
    """Represents a test scenario."""

    name: str
    created: datetime = timing.created_field()
    deleted: datetime = Field(
        sa_type=sa.DateTime(timezone=True),
        nullable=True
    )

class ScenarioCaseModel(TimestampMixin, rx.Model, table=True):
    """Represents a test case assigned to a scenario."""

    scenario_id:int = Field(foreign_key="scenariomodel.id")
    case_id:int = Field(foreign_key=consts.CASE_MODEL_ID)
    order:int
    case_name:str = Field(nullable=True)
    created: datetime = timing.created_field()