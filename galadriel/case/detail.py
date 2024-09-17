import reflex as rx

from ..navigation import routes
from . import state
from .. pages import base_page
from ..ui.components import Badge

def __case_list_button():
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevron-left", size=26), 
                rx.text("to Cases", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.CASES
        ), 
    )

def __case_edit_button():
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("pencil", size=26), 
                rx.text("Edit", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.CASE_EDIT
        ), 
    )   

def case_detail_page() -> rx.Component:
    title_badge = Badge()
    can_edit = True #TODO: add roles and privileges
    edit_link = __case_edit_button()

    edit_link_element = rx.cond(
        can_edit,
        edit_link,
        rx.fragment("")
    )
    
    case_detail_content = rx.vstack(
        rx.flex(
            title_badge.title("beaker", "Test Case Detail"),
            rx.spacer(),
            rx.hstack(__case_list_button(), edit_link_element),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",       
        ),
        rx.hstack(
            rx.heading(
                f"{state.CaseState.case.name}",
                size="7",
            ),
            rx.badge(f"{state.CaseState.case.created}", variant="outline"),
            align="center",
        ),
        spacing="5",
        align="left",
        min_height="85vh",
    ),
    
    return base_page(case_detail_content)