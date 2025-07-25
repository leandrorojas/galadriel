import reflex as rx
import reflex_local_auth

from ..navigation import routes
from . import state
from .. pages import base_page
from ..ui.components import Badge, Table, Button, MomentBadge, Moment
from . import model
from ..case.model import CaseModel
from ..utils import consts
from ..auth.state import Session

DISABLE_EDIT_MODE:bool = True

def __show_test_cases(test_cases:model.ScenarioCaseModel):
    global DISABLE_EDIT_MODE

    return rx.table.row(
        rx.table.cell(test_cases.order),
        rx.table.cell(test_cases.case_name),
        rx.table.cell(
            rx.flex(
                rx.button(rx.icon("arrow-big-up"), disabled=DISABLE_EDIT_MODE, on_click=lambda: state.ScenarioState.move_case_up(getattr(test_cases, consts.FIELD_ID))), 
                rx.button(rx.icon("arrow-big-down"), disabled=DISABLE_EDIT_MODE, on_click=lambda: state.ScenarioState.move_case_down(getattr(test_cases, consts.FIELD_ID))), 
                rx.button(rx.icon("trash-2"), disabled=DISABLE_EDIT_MODE, color_scheme="red", on_click=lambda: state.ScenarioState.unlink_case(getattr(test_cases, consts.FIELD_ID))),
                spacing="2",
            )
        ),
    )

def __cases_table() -> rx.Component:
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
            rx.table.body(rx.foreach(state.ScenarioState.test_cases, __show_test_cases)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.ScenarioState.load_cases,
        ),
    )

def __show_test_cases_in_search(test_case:CaseModel):
    moment_component = Moment()

    return rx.table.row(
            rx.table.cell(rx.button(rx.icon("plus"), on_click=lambda: state.ScenarioState.link_case(getattr(test_case, consts.FIELD_ID)))),
            rx.table.cell(test_case.name),
            rx.table.cell(moment_component.moment(test_case.created)),
            rx.table.cell(rx.form(rx.input(name="case_id", value=test_case.id)), hidden=True),
    )

def __search_cases_table() -> rx.Component:
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
                rx.table.body(rx.foreach(state.ScenarioState.test_cases_for_search, __show_test_cases_in_search)),
                variant="surface",
                size="3",
                width="100%",
                on_mount=state.ScenarioState.load_cases_for_search,
            ),
        ),
    )

@reflex_local_auth.require_login
def scenario_detail_page() -> rx.Component:
    global DISABLE_EDIT_MODE
    DISABLE_EDIT_MODE = ~Session.can_edit

    title_badge = Badge()
    scenario = state.AddScenarioState.scenario
    button_component = Button()
    moment_badge_component = MomentBadge()

    edit_link_element = rx.cond(
        DISABLE_EDIT_MODE,
        rx.fragment(""),
        button_component.edit(state.ScenarioState.scenario_edit_url)
    )
    
    scenario_detail_content = rx.vstack(
        rx.flex(
            title_badge.title("route", "Test Scenario Detail"),
            rx.spacer(),
            rx.hstack(button_component.to_list("to Scenarios", routes.SCENARIOS), edit_link_element),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",       
        ),
        rx.hstack(
            rx.heading(f"{state.ScenarioState.scenario.name}", size="7",),
            moment_badge_component.moment_badge(state.ScenarioState.scenario.created),
            align="center",
        ),
        rx.vstack(
            rx.hstack(
                rx.icon(consts.ICON_TEST_TUBES),
                rx.heading("Cases", size="5",),
                rx.button(rx.icon("search", size=18), disabled=DISABLE_EDIT_MODE, on_click=state.ScenarioState.toggle_search),
                align="center"
            ),
            rx.cond(
                state.ScenarioState.show_search,
                rx.box(
                        rx.box(rx.input(type="hidden", name="scenario_id", value=scenario.id), display="none",),
                        rx.vstack(
                            rx.input(placeholder="start typing to search a Test Case to add to the Scenario", width="77vw", on_change=lambda value: state.ScenarioState.filter_test_cases(value)),
                            __search_cases_table(),
                        ),
                    ),
                __cases_table()
            ),
        ),
        spacing="5",
        align="start",
        min_height=consts.RELATIVE_VIEWPORT_85,
    ),
    
    return base_page(scenario_detail_content)