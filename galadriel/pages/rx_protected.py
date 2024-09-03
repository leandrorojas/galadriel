import reflex as rx
import reflex_local_auth
from ..ui.rx_base import rx_tutorial_base_page

from .. import navigation

@reflex_local_auth.require_login
def rx_tutorial_protected_page() -> rx.Component:
    about_content = rx.vstack(
        rx.heading("Protected Page"),
        rx.text(
            "Somos los más grandes del mundo",
            size="5",
        ),
        rx.link(
            rx.button("Check out our ducks!"),
            href=navigation.routes.RX_TUTORIAL_HOME_ROUTE,
            is_extgsernal=True,
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return rx_tutorial_base_page(about_content)