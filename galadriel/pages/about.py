import reflex as rx
from .base import base_page

from .. import navigation

def about_page() -> rx.Component:
    about_content = rx.vstack(
        rx.heading("About Us"),
        rx.text(
            "[galadriel] Somos los más grandes del mundo",
            size="5",
        ),
        rx.link(
            rx.button("Check out our ducks!"),
            href=navigation.rx_routes.RX_TUTORIAL_HOME_ROUTE,
            is_extgsernal=True,
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return base_page(about_content)