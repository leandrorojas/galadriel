"""Test scenario list, add, and edit pages."""

import reflex as rx
from . import state, model
from .forms import scenario_add_form, scenario_edit_form

from ..navigation import routes

from ..pages.add import add_page
from ..pages.edit import edit_page
from ..pages import base_page

from ..ui.components import Table, PageHeader, Moment
from ..utils import consts
from ..auth.state import require_login, require_editor, Session

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
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    Table.sortable_header("name", "fingerprint", "name", state.ScenarioState.sort_by, state.ScenarioState.sort_asc, state.ScenarioState.toggle_sort),
                    Table.sortable_header("created", "calendar-check-2", "created", state.ScenarioState.sort_by, state.ScenarioState.sort_asc, state.ScenarioState.toggle_sort),
                ),
                style={"position": "sticky", "top": "0", "z_index": "1", "background_color": "var(--color-background)"},
            ),
            rx.table.body(rx.foreach(state.ScenarioState.sorted_scenarios, __show_scenario)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.ScenarioState.load_scenarios,
        ),
        overflow_y="auto",
        flex="1",
        width="100%",
    )

@require_login
def scenarios_list_page() -> rx.Component:
    """Render the test scenarios list page."""
    header_component = PageHeader()

    return base_page(
        rx.vstack(
            header_component.list("Test Scenarios", "route", "Add Scenario", routes.SCENARIO_ADD, Session.can_edit, "Group of Test Cases executed in a specific order"),
            __table(),
            spacing="5", align="center", width="100%"
        ),
    )

@require_editor
def scenario_add_page() -> rx.Component:
    """Render the add test scenario page."""
    return add_page(scenario_add_form, "New Test Scenario", "route", "to Scenarios", routes.SCENARIOS)

@require_editor
def scenario_edit_page() -> rx.Component:
    """Render the edit test scenario page."""
    return edit_page(scenario_edit_form, "Edit Test Scenario", "route", "to Scenarios", "to Scenario Detail", routes.SCENARIOS, state.EditScenarioState.scenario_url)