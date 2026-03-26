"""Settings state management."""

import reflex as rx
from ..utils import jira


class SettingsState(rx.State):
    """Handles settings page actions."""

    jira_checking: bool = False

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
