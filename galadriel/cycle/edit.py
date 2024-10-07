import reflex as rx
import reflex_local_auth

from . import forms
from .state import EditCycleState
from ..pages import base_page
from ..navigation import routes
from ..ui.components import Badge

def __cycle_list_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevrons-left", size=26), 
                rx.text("to Cycles", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.CYCLES
        ), 
    )

def __cycle_detail_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevron-left", size=26), 
                rx.text("back to Detail", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=f"{EditCycleState.cycle_url}"
        ), 
    )

@reflex_local_auth.require_login
def cycle_edit_page() -> rx.Component:
    my_form = forms.cycle_edit_form()
    cycle = EditCycleState.cycle
    title_badge = Badge()

    cycle_edit_content = rx.vstack(
        rx.flex(
            title_badge.title("beaker", "Edit Test Cycle"),
            rx.spacer(),
            rx.hstack(__cycle_list_button(),__cycle_detail_button()),
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
    
    return base_page(cycle_edit_content)