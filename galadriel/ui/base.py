import reflex as rx
from .nav import navbar
from .dashboard import base_dashboard_page

def base_layout_component(content: rx.Component, *args) -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.box( 
            content,
        ),
        rx.color_mode.button(position="bottom-left"),
        *args,
        rx.logo(),
    )

def base_page(content: rx.Component, *args) -> rx.Component:
    is_logged_in = True

    return rx.cond(
        is_logged_in,
        base_dashboard_page(content, *args),
        base_layout_component(content, *args),
    ) 