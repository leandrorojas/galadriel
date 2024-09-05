import reflex as rx
#from ..ui.rx_base import rx_tutorial_base_page

from .. import navigation
from . import state, model
from ..pages import base_page
from ..ui.components import Badge, Tooltip

def __scenario_detail_link(child: rx.Component, scenario: model.CaseModel):

    if scenario is None:
        return rx.fragment(child)
    
    scenario_id = scenario.id
    if scenario_id is None:
        return rx.fragment(child)

    root_path = navigation.routes.SCENARIOS
    scenario_detail_url = f"{root_path}/{scenario_id}"

    return rx.link(
        child,
        href=scenario_detail_url
    )

def __scenario_list_item(scenario: model.CaseModel):
    return rx.box(
        __scenario_detail_link(
            rx.heading(scenario.name),
            scenario
        ),
        padding="1em"
    )

def __show_scenario(scenario:model.CaseModel):
    return rx.table.row(
         rx.table.cell(__scenario_detail_link(scenario.name, scenario)),
         rx.table.cell(scenario.created),
    )

def __add_scenario_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("plus", size=26), 
                rx.text("Add Scenario", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=navigation.routes.SCENARIO_ADD
        ), 
    )

def __header_cell(text: str, icon: str):
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )    

def __table() -> rx.Component:
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    __header_cell("name", "fingerprint"),
                    __header_cell("created", "calendar-check-2"),
                ),
            ),
            rx.table.body(rx.foreach(state.ScenarioState.scenarios, __show_scenario)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.ScenarioState.load_scenarios,
        ),
    )

def scenarios_list_page() -> rx.Component:
    title_badge = Badge()
    title_tooltip = Tooltip()

    return base_page(
        rx.vstack(
            rx.flex(
                title_badge.title("route", "Test Scenarios"),
                title_tooltip.info("Group of Test Cases executed in a specific order"),
                rx.spacer(),
                rx.hstack(__add_scenario_button(),),
                spacing="2",
                flex_direction=["column", "column", "row"],
                align="center",
                width="100%",
                top="0px",
                padding_top="2em",       
            ),
            __table(),
            spacing="5",
            align="center",
            min_height="85vh"
        ),
    ),