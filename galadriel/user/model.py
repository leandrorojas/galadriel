import reflex as rx
import sqlalchemy as sa

from datetime import datetime
from sqlmodel import Field

from ..utils import timing

class GaladrielUser(rx.Model, table=True):
    email:str
    user_id:int = Field(foreign_key="localuser.id")
    user_role:int = Field(foreign_key="galadrieluserrole.id")
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )
    updated: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'onupdate': sa.func.now(),
            'server_default': sa.func.now()
        },
        nullable=False
    )

class GaladrielUserDisplay(rx.Model):
    local_user_id:int
    galadriel_user_id:int
    username:str
    email:str
    role:str
    enabled: bool
    created: datetime
    updated: datetime

class GaladrielUserRole(rx.Model, table=True):
    name:str
    description:str = Field(nullable = True)
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )
    updated: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'onupdate': sa.func.now(),
            'server_default': sa.func.now()
        },
        nullable=False
    )