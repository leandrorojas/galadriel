import reflex as rx
import reflex_local_auth

from ..pages import base_page
from ..navigation import routes
from ..ui.components import Badge, Tooltip
from .state import CycleState
from ..iteration import IterationSnapshotModel

READ_ONLY = False

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

def __force_close_iteration_snapshot_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("square", size=26), 
                rx.text("Close", size="4", display=["none", "none", "block"]), 
                size="3",
                variant="soft",
                color_scheme="red",
                disabled=READ_ONLY,
                on_click=lambda: CycleState.set_iteration_execution_status_closed(CycleState.iteration_id),
            ),
            
            href=routes.CYCLES
        ), 
    )

def __hold_iteration_snapshot_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("pause", size=26), 
                rx.text("Pause", size="4", display=["none", "none", "block"]), 
                size="3",
                variant="soft",
                color_scheme="yellow",
                disabled=READ_ONLY,
                on_click=lambda: CycleState.set_iteration_execution_status_on_hold(CycleState.iteration_id),
            ),
            
            href=routes.CYCLES
        ), 
    )

def __header_cell(text: str, icon: str, hide_column:bool = False, info_tooltip:str = ""):
    title_tooltip = Tooltip()

    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            rx.cond(info_tooltip == "", rx.text(""), title_tooltip.info(info_tooltip)),
            align="center",
            spacing="2",
        ),
        hidden=hide_column,
    )

def __badge(icon: str, text: str, color=""):
    if (color == ""):
        return rx.badge(rx.icon(icon, size=16), text, radius="full", variant="soft", size="3")
    else:
        return rx.badge(rx.icon(icon, size=16), text, radius="full", variant="soft", size="3", color_scheme=color)

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
        "To Do": ("circle-help", "To Do", "blue"),
        "Failed": ("x", "Failed", "red"),
        "Passed": ("check", "Passed", "green"),
        "Skipped": ("list-x", "Skipped", "gray"),
        "Blocked": ("cuboid", "Blocked", "gray") #also brick-wall
    }
    return __badge(*badge_mapping.get(child_status, ("circle-help", "Not Found")))

def __show_snapshot_element(snapshot_element:IterationSnapshotModel):
    return rx.table.row(
        # rx.table.cell(rx.match(
        #     snapshot_element.child_type,
        #     (1, __element_type_badge("Suite")),
        #     (2, __element_type_badge("Scenario")),
        #     (3, __element_type_badge("Case")),
        #     (4, __element_type_badge("Step"))
        # )),
        rx.table.cell(rx.cond(snapshot_element.child_name != None, snapshot_element.child_name + " ", ""),
        rx.match(
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
            (1, __element_status_badge("To Do")),
            (2, __element_status_badge("Failed")),
            (3, __element_status_badge("Passed")),
            (4, __element_status_badge("Skipped")),
            (5, __element_status_badge("Blocked")),
        )),
        rx.table.cell(
            rx.cond(
                snapshot_element.child_type == 4,
                rx.flex(
                    rx.button(rx.icon("check"), color_scheme="green", size="1", disabled=READ_ONLY, on_click=lambda: CycleState.pass_iteration_snapshot_step(getattr(snapshot_element, "id"))),
                    rx.button(rx.icon("x"), color_scheme="red", size="1", disabled=READ_ONLY, on_click=lambda: CycleState.fail_iteration_snapshot_step(getattr(snapshot_element, "id"))),
                    rx.button(rx.icon("list-x"), color_scheme="gray", size="1", disabled=READ_ONLY, on_click=lambda: CycleState.skip_iteration_snapshot_step(getattr(snapshot_element, "id"))),
                    spacing="2",
                ),
            ),
        ),
    )

@reflex_local_auth.require_login
def iteration_page() -> rx.Component:
    title_badge = Badge()

    global READ_ONLY
    READ_ONLY = ~CycleState.is_iteration_editable

    cycle_edit_content = rx.vstack(
        rx.flex(
            title_badge.title("iteration-ccw", f"Iteration for {CycleState.cycle_name}"),
            rx.spacer(),
            __hold_iteration_snapshot_button(),
            __force_close_iteration_snapshot_button(),
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
                            #__header_cell("type", "blocks"),
                            __header_cell("name/type", "tag",info_tooltip="[P]requisite"),
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