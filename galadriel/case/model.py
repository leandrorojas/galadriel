import reflex as rx

from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field

from ..utils import timing, consts

class CaseModel(rx.Model, table=True): 
    name: str
    created: datetime = Field(
        default_factory=timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={'server_default': sa.func.now()},
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

class StepModel(rx.Model, table=True):
    case_id:int = Field(foreign_key=consts.CASE_MODEL_ID)
    order:int
    action:str
    expected:str
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

class PrerequisiteModel(rx.Model, table=True):
    case_id:int = Field(foreign_key=consts.CASE_MODEL_ID)
    prerequisite_id:int = Field(foreign_key=consts.CASE_MODEL_ID)
    order:int
    prerequisite_name:str = Field(nullable=True)
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
        d["created"] = timing.ensure_utc(self.created).replace(microsecond=0).isoformat(sep=" ")
        return d