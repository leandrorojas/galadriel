"""Settings page for application configuration (admin-only)."""

import reflex as rx

from ..pages import base_page
from ..ui.components import Badge
from ..auth.state import require_super_admin
from .state import SettingsState


def __setting_row(name: str, description: str, action: rx.Component) -> rx.Component:
    """Render a single settings row with name, description, and action."""
    return rx.table.row(
        rx.table.cell(
            rx.vstack(
                rx.text(name, weight="bold", size="3"),
                rx.text(description, size="2", color_scheme="gray"),
                spacing="1",
            ),
        ),
        rx.table.cell(
            action,
            align="right",
        ),
    )


def __config_field(label: str, value: rx.Var[str], on_change, editing: rx.Var[bool]) -> rx.Component:
    """Render a config field that switches between read-only text and input."""
    return rx.hstack(
        rx.text(label, weight="bold", size="2", min_width="8em"),
        rx.cond(
            editing,
            rx.input(value=value, on_change=on_change, size="2", width="100%"),
            rx.text(rx.cond(value, value, "—"), size="2", color_scheme="gray"),
        ),
        width="100%",
        align="center",
    )


def __jira_section() -> rx.Component:
    """Render the Jira configuration accordion section."""
    editing = SettingsState.jira_editing

    return rx.accordion.root(
        rx.accordion.item(
            header=rx.hstack(
                rx.icon("ticket", size=16),
                rx.text("Jira", weight="bold", size="3"),
                align="center",
                spacing="2",
            ),
            content=rx.vstack(
                __config_field("URL", SettingsState.jira_url, SettingsState.set_jira_url, editing),
                __config_field("User", SettingsState.jira_user, SettingsState.set_jira_user, editing),
                __config_field("Project", SettingsState.jira_project, SettingsState.set_jira_project, editing),
                __config_field("Issue type", SettingsState.jira_issue_type, SettingsState.set_jira_issue_type, editing),
                __config_field("Done status", SettingsState.jira_done_status, SettingsState.set_jira_done_status, editing),
                rx.separator(),
                rx.hstack(
                    rx.cond(
                        editing,
                        rx.hstack(
                            rx.button(
                                "Cancel",
                                on_click=SettingsState.toggle_jira_editing,
                                variant="soft",
                                size="2",
                            ),
                            rx.button(
                                rx.icon("save", size=16),
                                "Save",
                                on_click=SettingsState.save_jira_settings,
                                size="2",
                            ),
                            spacing="2",
                        ),
                        rx.button(
                            rx.icon("pencil", size=16),
                            "Edit",
                            on_click=SettingsState.toggle_jira_editing,
                            variant="outline",
                            size="2",
                        ),
                    ),
                    rx.spacer(),
                    rx.button(
                        rx.cond(
                            SettingsState.jira_checking,
                            rx.spinner(size="2"),
                            rx.icon("activity", size=16),
                        ),
                        "Check connection",
                        on_click=SettingsState.check_jira_connection,
                        loading=SettingsState.jira_checking,
                        variant="outline",
                        size="2",
                    ),
                    width="100%",
                ),
                spacing="3",
                width="100%",
                padding_y="0.5em",
            ),
            value="jira",
        ),
        variant="surface",
        width="100%",
        collapsible=True,
    )


@require_super_admin
def settings_page() -> rx.Component:
    """Render the settings page with configurable options."""
    page_title = Badge()

    return base_page(
        rx.vstack(
            rx.flex(
                page_title.title("settings", "Settings"),
                flex_direction=["column", "column", "row"],
                align="center",
                width="100%",
                padding_top="2em",
                padding_bottom="0.5em",
                position="sticky",
                top="0",
                z_index="3",
                background_color="var(--color-background)",
            ),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("Setting"),
                        rx.table.column_header_cell(""),
                    ),
                ),
                rx.table.body(
                    __setting_row(
                        "Dark mode",
                        "Toggle between light and dark theme",
                        rx.color_mode.switch(size="3"),
                    ),
                ),
                variant="surface",
                size="3",
                width="100%",
            ),
            __jira_section(),
            spacing="5",
            align="center",
            width="100%",
            height="100%",
        ),
    )
