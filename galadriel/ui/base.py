import reflex as rx
from .nav import navbar

def base_page(content: rx.Component, *args) -> rx.Component:
    return rx.fragment(
        navbar(),
        rx.box( 
            content,
        ),
        rx.color_mode.button(position="bottom-left"),
        *args,
        rx.logo(),
    )