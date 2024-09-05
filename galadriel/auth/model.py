import reflex as rx
import sqlalchemy as sa

from datetime import datetime
from sqlmodel import Field, Relationship

from reflex_local_auth import LocalUser

from .. import utils

class RxTutorialUserInfo(rx.Model, table=True):
    email:str
    user_id:int = Field(foreign_key="localuser.id")
    auth_user: LocalUser = Relationship()
    created: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )
    updated: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'onupdate': sa.func.now(),
            'server_default': sa.func.now()
        },
        nullable=False
    )

class GaladrielUser(rx.Model, table=True):
    email:str
    user_id:int = Field(foreign_key="localuser.id")
    #auth_user: LocalUser = Relationship()
    created: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )
    updated: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'onupdate': sa.func.now(),
            'server_default': sa.func.now()
        },
        nullable=False
    )