import reflex as rx
import reflex_local_auth

from ..pages import base_page
from ..navigation import routes
from ..ui.components import Badge
from .state import CycleState
from ..iteration import IterationSnapshotModel

def __cycle_list_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevrons-left", size=26), 
                rx.text("to Cycles", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.CYCLES
        ), 
    )

def __header_cell(text: str, icon: str, hide_column:bool = False):
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
        hidden=hide_column,
    )

def __badge(icon: str, text: str):
    return rx.badge(rx.icon(icon, size=16), text, radius="full", variant="soft", size="3")

def __element_type_badge(child_type: str):
    badge_mapping = {
        "Suite": ("beaker", "Suite"),
        "Scenario": ("route", "Scenario"),
        "Case": ("test-tubes", "Case"),
        "Step": ("test-tube", "Step"),
    }
    return __badge(*badge_mapping.get(child_type, ("circle-help", "Not Found")))

def __element_status_badge(child_status: str):
    badge_mapping = {
        "Not Attempted": ("circle-help", "Not Attempted"),
        "Failed": ("x", "Failed"),
        "Passed": ("check", "Passed"),
    }
    return __badge(*badge_mapping.get(child_status, ("circle-help", "Not Found")))

def __show_snapshot_element(snapshot_element:IterationSnapshotModel):
    return rx.table.row(
        rx.table.cell(snapshot_element.child_name),
        rx.table.cell(rx.match(
            snapshot_element.child_type,
            (1, __element_type_badge("Suite")),
            (2, __element_type_badge("Scenario")),
            (3, __element_type_badge("Case")),
            (4, __element_type_badge("Step"))
        )),
        rx.table.cell(snapshot_element.child_action),
        rx.table.cell(snapshot_element.child_expected),
        rx.table.cell(rx.match(
            snapshot_element.child_status_id,
            (1, __element_status_badge("Not Attempted")),
            (2, __element_status_badge("Failed")),
            (3, __element_status_badge("Passed"))
        )),
        rx.table.cell(
            rx.cond(
                snapshot_element.child_type == 4,
                rx.flex(
                    rx.button(rx.icon("check"), color_scheme="green", on_click=lambda: CycleState.pass_iteration_step(getattr(snapshot_element, "id"))),
                    rx.button(rx.icon("x"), color_scheme="red", on_click=lambda: CycleState.fail_iteration_step(getattr(snapshot_element, "id"))),
                    spacing="2",
                ),
            ),
        ),
    )

@reflex_local_auth.require_login
def iteration_page() -> rx.Component:
    title_badge = Badge()

    cycle_edit_content = rx.vstack(
        rx.flex(
            title_badge.title("iteration-ccw", f"Iteration for {CycleState.cycle_name}"),
            rx.spacer(),
            __cycle_list_button(),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",
        ),
        rx.scroll_area(
            rx.fragment(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            __header_cell("name", "tag"),
                            __header_cell("type", "blocks"),
                            __header_cell("action", "pickaxe"),
                            __header_cell("expected", "gem"),
                            __header_cell("status", "activity"),
                            __header_cell("", "ellipsis"),
                        ),
                    ),
                    rx.table.body(rx.foreach(CycleState.iteration_snapshot_items, __show_snapshot_element)),
                    variant="surface",
                    size="3",
                    width="100%",
                    on_mount=CycleState.get_iteration_snapshot,
                ),
            ),
            type="hover",
            scrollbars="vertical",
            style={"height": "85vh"},
        ),
        spacing="5",
        align="center",
        min_height="95vh",
    ),
    
    return base_page(cycle_edit_content)