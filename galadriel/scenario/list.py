import reflex as rx
import reflex_local_auth

from .. import navigation
from . import state, model
from ..pages import base_page
from ..ui.components import Badge, Tooltip, Table, Button, PageHeader

from ..utils import consts

def __scenario_detail_link(child: rx.Component, scenario: model.ScenarioModel):

    if scenario is None: return rx.fragment(child)
    
    scenario_id = scenario.id

    if scenario_id is None: return rx.fragment(child)

    root_path = navigation.routes.SCENARIOS
    scenario_detail_url = f"{root_path}/{scenario_id}"

    return rx.link(child, href=scenario_detail_url)

def __show_scenario(scenario:model.ScenarioModel):
    return rx.table.row(
         rx.table.cell(__scenario_detail_link(scenario.name, scenario)),
         rx.table.cell(scenario.created),
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

    scenario_list_content = rx.vstack(
        header_component.list("Test Scenarios", "route", "Add Scenario", navigation.routes.SCENARIO_ADD, "Group of Test Cases executed in a specific order"),
        rx.scroll_area(
            __table(),
            type="hover",
            scrollbars="vertical",
            style={"height": consts.RELATIVE_VIEWPORT_85},
        ),
        spacing="5",
        align="center",
        min_height=consts.RELATIVE_VIEWPORT_85
    ),

    return base_page(scenario_list_content)