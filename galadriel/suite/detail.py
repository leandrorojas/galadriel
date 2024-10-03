import reflex as rx
import reflex_local_auth

from ..navigation import routes
from . import state
from .. pages import base_page
from ..ui.components import Badge

def __suite_list_button():
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevron-left", size=26), 
                rx.text("to Suites", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.SUITES
        ), 
    )

def __suite_edit_button():
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("pencil", size=26), 
                rx.text("Edit", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=f"{state.SuiteState.suite_edit_url}"
        ), 
    )

@reflex_local_auth.require_login
def suite_detail_page() -> rx.Component:
    title_badge = Badge()
    can_edit = True #TODO: add roles and privileges
    edit_link = __suite_edit_button()

    edit_link_element = rx.cond(
        can_edit,
        edit_link,
        rx.fragment("")
    )
    
    suite_detail_content = rx.vstack(
        rx.flex(
            title_badge.title("beaker", "Test Suite Detail"),
            rx.spacer(),
            rx.hstack(__suite_list_button(), edit_link_element),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",       
        ),
        rx.text(            
            f"name: {state.SuiteState.suite.name}",
            size="5",
            white_space='pre-wrap',),
        rx.text(
            f"created: {state.SuiteState.suite.created}",
            size="5",
            white_space='pre-wrap',
        ),
        spacing="5",
        align="left",
        min_height="85vh",
    ),
    
    return base_page(suite_detail_content)