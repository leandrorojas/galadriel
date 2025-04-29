from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from .. import utils

class IterationStatusModel(rx.Model, table=True): 
    name: str
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
    
class IterationModel(rx.Model, table=True):
    cycle_id:int = Field(foreign_key="cyclemodel.id")
    iteration_status_id:int = Field(foreign_key="iterationstatusmodel.id")
    iteration_number:int
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

class IterationSnapshotModel(rx.Model, table=True):
    iteration_id:int = Field(foreign_key="iterationmodel.id")
    order:int
    child_type:int
    child_id:int = Field(nullable=True)
    child_name:str = Field(nullable=True)
    child_action:str = Field(nullable=True)
    child_expected:str = Field(nullable=True)
    child_status_id:int = Field(foreign_key="iterationsnapshotstatusmodel.id", nullable=True)
    linked_issue:str = Field(nullable=True)
    linked_issue_status:str = Field(nullable=True)
    updated: datetime = Field(
        default_factory=utils.timing.get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=True
    )
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
        d["updated"] = self.created.replace(microsecond=0).isoformat(sep=" ")
        return d
    
class IterationSnapshotStatusModel(rx.Model, table=True):
    status_name:str
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

class IterationSnapshotLinkedIssues(rx.Model, table=True):
    iteration_snapshot_id:int = Field(foreign_key="iterationsnapshotmodel.id")
    issue_key:str
    unlinked: bool = Field(nullable=True)
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