"""Helper functions for reading and writing application settings."""

import reflex as rx
from .model import ConfigModel

# Jira setting keys
JIRA_URL = "jira_url"
JIRA_USER = "jira_user"
JIRA_PROJECT = "jira_project"
JIRA_ISSUE_TYPE = "jira_issue_type"
JIRA_DONE_STATUS = "jira_done_status"


def get_setting(name: str, default: str = "") -> str:
    """Read a setting value from the database, returning default if not found."""
    with rx.session() as session:
        row = session.exec(
            ConfigModel.select().where(ConfigModel.name == name)
        ).one_or_none()
        if row is None:
            return default
        return row.value


def set_setting(name: str, value: str) -> None:
    """Create or update a setting in the database."""
    with rx.session() as session:
        row = session.exec(
            ConfigModel.select().where(ConfigModel.name == name)
        ).one_or_none()
        if row is None:
            session.add(ConfigModel(name=name, value=value))
        else:
            row.value = value
        session.commit()
