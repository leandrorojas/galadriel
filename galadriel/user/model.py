import reflex as rx

from datetime import datetime
from sqlmodel import Field

from ..utils import timing
from ..utils.mixins import TimestampMixin

class GaladrielUser(TimestampMixin, rx.Model, table=True):
    __timestamp_fields__ = ("created", "updated")

    email:str
    user_id:int = Field(foreign_key="localuser.id")
    user_role:int = Field(foreign_key="galadrieluserrole.id")
    created: datetime = timing.created_field()
    updated: datetime = timing.updated_field(nullable=False)

class GaladrielUserDisplay(rx.Model):
    local_user_id:int
    galadriel_user_id:int
    username:str
    email:str
    role:str
    enabled: bool
    created: datetime
    updated: datetime

class GaladrielUserRole(TimestampMixin, rx.Model, table=True):
    __timestamp_fields__ = ("created", "updated")

    name:str
    description:str = Field(nullable = True)
    created: datetime = timing.created_field()
    updated: datetime = timing.updated_field(nullable=False)