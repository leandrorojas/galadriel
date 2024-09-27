import reflex as rx

from ..navigation import routes
from . import state
from .. pages import base_page
from ..ui.components import Badge

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

def scenario_detail_page() -> rx.Component:
    title_badge = Badge()
    can_edit = True #TODO: add roles and privileges
    edit_link = __scenario_edit_button()

    edit_link_element = rx.cond(
        can_edit,
        edit_link,
        rx.fragment("")
    )
    
    scenario_detail_content = rx.vstack(
        rx.flex(
            title_badge.title("beaker", "Test Scenario Detail"),
            rx.spacer(),
            rx.hstack(__scenario_list_button(), edit_link_element),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",       
        ),
        rx.text(            
            f"name: {state.ScenarioState.scenario.name}",
            size="5",
            white_space='pre-wrap',),
        rx.text(
            f"created: {state.ScenarioState.scenario.created}",
            size="5",
            white_space='pre-wrap',
        ),
        spacing="5",
        align="left",
        min_height="85vh",
    ),
    
    return base_page(scenario_detail_content)