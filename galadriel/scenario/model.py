from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from ..utils import timing, consts
from ..utils.mixins import TimestampMixin

class ScenarioModel(TimestampMixin, rx.Model, table=True):
    name: str
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )
    deleted: datetime = Field(
        sa_type=sa.DateTime(timezone=True),
        nullable=True
    )

class ScenarioCaseModel(TimestampMixin, rx.Model, table=True):
    scenario_id:int = Field(foreign_key="scenariomodel.id")
    case_id:int = Field(foreign_key=consts.CASE_MODEL_ID)
    order:int
    case_name:str = Field(nullable=True)
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )