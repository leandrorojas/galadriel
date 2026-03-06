from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from ..utils import timing, consts
from ..utils.mixins import TimestampMixin

class SuiteModel(TimestampMixin, rx.Model, table=True):
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

class SuiteChildTypeModel(TimestampMixin, rx.Model, table=True):
    type_name:str
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )

class SuiteChildModel(TimestampMixin, rx.Model, table=True):
    suite_id:int = Field(foreign_key="suitemodel.id")
    child_type_id:int = Field(foreign_key="suitechildtypemodel.id")
    child_id:int
    order:int
    child_name:str = Field(nullable=True)
    child_type_name:str = Field(nullable=True)
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )