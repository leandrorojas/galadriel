import reflex as rx
from ..ui.components import Badge
from ..pages import base_page
from ..navigation import routes

from . import forms

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

def scenario_add_page() -> rx.Component:
    title_badge = Badge()
    my_form = forms.scenario_add_form()

    scenario_add_content = rx.vstack(
        rx.flex(
            title_badge.title("route", "New Test Scenario"),
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
    ),
    
    return base_page(scenario_add_content)