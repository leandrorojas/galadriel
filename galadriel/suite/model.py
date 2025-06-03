from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from ..utils import timing, consts

class SuiteModel(rx.Model, table=True):
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

    def dict(self, *args, **kwargs) -> dict:
        """Serialize method."""
        d = super().dict(*args, **kwargs)
        d["created"] = timing.ensure_utc(self.created).replace(microsecond=0).isoformat(sep=" ")
        return d

class SuiteChildTypeModel(rx.Model, table=True):
    type_name:str
    created: datetime = Field(
        default_factory=timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )

    def dict(self, *args, **kwargs) -> dict:
        """Serialize method."""
        d = super().dict(*args, **kwargs)
        d["created"] = self.created.replace(microsecond=0).isoformat(sep=" ")
        return d

class SuiteChildModel(rx.Model, table=True):
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

    def dict(self, *args, **kwargs) -> dict:
        """Serialize method."""
        d = super().dict(*args, **kwargs)
        d["created"] = self.created.replace(microsecond=0).isoformat(sep=" ")
        return d