from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from .. import utils

class CaseModel(rx.Model, table=True): 
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