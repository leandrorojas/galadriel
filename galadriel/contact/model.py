from datetime import datetime, timezone
import reflex as rx
import sqlalchemy as sa
from sqlmodel import Field

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ContactModel(rx.Model, table=True):
    first_name:str | None = None
    last_name:str | None = None
    email:str
    contact_message:str
    created: datetime = Field(
        default_factory=get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )