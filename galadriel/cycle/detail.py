"""Test cycle detail page with child management."""

import reflex as rx
from ..navigation import routes
from . import state
from .. pages import base_page
from ..ui.components import Badge, Table, Button, MomentBadge, Moment, SearchTable
from . import model
from ..suite.model import SuiteModel
from ..case.model import CaseModel
from ..scenario.model import ScenarioModel
from ..utils import consts

from ..auth.state import require_login, Session

def __search_table_header():
    return SearchTable().header()

def __show_test_cases_in_search(test_case:CaseModel):
    moment_component = Moment()

    return rx.table.row(
            rx.table.cell(rx.button(rx.icon("plus"), on_click=lambda: state.CycleState.link_case(getattr(test_case, consts.FIELD_ID)))),
            rx.table.cell(test_case.name),
            rx.table.cell(moment_component.moment(test_case.created)),
            rx.table.cell(rx.form(rx.input(name="case_id", value=rx.cond(test_case.id, test_case.id, ""))), hidden=True),
    )

def __search_cases_table() -> rx.Component:
    return rx.fragment(
        rx.form(
            rx.table.root(
                __search_table_header(),
                rx.table.body(rx.foreach(state.CycleState.cases_for_search, __show_test_cases_in_search)),
                variant="surface",
                size="3",
                width="100%",
                on_mount=state.CycleState.load_cases_for_search,
            ),
        ),
    )

def __show_scenarios_in_search(scenario:ScenarioModel):
    moment_component = Moment()

    return rx.table.row(
            rx.table.cell(rx.button(rx.icon("plus"), on_click=lambda: state.CycleState.link_scenario(getattr(scenario, consts.FIELD_ID)))),
            rx.table.cell(scenario.name),
            rx.table.cell(moment_component.moment(scenario.created)),
            rx.table.cell(rx.form(rx.input(name="scenario_id", value=rx.cond(scenario.id, scenario.id, ""))), hidden=True),
    )

def __search_scenarios_table() -> rx.Component:
    return rx.fragment(
        rx.form(
            rx.table.root(
                __search_table_header(),
                rx.table.body(rx.foreach(state.CycleState.scenarios_for_search, __show_scenarios_in_search)),
                variant="surface",
                size="3",
                width="100%",
                on_mount=state.CycleState.load_scenarios_for_search,
            ),
        ),
    )

def __show_suites_in_search(suite:SuiteModel):
    moment_component = Moment()

    return rx.table.row(
            rx.table.cell(rx.button(rx.icon("plus"), on_click=lambda: state.CycleState.link_suite(getattr(suite, consts.FIELD_ID)))),
            rx.table.cell(suite.name),
            rx.table.cell(moment_component.moment(suite.created)),
            rx.table.cell(rx.form(rx.input(name="suite_id", value=rx.cond(suite.id, suite.id, ""))), hidden=True),
    )

def __search_suites_table() -> rx.Component:
    return rx.fragment(
        rx.form(
            rx.table.root(
                __search_table_header(),
                rx.table.body(rx.foreach(state.CycleState.suites_for_search, __show_suites_in_search)),
                variant="surface",
                size="3",
                width="100%",
                on_mount=state.CycleState.load_suites_for_search,
            ),
        ),
    )

def __child_type_badge(child_type: str):
    badge_mapping = {
        "Suite": ("beaker", "Suite"),
        "Scenario": ("route", "Scenario"),
        "Case": (consts.ICON_TEST_TUBES, "Case")
    }
    return SearchTable.badge_with_icon(*badge_mapping.get(child_type, ("circle-help", "Not Found")))

def __show_child(cycle_child:model.CycleChildModel):
    DISABLE_EDIT_MODE = ~Session.can_edit

    return rx.table.row(
        rx.table.cell(cycle_child.order),
        rx.table.cell(rx.match(
            cycle_child.child_type_id,
            (1, __child_type_badge("Suite")),
            (2, __child_type_badge("Scenario")),
            (3, __child_type_badge("Case"))
        )),
        rx.table.cell(cycle_child.child_name),
        rx.table.cell(
            rx.flex(
                rx.button(rx.icon("arrow-big-up"), disabled=rx.cond(DISABLE_EDIT_MODE, DISABLE_EDIT_MODE, state.CycleState.has_iteration | (cycle_child.order == 1)), on_click=lambda: state.CycleState.move_child_up(getattr(cycle_child, consts.FIELD_ID))),  # NOSONAR - Reflex event handler; self is implicit
                rx.button(rx.icon("arrow-big-down"), disabled=rx.cond(DISABLE_EDIT_MODE, DISABLE_EDIT_MODE, state.CycleState.has_iteration | (cycle_child.order == state.CycleState.child_count)), on_click=lambda: state.CycleState.move_child_down(getattr(cycle_child, consts.FIELD_ID))),  # NOSONAR
                rx.button(rx.icon("trash-2"), color_scheme="red", disabled=rx.cond(DISABLE_EDIT_MODE,DISABLE_EDIT_MODE, state.CycleState.has_iteration), on_click=lambda: state.CycleState.unlink_child(getattr(cycle_child, consts.FIELD_ID))),  # NOSONAR
                spacing="2",
            )
        ),
    )

def __cycle_children_table() -> rx.Component:
    table_component = Table()
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    table_component.header("order", "list-ordered"),
                    table_component.header("type","blocks"),
                    table_component.header("name", "tag"),
                    table_component.header("", "ellipsis"),
                ),
            ),
            rx.table.body(rx.foreach(state.CycleState.children, __show_child)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.CycleState.load_children,
        ),
    )

@require_login
def cycle_detail_page() -> rx.Component:
    """Render the test cycle detail page."""
    DISABLE_EDIT_MODE = ~Session.can_edit

    title_badge = Badge()
    button_component = Button()
    moment_badge_component = MomentBadge()

    edit_link_element = rx.cond(
        DISABLE_EDIT_MODE,
        rx.fragment(""),
        button_component.edit(state.CycleState.cycle_edit_url, disabled=state.CycleState.has_iteration)
    )

    cycle_detail_content = rx.vstack(
        rx.flex(
            title_badge.title("beaker", "Test Cycle Detail"),
            rx.spacer(),
            rx.hstack(button_component.to_list("to Cycles", routes.CYCLES), edit_link_element),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",
        ),
        rx.hstack(
            rx.heading(
                f"{state.CycleState.cycle.name}",
                size="7",
            ),
            rx.cond(
                state.CycleState.iteration_status_name,
                rx.match(
                    state.CycleState.iteration_status_name,
                    (consts.STATUS_EXECUTION_IN_PROGRESS, rx.badge(rx.icon("activity"), consts.STATUS_EXECUTION_IN_PROGRESS, color_scheme="blue")),
                    (consts.STATUS_EXECUTION_CLOSED, rx.badge(rx.icon("activity"), consts.STATUS_EXECUTION_CLOSED, color_scheme="red")),
                    (consts.STATUS_EXECUTION_COMPLETED, rx.badge(rx.icon("activity"), consts.STATUS_EXECUTION_COMPLETED, color_scheme="green")),
                    (consts.STATUS_EXECUTION_ON_HOLD, rx.badge(rx.icon("activity"), consts.STATUS_EXECUTION_ON_HOLD, color_scheme="yellow")),
                    (consts.STATUS_EXECUTION_COMPLETED_FAILED, rx.badge(rx.icon("activity"), consts.STATUS_EXECUTION_COMPLETED_FAILED, color_scheme="orange")),
                    (consts.STATUS_EXECUTION_NOT_STARTED, rx.badge(rx.icon("activity"), consts.STATUS_EXECUTION_NOT_STARTED)),
                    rx.badge(rx.icon("activity"), state.CycleState.iteration_status_name),
                ),
            ),
            rx.badge(rx.icon("gauge"), f"{state.CycleState.cycle.threshold}", color_scheme="lime"),
            moment_badge_component.moment_badge(state.CycleState.cycle.created),
            align="center",
        ),
        __cycle_children_table(),
        rx.cond(
            state.CycleState.has_iteration,
            rx.fragment(""),
            rx.fragment(
                rx.vstack(
                    rx.hstack(
                        rx.icon("beaker"),
                        rx.heading("Suites", size="5",),
                        rx.button(rx.icon("search", size=18), disabled=DISABLE_EDIT_MODE, on_click=state.CycleState.toggle_suite_search),
                        align="center"
                    ),
                    rx.cond(
                        state.CycleState.show_suite_search,
                        rx.box(
                            rx.box(rx.input(type="hidden", name="cycle_id", value=state.CycleState.cycle_id), display="none",),
                            rx.vstack(
                                rx.input(placeholder="start typing to search a Suite to add to the Cycle", width="77vw", on_change=lambda value: state.CycleState.filter_suites(value)),
                                __search_suites_table(),
                            ),
                        ),
                    ),
                    ),
                rx.vstack(
                    rx.hstack(
                        rx.icon("route"),
                        rx.heading("Scenarios", size="5",),
                        rx.button(rx.icon("search", size=18), disabled=DISABLE_EDIT_MODE, on_click=state.CycleState.toggle_scenario_search),
                        align="center"
                    ),
                    rx.cond(
                        state.CycleState.show_scenario_search,
                        rx.box(
                                rx.box(rx.input(type="hidden", name="cycle_id", value=state.CycleState.cycle_id), display="none",),
                                rx.vstack(
                                    rx.input(placeholder="start typing to search a Scenario to add to the Cycle", width="77vw", on_change=lambda value: state.CycleState.filter_scenarios(value)),
                                    __search_scenarios_table(),
                                ),
                            ),
                    ),
                ),
                rx.vstack(
                    rx.hstack(
                        rx.icon(consts.ICON_TEST_TUBES),
                        rx.heading("Cases", size="5",),
                        rx.button(rx.icon("search", size=18), disabled=DISABLE_EDIT_MODE, on_click=state.CycleState.toggle_case_search),
                        align="center"
                    ),
                    rx.cond(
                        state.CycleState.show_case_search,
                        rx.box(
                                rx.box(rx.input(type="hidden", name="cycle_id", value=state.CycleState.cycle_id), display="none",),
                                rx.vstack(
                                    rx.input(placeholder="start typing to search a Test Case to add to the Cycle", width="77vw", on_change=lambda value: state.CycleState.filter_test_cases(value)),
                                    __search_cases_table(),
                                ),
                            ),
                    ),
                ),
            ),
        ),
        spacing="5",
        align="start",
        min_height= consts.RELATIVE_VIEWPORT_85,
    ),
    
    return base_page(cycle_detail_content)