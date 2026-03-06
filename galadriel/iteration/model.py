from datetime import datetime
import sqlalchemy as sa
from sqlmodel import Field
import reflex as rx

from ..utils import timing, consts
from ..utils.mixins import TimestampMixin

class IterationStatusModel(TimestampMixin, rx.Model, table=True):
    name: str
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )

class IterationModel(TimestampMixin, rx.Model, table=True):
    cycle_id:int = Field(foreign_key="cyclemodel.id")
    iteration_status_id:int = Field(foreign_key="iterationstatusmodel.id")
    iteration_number:int
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )

class IterationSnapshotModel(TimestampMixin, rx.Model, table=True):
    __timestamp_fields__ = ("created", "updated")

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
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=True
    )
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )

class IterationSnapshotStatusModel(TimestampMixin, rx.Model, table=True):
    status_name:str
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )

class IterationSnapshotLinkedIssues(TimestampMixin, rx.Model, table=True):
    iteration_snapshot_id:int = Field(foreign_key="iterationsnapshotmodel.id")
    issue_key:str
    unlinked: bool = Field(nullable=True)
    created: datetime = Field(
        default_factory=timing.get_utc_now,
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False
    )