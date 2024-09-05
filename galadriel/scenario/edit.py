import reflex as rx
#from ..ui.rx_base import rx_tutorial_base_page

from . import forms
from .state import EditScenarioState
from ..pages import base_page
from ..navigation import routes
from ..ui.components import Badge

def __scenario_list_button() -> rx.Component:
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

def scenario_edit_page() -> rx.Component:
    my_form = forms.scenario_edit_form()
    scenario = EditScenarioState.scenario
    title_badge = Badge()

    scenario_edit_content = rx.vstack(
        rx.flex(
            title_badge.title("route", "Edit Test Scenario"),
            rx.spacer(),
            rx.hstack(__scenario_list_button(),),            
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",       
        ),
        rx.desktop_only(
            rx.box( 
                my_form,
                width="50vw",
            ),
        ),
        rx.mobile_and_tablet(
            rx.box(
                my_form,
                width="55vw"
            ),
        ),
        spacing="5",
        align="center",
        min_height="95vh",
    ),
    
    return base_page(scenario_edit_content)