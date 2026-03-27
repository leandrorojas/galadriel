"""Action log page — list + detail layout."""

import reflex as rx

from ..pages import base_page
from ..ui.components import Badge, Table, Moment
from ..utils import consts
from ..auth.state import require_super_admin
from .state import ActionLogState


def __entry_row(entry) -> rx.Component:
    """Render a single action log row in the list."""
    moment_component = Moment()
    return rx.table.row(
        rx.table.cell(entry.username),
        rx.table.cell(entry.action),
        rx.table.cell(entry.entity_type),
        rx.table.cell(entry.entity_name),
        rx.table.cell(moment_component.moment(entry.created)),
        cursor="pointer",
        on_click=ActionLogState.select_entry(entry.log_id),
        _hover={"bg": rx.color("accent", 3)},
    )


def __entry_table() -> rx.Component:
    """Render the action log table."""
    table_component = Table()
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    table_component.header("user", "user"),
                    table_component.header("action", "activity"),
                    table_component.header("type", "layers"),
                    table_component.header("name", "tag"),
                    table_component.header("date", "calendar-clock"),
                ),
            ),
            rx.table.body(
                rx.foreach(ActionLogState.entries, __entry_row),
            ),
            variant="surface",
            size="3",
            width="100%",
        ),
        class_name="sticky-table",
        overflow_y="auto",
        flex="1",
        min_height="0",
        width="100%",
    )


def __detail_panel() -> rx.Component:
    """Render the detail panel for the selected entry."""
    entry = ActionLogState.selected_entry
    moment_component = Moment()
    return rx.cond(
        entry,
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Action Detail", size="4"),
                    rx.spacer(),
                    rx.icon(
                        "x",
                        cursor="pointer",
                        on_click=ActionLogState.clear_selection,
                    ),
                    width="100%",
                    align="center",
                ),
                rx.divider(),
                rx.vstack(
                    __detail_field("User", entry.username),
                    __detail_field("Action", entry.action),
                    __detail_field("Entity Type", entry.entity_type),
                    __detail_field("Entity Name", entry.entity_name),
                    __detail_field("Date", moment_component.moment(entry.created)),
                    rx.cond(
                        entry.detail,
                        rx.vstack(
                            rx.text("Detail", weight="bold", size="2", color=consts.COLOR_MUTED),
                            rx.text(entry.detail, size="2"),
                            spacing="1",
                            width="100%",
                        ),
                    ),
                    spacing="3",
                    width="100%",
                ),
                spacing="3",
                width="100%",
            ),
            width="100%",
        ),
        rx.center(
            rx.text("Select an entry to view details", color=consts.COLOR_MUTED),
            min_height="200px",
            width="100%",
        ),
    )


def __detail_field(label: str, value) -> rx.Component:
    """Render a label-value pair in the detail panel."""
    return rx.hstack(
        rx.text(label, weight="bold", size="2", color=consts.COLOR_MUTED, min_width="100px"),
        rx.text(value, size="2"),
        spacing="2",
        width="100%",
    )


@require_super_admin
def action_log_page() -> rx.Component:
    """Render the action log page with list + detail layout."""
    page_title = Badge()

    return base_page(
        rx.vstack(
            rx.flex(
                page_title.title("scroll-text", "Action Log"),
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
            rx.input(
                rx.input.slot(rx.icon("search", size=16)),
                placeholder="Search by user, action, type, or name...",
                value=ActionLogState.search_value,
                on_change=ActionLogState.filter_entries,
                size="2",
                width="100%",
            ),
            rx.flex(
                rx.box(
                    __entry_table(),
                    flex="2",
                ),
                rx.box(
                    __detail_panel(),
                    flex="1",
                ),
                direction="row",
                spacing="4",
                width="100%",
                height="100%",
            ),
            spacing="5",
            align="center",
            width="100%",
            height="100%",
        ),
    )
