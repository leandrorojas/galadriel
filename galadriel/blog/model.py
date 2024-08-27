from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from .. import utils

class BlogPostModel(rx.Model, table=True):
    title: str
    content: str
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
    publish_active:bool = False
    published: datetime = Field(
        default_factory=None, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={},
        nullable=True
    )