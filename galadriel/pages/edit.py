import reflex as rx

from ..ui.components import Badge
from ..pages import base_page

def __to_list_button(to_list_button:str, link:str) -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevrons-left", size=26), 
                rx.text(to_list_button, size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=link
        ),
    )

def __to_detail_button(to_detail_button:str, link:str) -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevron-left", size=26), 
                rx.text(to_detail_button, size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=link
        )
    )

def edit_page(form:rx.Component, title:str, title_icon:str, to_list_button:str, to_detail_button:str, list_link:str, detail_link:str) -> rx.Component:
    my_form = form()
    title_badge = Badge()

    case_edit_content = rx.vstack(
        rx.flex(
            title_badge.title(title_icon, title),
            rx.spacer(),
            rx.hstack(__to_list_button(to_list_button, list_link),__to_detail_button(to_detail_button, detail_link)),            
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",
        ),
        rx.desktop_only(rx.box(my_form, width="50vw",),),
        rx.mobile_and_tablet(rx.box(my_form, width="55vw"),),
        spacing="5", align="center", min_height="95vh",
    ),
    
    return base_page(case_edit_content)