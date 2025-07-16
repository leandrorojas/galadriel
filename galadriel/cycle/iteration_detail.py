import reflex as rx
import reflex_local_auth

from ..pages import base_page
from ..navigation import routes
from ..ui.components import Badge, Table
from .state import CycleState
from ..iteration import IterationSnapshotModel
from ..utils import jira, consts

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

def __badge(icon: str, text: str, color=""):
    if (color == ""):
        return rx.badge(rx.icon(icon, size=16), text, radius="full", variant="soft", size="3")
    else:
        return rx.badge(rx.icon(icon, size=16), text, radius="full", variant="soft", size="3", color_scheme=color)

def __element_type_badge(child_type: str):
    badge_mapping = {
        "Suite": ("beaker", "Suite"),
        "Scenario": ("route", "Scenario"),
        "Case": (consts.ICON_TEST_TUBES, "Case"),
        "Step": ("test-tube", "Step"),
    }
    return __badge(*badge_mapping.get(child_type, ("circle-help", "Not Found")))

def __element_status_badge(child_status: str):
    badge_mapping = {
        consts.STATUS_EXECUTION_TO_DO: ("circle-help", consts.STATUS_EXECUTION_TO_DO, "blue"),
        "Failed": ("x", "Failed", "red"),
        "Passed": ("check", "Passed", "green"),
        "Skipped": ("list-x", "Skipped", "gray"),
        "Blocked": ("cuboid", "Blocked", "gray") 
    }
    return __badge(*badge_mapping.get(child_status, ("circle-help", "Not Found")))

def __show_snapshot_element(snapshot_element:IterationSnapshotModel):
    return rx.table.row(
        rx.table.cell(rx.cond(snapshot_element.child_name != None, snapshot_element.child_name + " ", ""),
        rx.match(
            snapshot_element.child_type,
            (1, __element_type_badge("Suite")),
            (2, __element_type_badge("Scenario")),
            (3, __element_type_badge("Case")) 
        )),
        rx.table.cell(snapshot_element.child_action),
        rx.table.cell(snapshot_element.child_expected),
        rx.table.cell(rx.match(
            snapshot_element.child_status_id,
            (1, __element_status_badge(consts.STATUS_EXECUTION_TO_DO)),
            (2, __element_status_badge("Failed")),
            (3, __element_status_badge("Passed")),
            (4, __element_status_badge("Skipped")),
            (5, __element_status_badge("Blocked")),
        )),
        rx.cond(
            snapshot_element.linked_issue != None,
            rx.table.cell(rx.link(snapshot_element.linked_issue, href=jira.get_issue_url(snapshot_element.linked_issue), is_external=True), rx.button(rx.icon("circle-minus", size=15), color_scheme="red", size="1", on_click= lambda: CycleState.unlink_issue_from_snapshot_step(getattr(snapshot_element, consts.FIELD_ID))), align="center"),
            rx.table.cell("")
        ),
        rx.table.cell(
            rx.cond(
                snapshot_element.child_type == 4,
                rx.flex(
                    rx.button(rx.icon("check"), color_scheme="green", size="1", disabled=READ_ONLY, on_click=lambda: CycleState.pass_iteration_snapshot_step(getattr(snapshot_element, consts.FIELD_ID))),
                    rx.cond(
                        snapshot_element.linked_issue == None,
                        rx.dialog.root(
                            rx.dialog.trigger(rx.button(rx.icon("x"), color_scheme="red", size="1", disabled=READ_ONLY),), 
                            rx.dialog.content(
                                rx.hstack(rx.badge(rx.icon("bug", size=34), color_scheme="crimson", radius="full", padding="0.65rem",), rx.vstack(rx.dialog.title("Add New Issue", weight="bold", margin="0",), rx.dialog.description("Additional info will be auto-included in the report description", spacing="1", height="100%", align_items="start",),), height="100%", spacing="4", margin_bottom="1.5em", align_items="center", width="100%",),
                                rx.flex(
                                    rx.form.root(
                                        rx.flex(
                                            rx.vstack(
                                                rx.box(rx.input(type="hidden",name="snapshot_item_id", value=snapshot_element.id),display="none",),
                                                rx.box(rx.checkbox(type="hidden",name="just_fail", checked=CycleState.fail_checkbox),display="none",),
                                                rx.input(name="summary", placeholder="Summary", width="100%", default_value=f"{snapshot_element.child_action} is failing"),
                                                rx.input(name="actual", placeholder="Actual Result", width="100%",),
                                                rx.input(name="expected", placeholder="Expected Result", width="100%", default_value=f"{snapshot_element.child_expected}"),
                                            ), direction="column", spacing="3",
                                        ),
                                        rx.flex(
                                            rx.dialog.close(rx.button("Cancel", variant="soft", color_scheme="gray",),),
                                            rx.dialog.close(rx.button("Fail Case", color_scheme="gray", on_click=CycleState.turn_on_fail_checkbox)),
                                            rx.form.submit(rx.dialog.close(rx.button("Fail Case & Create Issue", type="submit", on_click=CycleState.turn_off_fail_checkbox,),),as_child=True,),
                                            padding_top="2em", spacing="3", mt="4", justify="end",
                                        ), reset_on_submit=False, on_submit=CycleState.fail_iteration_snapshot_step_and_create_issue,), width="100%", direction="column", spacing="4",
                                ), max_width="450px", padding="1.5em", border=f"2px solid {rx.color('accent', 7)}", border_radius="25px",
                            ),
                        ),
                        rx.button(rx.icon("x"), color_scheme="red", size="1", disabled=True),
                    ),
                    rx.button(rx.icon("list-x"), color_scheme="gray", size="1", disabled=READ_ONLY, on_click=lambda: CycleState.skip_iteration_snapshot_step(getattr(snapshot_element, consts.FIELD_ID))),
                    spacing="2",
                ),
            ),
        ),
    )

@reflex_local_auth.require_login
def iteration_page() -> rx.Component:
    title_badge = Badge()
    table_component = Table()

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
                            table_component.header("name/type", "tag",info_tooltip="[P]requisite"),
                            table_component.header("action", "pickaxe"),
                            table_component.header("expected", "gem"),
                            table_component.header("status", "activity"),
                            table_component.header("issue", "bug"),
                            table_component.header("", "ellipsis"),
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
            style={"height": consts.RELATIVE_VIEWPORT_85},
        ),
        spacing="5",
        align="center",
        min_height="95vh",
    ),
    
    return base_page(cycle_edit_content)