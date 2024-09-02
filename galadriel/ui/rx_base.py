import reflex as rx
from .rx_nav import rx_tutorial_navbar
from .rx_dashboard import rx_tutorial_base_dashboard_page
from ..auth.state import RxTutorialSessionState

def rx_tutorial_base_layout_component(content: rx.Component, *args) -> rx.Component:
    return rx.fragment(
        rx_tutorial_navbar(),
        rx.box( 
            content,
        ),
        rx.color_mode.button(position="bottom-left"),
        *args,
        rx.logo(),
    )

def rx_tutorial_base_page(content: rx.Component, *args) -> rx.Component:
    if not isinstance(content, rx.Component):
        content = rx.heading("this is not a valid content element")

    return rx.cond(
        RxTutorialSessionState.is_authenticated,
        rx_tutorial_base_dashboard_page(content, *args),
        rx_tutorial_base_layout_component(content, *args),
    )