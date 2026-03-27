"""Settings state management."""

import reflex as rx
from ..utils import jira
from ..config.helpers import (
    get_setting, set_setting,
    JIRA_URL, JIRA_USER, JIRA_PROJECT, JIRA_ISSUE_TYPE, JIRA_DONE_STATUS,
)


class SettingsState(rx.State):
    """Handles settings page actions."""

    jira_checking: bool = False
    jira_editing: bool = False

    jira_url: str = ""
    jira_user: str = ""
    jira_project: str = ""
    jira_issue_type: str = ""
    jira_done_status: str = ""

    def load_jira_settings(self):
        """Load Jira settings from the database."""
        self.jira_url = get_setting(JIRA_URL)
        self.jira_user = get_setting(JIRA_USER)
        self.jira_project = get_setting(JIRA_PROJECT)
        self.jira_issue_type = get_setting(JIRA_ISSUE_TYPE)
        self.jira_done_status = get_setting(JIRA_DONE_STATUS)
        self.jira_editing = False

    def toggle_jira_editing(self):
        """Toggle between view and edit mode for Jira settings."""
        if self.jira_editing:
            self.load_jira_settings()
        self.jira_editing = not self.jira_editing

    def save_jira_settings(self):
        """Persist Jira settings to the database."""
        set_setting(JIRA_URL, self.jira_url)
        set_setting(JIRA_USER, self.jira_user)
        set_setting(JIRA_PROJECT, self.jira_project)
        set_setting(JIRA_ISSUE_TYPE, self.jira_issue_type)
        set_setting(JIRA_DONE_STATUS, self.jira_done_status)
        jira._client._session = None
        self.jira_editing = False
        return rx.toast.success("Jira settings saved")

    def check_jira_connection(self):
        """Test the Jira connection and show the result as a toast."""
        self.jira_checking = True
        yield
        try:
            success, message = jira.check_connection()
            if success:
                yield rx.toast.success(message)
            else:
                yield rx.toast.error(message)
        except Exception:
            yield rx.toast.error("Unexpected error while checking Jira connection")
        finally:
            self.jira_checking = False
