import reflex as rx
import sqlalchemy as sa

from datetime import datetime
from sqlmodel import Field

from .. import utils

class UserInfo(rx.Model, table=True):
    email:str
    user_id:int = Field(foreign_key="localuser.id")
    created: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=True
    )
    updated: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'onupdate': sa.func.now(),
            'server_default': sa.func.now()
        },
        nullable=True
    )

    #Other fields --> can_use_galadriel: bool <- self explanatory 