from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from .. import utils

class CycleModel(rx.Model, table=True):
    name: str
    threshold:str = Field(nullable = True)
    iteration_status_name:str = Field(nullable=True)
    cycle_status_name: str = Field(nullable=True)
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

    def dict(self, *args, **kwargs) -> dict:
        """Serialize method."""
        d = super().dict(*args, **kwargs)
        d["created"] = self.created.replace(microsecond=0).isoformat(sep=" ")
        return d

class CycleChildTypeModel(rx.Model, table=True):
    type_name:str
    created: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
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
    
class CycleStatusModel(rx.Model, table=True):
    status_name: str
    created: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
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

class CycleChildModel(rx.Model, table=True):
    cycle_id:int = Field(foreign_key="cyclemodel.id")
    child_type_id:int = Field(foreign_key="cyclechildtypemodel.id")
    child_id:int
    order:int
    child_name:str = Field(nullable=True)
    created: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
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