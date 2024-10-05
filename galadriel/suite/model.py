from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from .. import utils

class SuiteModel(rx.Model, table=True):
    name: str
    created: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
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
    #created_by

class SuiteChildTypeModel(rx.Model, table=True):
    type_name:str
    created: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )

class SuiteChildModel(rx.Model, table=True):
    suite_id:int = Field(foreign_key="suitemodel.id")
    child_type_id:int = Field(foreign_key="suitechildtypemodel.id")
    child_id:int
    order:int
    child_name:str = Field(nullable=True)
    child_type_name:str = Field(nullable=True)
    created: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )