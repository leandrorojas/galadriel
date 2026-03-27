"""Helper functions for logging user actions."""

import reflex as rx

from .model import ActionLogModel


def log_action(
    user_id: int,
    username: str,
    action: str,
    entity_type: str = "",
    entity_name: str = "",
    detail: str = "",
) -> None:
    """Record a user action in the audit log."""
    with rx.session() as session:
        entry = ActionLogModel(
            user_id=user_id,
            username=username,
            action=action,
            entity_type=entity_type,
            entity_name=entity_name,
            detail=detail,
        )
        session.add(entry)
        session.commit()
