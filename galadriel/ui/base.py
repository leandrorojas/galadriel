import reflex as rx
from .nav import navbar
from .dashboard import base_dashboard_page
from ..auth.state import SessionState

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
    # if not isinstance(content, rx.Component):
    #     content = rx.heading("this is not a valid content element")

    return rx.cond(
        SessionState.is_authenticated,
        base_dashboard_page(content, *args),
        base_layout_component(content, *args),
    ) 