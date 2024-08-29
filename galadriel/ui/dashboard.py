import reflex as rx
from .sidebar import sidebar

def base_dashboard_page(content: rx.Component, *args) -> rx.Component:
    return rx.fragment(
        rx.hstack(
            sidebar(),
            rx.box( 
                content,
                rx.logo(),
            ),
        ),
        #rx.color_mode.button(position="bottom-left"),
        *args,
    )