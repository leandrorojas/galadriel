import reflex as rx

from ..ui.components import Badge, Button
from . import base_page

def add_page(form:rx.Component, title:str, title_icon:str, button:str, link:str) -> rx.Component:
    title_badge = Badge()
    my_form = form()
    button_component = Button()

    content = rx.vstack(
        rx.flex(
            title_badge.title(title_icon, title),
            rx.spacer(),
            rx.hstack(button_component.to_list(button, link),),
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