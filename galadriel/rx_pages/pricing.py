import reflex as rx
from ..rx_ui.base import rx_tutorial_base_page

from .. import rx_navigation

def rx_tutorial_pricing_page() -> rx.Component:
    pricing_content = rx.vstack(
        rx.heading("Pricing"),
        rx.text(
            "Somos los más buenos, bonitos y baratos del mundo",
            size="5",
        ),
        rx.link(
            rx.button("Check out our decks!"),
            href=rx_navigation.routes.HOME_ROUTE,
            is_extgsernal=True,
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return rx_tutorial_base_page(pricing_content)