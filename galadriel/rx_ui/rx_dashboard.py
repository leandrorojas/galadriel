import reflex as rx
from .rx_sidebar import sidebar

def rx_tutorial_base_dashboard_page(content: rx.Component, *args) -> rx.Component:
    return rx.fragment(
        rx.hstack(
            sidebar(),
            rx.box(
                rx.hstack(),
                content,
                rx.logo(),
                width="100%",
                spacing="5",
                justify="center",
                align="center",
                min_height="85vh",
                justify_content = "center",
            ),
        ),
        #rx.color_mode.button(position="bottom-left"),
        *args,
    )