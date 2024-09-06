from datetime import datetime
import reflex as rx
import sqlalchemy as sa

from sqlmodel import Field

from .. import utils

class RxTutorialContactModel(rx.Model, table=True):
    first_name:str | None = None
    last_name:str | None = None
    email:str
    contact_message:str
    created: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )