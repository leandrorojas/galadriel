import reflex as rx

from ..navigation import routes
from . import state
from .. pages import base_page
from ..ui.components import Badge
from . import model
from ..case.model import CaseModel

def __scenario_list_button():
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevron-left", size=26), 
                rx.text("to Scenarios", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.SCENARIOS
        ), 
    )

def __scenario_edit_button(): 
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("pencil", size=26), 
                rx.text("Edit", size="4", display=["none", "none", "block"]),
                size="3", 
            ),
            href=routes.SCENARIO_EDIT
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

def __show_test_cases(test_cases:model.ScenarioCaseModel):
    return rx.table.row(
        rx.table.cell(test_cases.order),
        rx.table.cell(test_cases.case_name),
        rx.table.cell(
            rx.flex(
                rx.button(rx.icon("arrow-big-up")),#, on_click=lambda: state.CaseState.move_prerequisite_up(getattr(test_cases, "id"))), 
                rx.button(rx.icon("arrow-big-down")),#, on_click=lambda: state.CaseState.move_prerequisite_down(getattr(test_cases, "id"))), 
                rx.button(rx.icon("trash-2"), color_scheme="red"),#, on_click=lambda: state.CaseState.delete_prerequisite(getattr(test_cases, "id"))),
                spacing="2",
            )
        ),
    )

def __cases_table() -> rx.Component:
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    __header_cell("order", "list-ordered"),
                    __header_cell("test case", "pickaxe"),
                    __header_cell("", "ellipsis"),
                ),
            ),
            rx.table.body(rx.foreach(state.ScenarioState.test_cases, __show_test_cases)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.ScenarioState.load_test_cases,
        ),
    )

def __show_test_cases_in_search(test_case:CaseModel):

    return rx.table.row(
            rx.table.cell(rx.button(rx.icon("plus"), on_click=lambda: state.ScenarioState.link_test_case(getattr(test_case, "id")))),
            rx.table.cell(test_case.name),
            rx.table.cell(test_case.created),
            rx.table.cell(rx.form(rx.input(name="case_id", value=test_case.id)), hidden=True),
    )

def __search_cases_table() -> rx.Component:
    return rx.fragment(
        rx.form(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        __header_cell("", "ellipsis"),
                        __header_cell("name", "fingerprint"),
                        __header_cell("created", "calendar-check-2"),
                        __header_cell("selected_id", "search", True),
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

def scenario_detail_page() -> rx.Component:
    title_badge = Badge()
    scenario = state.AddScenarioState.scenario
    can_edit = True #TODO: add roles and privileges
    edit_link = __scenario_edit_button()

    edit_link_element = rx.cond(
        can_edit,
        edit_link,
        rx.fragment("") 
    )
    
    scenario_detail_content = rx.vstack(
        rx.flex(
            title_badge.title("route", "Test Scenario Detail"),
            rx.spacer(),
            rx.hstack(__scenario_list_button(), edit_link_element),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",       
        ),
        rx.hstack(
            rx.heading(
                f"{state.ScenarioState.scenario.name}",
                size="7",
            ),
            rx.badge(f"{state.ScenarioState.scenario.created}", variant="outline"),
            align="center",
        ),
        rx.vstack(
            rx.hstack(
                rx.heading("Cases", size="5",),
                rx.button(rx.icon("search", size=18), on_click=state.ScenarioState.toggle_search),
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
        align="left",
        min_height="85vh",
    ),
    
    return base_page(scenario_detail_content)