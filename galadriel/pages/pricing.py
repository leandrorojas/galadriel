import reflex as rx
from ..ui.base import base_page

from .. import navigation

def pricing_page() -> rx.Component:
    pricing_content = rx.vstack(
        rx.heading("Pricing"),
        rx.text(
            "Somos los más buenos, bonitos y baratos del mundo",
            size="5",
        ),
        rx.link(
            rx.button("Check out our decks!"),
            href=navigation.routes.HOME_ROUTE,
            is_extgsernal=True,
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return base_page(pricing_content)