import reflex as rx
import reflex_local_auth

from . import state, model
from .forms import scenario_add_form, scenario_edit_form

from ..navigation import routes

from ..pages.add import add_page
from ..pages.edit import edit_page
from ..pages import base_page

from ..ui.components import Table, PageHeader, Moment
from ..utils import consts
from ..auth.state import Session

def __scenario_detail_link(child: rx.Component, scenario: model.ScenarioModel):
    if scenario is None: return rx.fragment(child)
    
    scenario_id = scenario.id

    if scenario_id is None: return rx.fragment(child)

    root_path = routes.SCENARIOS
    scenario_detail_url = f"{root_path}/{scenario_id}"

    return rx.link(child, href=scenario_detail_url)

def __show_scenario(scenario:model.ScenarioModel):
    moment_component = Moment()
    return rx.table.row(
         rx.table.cell(__scenario_detail_link(scenario.name, scenario)),
         rx.table.cell(moment_component.moment(scenario.created)),
    )

def __table() -> rx.Component:
    table_component = Table()
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    table_component.header("name", "fingerprint"),
                    table_component.header("created", "calendar-check-2"),
                ),
            ),
            rx.table.body(rx.foreach(state.ScenarioState.scenarios, __show_scenario)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.ScenarioState.load_scenarios,
        ),
    )

@reflex_local_auth.require_login
def scenarios_list_page() -> rx.Component:
    header_component = PageHeader()

    return base_page(
        rx.vstack(
            header_component.list("Test Scenarios", "route", "Add Scenario", routes.SCENARIO_ADD, Session.can_edit, "Group of Test Cases executed in a specific order"),
            rx.scroll_area(__table(), type="hover", scrollbars="vertical", style={"height": consts.RELATIVE_VIEWPORT_85},),
            spacing="5", align="center", min_height=consts.RELATIVE_VIEWPORT_85
        ),
    )

@reflex_local_auth.require_login
def scenario_add_page() -> rx.Component:
    return add_page(scenario_add_form, "New Test Scenario", "route", "to Scenarios", routes.SCENARIOS)

@reflex_local_auth.require_login
def scenario_edit_page() -> rx.Component:
    return edit_page(scenario_edit_form, "Edit Test Scenario", "route", "to Scenarios", "to Scenario Detail", routes.SCENARIOS, state.EditScenarioState.scenario_url)