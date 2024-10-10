import reflex as rx
import reflex_local_auth

from . import forms
from .state import EditSuiteState
from ..pages import base_page
from ..navigation import routes
from ..ui.components import Badge

def __suite_list_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevrons-left", size=26), 
                rx.text("to Suites", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.SUITES
        ), 
    )

def __suite_detail_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevron-left", size=26), 
                rx.text("back to Detail", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=EditSuiteState.suite_url
        ), 
    )

@reflex_local_auth.require_login
def suite_edit_page() -> rx.Component:
    my_form = forms.suite_edit_form()
    suite = EditSuiteState.suite
    title_badge = Badge()

    suite_edit_content = rx.vstack(
        rx.flex(
            title_badge.title("beaker", "Edit Test Suite"),
            rx.spacer(),
            rx.hstack(__suite_list_button(),__suite_detail_button()),
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
    
    return base_page(suite_edit_content)