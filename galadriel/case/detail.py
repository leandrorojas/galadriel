import reflex as rx
import reflex_local_auth

from ..navigation import routes
from ..pages import base_page
from ..ui.components import Badge, Table, Button, Moment, MomentBadge
from . import model, state
from .forms import step_add_form    
from ..utils import consts
from ..auth.state import Session

DISABLE_EDIT_MODE:bool = True

first_row:bool = True
last_row:bool = False

#prerequisites
def __show_prerequisite(prerequisite:model.PrerequisiteModel):
    global DISABLE_EDIT_MODE
    return rx.table.row(
        rx.table.cell(prerequisite.order),
        rx.table.cell(prerequisite.prerequisite_name),
        rx.table.cell(
            rx.flex(
                rx.button(rx.icon("arrow-big-up"), disabled=DISABLE_EDIT_MODE, on_click=lambda: state.CaseState.move_prerequisite_up(getattr(prerequisite, consts.FIELD_ID))), 
                rx.button(rx.icon("arrow-big-down"), disabled=DISABLE_EDIT_MODE, on_click=lambda: state.CaseState.move_prerequisite_down(getattr(prerequisite, consts.FIELD_ID))), 
                rx.button(rx.icon("trash-2"), disabled=DISABLE_EDIT_MODE, color_scheme="red", on_click=lambda: state.CaseState.delete_prerequisite(getattr(prerequisite, consts.FIELD_ID))),
                spacing="2",
            )
        ),
    )

def __prerequisites_table() -> rx.Component:
    table_component = Table()
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    table_component.header("order", "list-ordered"),
                    table_component.header("test case", "pickaxe"),
                    table_component.header("", "ellipsis"),
                ),
            ),
            rx.table.body(rx.foreach(state.CaseState.prerequisites, __show_prerequisite)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.CaseState.load_prerequisites,
        ),
    )

def __show_case_as_prerequisite(prerequisite:model.CaseModel):
    moment_component = Moment()

    return rx.table.row(
            rx.table.cell(rx.button(rx.icon("plus"), on_click=lambda: state.CaseState.add_prerequisite(getattr(prerequisite, consts.FIELD_ID)))),
            rx.table.cell(prerequisite.name),
            rx.table.cell(moment_component.moment(prerequisite.created)),
            rx.table.cell(rx.form(rx.input(name="prerequisite_id", value=prerequisite.id, read_only=True)), hidden=True),
    )

def __search_prerequisites_table() -> rx.Component:
    table_component = Table()
    return rx.fragment(
        rx.form(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        table_component.header("", "ellipsis"),
                        table_component.header("name", "fingerprint"),
                        table_component.header("created", "calendar-check-2"),
                        table_component.header("selected_id", "search", True),
                    ),
                ),
                rx.table.body(rx.foreach(state.CaseState.cases, __show_case_as_prerequisite)),
                variant="surface",
                size="3",
                width="100%",
                on_mount=state.CaseState.load_cases,
            ),
        ),
    )

#steps
def __show_step(test_step:model.StepModel):
    global DISABLE_EDIT_MODE

    return rx.table.row(
        rx.table.cell(test_step.order),
        rx.table.cell(test_step.action),
        rx.table.cell(test_step.expected),
        rx.table.cell(
            rx.flex(
                rx.button(rx.icon("arrow-big-up"), disabled=DISABLE_EDIT_MODE, on_click=lambda: state.CaseState.move_step_up(getattr(test_step, consts.FIELD_ID))), 
                rx.button(rx.icon("arrow-big-down"), disabled=DISABLE_EDIT_MODE, on_click=lambda: state.CaseState.move_step_down(getattr(test_step, consts.FIELD_ID))),
                rx.button(rx.icon("trash-2"), disabled=DISABLE_EDIT_MODE, color_scheme="red", on_click=lambda: state.CaseState.delete_step(getattr(test_step, consts.FIELD_ID))),
                spacing="2",
            )
        ),
    )

def __steps_table() -> rx.Component:
    table_component = Table()
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    table_component.header("order", "list-ordered"),
                    table_component.header("action", "pickaxe"),
                    table_component.header("expected", "gem"),
                    table_component.header("", "ellipsis"),
                ),
            ),
            rx.table.body(rx.foreach(state.CaseState.steps, __show_step)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.CaseState.load_steps,
        ),
    )

@reflex_local_auth.require_login
def case_detail_page() -> rx.Component:
    title_badge = Badge()
    test_case = state.AddStepState.case
    button_component = Button()
    moment_badge_component = MomentBadge()

    global DISABLE_EDIT_MODE
    DISABLE_EDIT_MODE = ~Session.can_edit

    edit_link_element = rx.cond(
        DISABLE_EDIT_MODE,
        rx.fragment(""),
        button_component.edit(state.CaseState.case_edit_url),
    )

    case_detail_content = rx.vstack(
        rx.flex(
            title_badge.title(consts.ICON_TEST_TUBES, "Test Case Detail"),
            rx.spacer(),
            rx.hstack(button_component.to_list("to Cases", routes.CASES), edit_link_element),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",
        ),
        rx.hstack(
            rx.heading(f"{state.CaseState.case.name}", size="7",),
            #TODO: the tooltip is displayed in UTC, it should be displayed in local time
            moment_badge_component.moment_badge(str(state.CaseState.case.created)),
            align="center",
        ),
        rx.vstack(
            rx.hstack(
                rx.icon(consts.ICON_TEST_TUBES),
                rx.heading("Prerequisites", size="5",),
                rx.button(rx.icon("search", size=18), disabled=DISABLE_EDIT_MODE, on_click=state.CaseState.toggle_search),
                align="center"
            ),
            rx.cond(
                state.CaseState.show_search,
                rx.box(
                        rx.box(rx.input(type="hidden", name="case_id", value=test_case.id, read_only=True), display="none"),
                        rx.vstack(
                            rx.input(placeholder="start typing to search a Test Case to add as prerequisite", on_change=lambda value: state.CaseState.filter_cases(value), width="77vw"),
                            __search_prerequisites_table(),
                        ),
                    ),                   
                __prerequisites_table()
            ),
        ),
        rx.vstack(
            rx.hstack(rx.icon("test-tube"), rx.heading("Steps", size="5",)),
            step_add_form(DISABLE_EDIT_MODE),
            __steps_table(),
        ),
        spacing="5",
        align="start",
        min_height=consts.RELATIVE_VIEWPORT_85,
    ),
    
    return base_page(case_detail_content)