import reflex as rx

from ..ui.components import Badge
from . import base_page

def add_page(form:rx.Component, title:str, title_icon:str, button:str, link:str) -> rx.Component:
    title_badge = Badge()
    my_form = form()

    content = rx.vstack(
        rx.flex(
            title_badge.title(title_icon, title),
            rx.spacer(),
            rx.hstack(
                rx.link(
                    rx.button(
                        rx.icon("chevron-left", size=26), 
                        rx.text(button, size="4", display=["none", "none", "block"]), 
                        size="3", 
                    ),
                    href=link
                ),
            ),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",       
        ),        
        rx.desktop_only(rx.box(my_form, width="50vw",),),
        rx.mobile_and_tablet(rx.box(my_form, width="55vw"),),
        spacing="5",
        align="center",
    ),
    
    return base_page(content)