"""Action log state for the audit log page."""

import reflex as rx
from sqlmodel import select, col

from .model import ActionLogModel, ActionLogDisplay


class ActionLogState(rx.State):
    """Manages the action log list and detail view."""

    entries: list[ActionLogDisplay] = []
    selected_entry: ActionLogDisplay | None = None
    search_value: str = ""

    def load_entries(self) -> None:
        """Load all action log entries, newest first."""
        with rx.session() as session:
            query = select(ActionLogModel).order_by(col(ActionLogModel.created).desc())
            if self.search_value:
                pattern = f"%{self.search_value}%"
                query = query.where(
                    col(ActionLogModel.username).ilike(pattern)
                    | col(ActionLogModel.action).ilike(pattern)
                    | col(ActionLogModel.entity_type).ilike(pattern)
                    | col(ActionLogModel.entity_name).ilike(pattern)
                )
            rows = session.exec(query).all()
            self.entries = [
                ActionLogDisplay(
                    log_id=r.id,
                    user_id=r.user_id,
                    username=r.username,
                    action=r.action,
                    entity_type=r.entity_type,
                    entity_name=r.entity_name,
                    detail=r.detail,
                    created=r.created,
                )
                for r in rows
            ]
        self.selected_entry = None

    def select_entry(self, log_id: int) -> None:
        """Select an entry by its log id to show in the detail panel."""
        for entry in self.entries:
            if entry.log_id == log_id:
                self.selected_entry = entry
                return
        self.selected_entry = None

    def clear_selection(self) -> None:
        """Clear the selected entry."""
        self.selected_entry = None

    def filter_entries(self, value: str) -> None:
        """Update search value and reload entries."""
        self.search_value = value
        self.load_entries()
