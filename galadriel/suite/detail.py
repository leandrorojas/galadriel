import reflex as rx
import reflex_local_auth

from ..navigation import routes
from . import state
from .. pages import base_page
from ..ui.components import Badge
from . import model
from ..case.model import CaseModel
from ..scenario.model import ScenarioModel

def __suite_list_button():
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevron-left", size=26), 
                rx.text("to Suites", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.SUITES
        ), 
    )

def __suite_edit_button():
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("pencil", size=26), 
                rx.text("Edit", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=state.SuiteState.suite_edit_url
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

def __show_test_cases_in_search(test_case:CaseModel):
    return rx.table.row(
            rx.table.cell(rx.button(rx.icon("plus"), on_click=lambda: state.SuiteState.link_case(getattr(test_case, "id")))),
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
                rx.table.body(rx.foreach(state.SuiteState.cases_for_search, __show_test_cases_in_search)),
                variant="surface",
                size="3",
                width="100%",
                on_mount=state.SuiteState.load_cases_for_search,
            ),
        ),
    )

def __show_scenarios_in_search(scenario:ScenarioModel):
    return rx.table.row(
            rx.table.cell(rx.button(rx.icon("plus"), on_click=lambda: state.SuiteState.link_scenario(getattr(scenario, "id")))),
            rx.table.cell(scenario.name),
            rx.table.cell(scenario.created),
            rx.table.cell(rx.form(rx.input(name="scenario_id", value=scenario.id)), hidden=True),
    )

def __search_scenarios_table() -> rx.Component:
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
                rx.table.body(rx.foreach(state.SuiteState.scenarios_for_search, __show_scenarios_in_search)),
                variant="surface",
                size="3",
                width="100%",
                on_mount=state.SuiteState.load_scenarios_for_search,
            ),
        ),
    )

def __badge(icon: str, text: str):
    return rx.badge(rx.icon(icon, size=16), text, radius="full", variant="soft", size="3")

def __child_type_badge(child_type: str):
    badge_mapping = {
        "Scenario": ("route", "Scenario"),
        "Case": ("test-tubes", "Case")
    }
    return __badge(*badge_mapping.get(child_type, ("circle-help", "Not Found")))

def __show_child(suite_child:model.SuiteChildModel):
    return rx.table.row(
        rx.table.cell(suite_child.order),
        rx.table.cell(rx.match(
            suite_child.child_type_id,
            (1, __child_type_badge("Scenario")),
            (2, __child_type_badge("Case"))
        )),
        rx.table.cell(suite_child.child_name),
        rx.table.cell(
            rx.flex(
                rx.button(rx.icon("arrow-big-up"), on_click=lambda: state.SuiteState.move_child_up(getattr(suite_child, "id"))), 
                rx.button(rx.icon("arrow-big-down"), on_click=lambda: state.SuiteState.move_child_down(getattr(suite_child, "id"))), 
                rx.button(rx.icon("trash-2"), color_scheme="red", on_click=lambda: state.SuiteState.unlink_child(getattr(suite_child, "id"))),
                spacing="2",
            )
        ),
    )

def __suite_children_table() -> rx.Component:
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    __header_cell("order", "list-ordered"),
                    __header_cell("type","blocks"),
                    __header_cell("name", "tag"),
                    __header_cell("", "ellipsis"),
                ),
            ),
            rx.table.body(rx.foreach(state.SuiteState.children, __show_child)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.SuiteState.load_children,
        ),
    )

@reflex_local_auth.require_login
def suite_detail_page() -> rx.Component:
    title_badge = Badge()
    can_edit = True #TODO: add roles and privileges
    edit_link = __suite_edit_button()

    edit_link_element = rx.cond(
        can_edit,
        edit_link,
        rx.fragment("")
    )

    suite_detail_content = rx.vstack(
        rx.flex(
            title_badge.title("beaker", "Test Suite Detail"),
            rx.spacer(),
            rx.hstack(__suite_list_button(), edit_link_element),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",       
        ),
        rx.hstack(
            rx.heading(
                f"{state.SuiteState.suite.name}",
                size="7",
            ),
            rx.badge(f"{state.SuiteState.suite.created}", variant="outline"),
            align="center",
        ),
        __suite_children_table(),
        rx.vstack(
            rx.hstack(
                rx.icon("route"),
                rx.heading("Scenarios", size="5",),
                rx.button(rx.icon("search", size=18), on_click=state.SuiteState.toggle_scenario_search),
                align="center"
            ),
            rx.cond(
                state.SuiteState.show_scenario_search,
                rx.box(
                        rx.box(rx.input(type="hidden", name="suite_id", value=state.SuiteState.id), display="none",),
                        rx.vstack(
                            rx.input(placeholder="start typing to search a Scenario to add to the Suite", width="77vw", on_change=lambda value: state.SuiteState.filter_scenarios(value)),
                            __search_scenarios_table(),
                        ),
                    ),
            ),
        ),
        rx.vstack(
            rx.hstack(
                rx.icon("test-tubes"),
                rx.heading("Cases", size="5",),
                rx.button(rx.icon("search", size=18), on_click=state.SuiteState.toggle_case_search),
                align="center"
            ),
            rx.cond(
                state.SuiteState.show_case_search,
                rx.box(
                        rx.box(rx.input(type="hidden", name="suite_id", value=state.SuiteState.id), display="none",),
                        rx.vstack(
                            rx.input(placeholder="start typing to search a Test Case to add to the Suite", width="77vw", on_change=lambda value: state.SuiteState.filter_test_cases(value)),
                            __search_cases_table(),
                        ),
                    ),
            ),
        ),
        spacing="5",
        align="start",
        min_height="85vh",
    ),
    
    return base_page(suite_detail_content)