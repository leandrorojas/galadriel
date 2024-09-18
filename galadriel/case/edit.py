import reflex as rx
#from ..ui.rx_base import rx_tutorial_base_page

from . import forms
from .state import EditCaseState
from ..pages import base_page
from ..navigation import routes
from ..ui.components import Badge

def __case_list_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevrons-left", size=26), 
                rx.text("to List", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),            
            href=routes.CASES
        ), 
        rx.link(
            rx.button(
                rx.icon("chevron-left", size=26), 
                rx.text("to Case Detal", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.CASE_EDIT
        )
    )

def case_edit_page() -> rx.Component:
    my_form = forms.case_edit_form()
    case = EditCaseState.case
    title_badge = Badge()

    case_edit_content = rx.vstack(
        rx.flex(
            title_badge.title("route", "Edit Test Case"),
            rx.spacer(),
            rx.hstack(__case_list_button(),),            
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
    
    return base_page(case_edit_content)