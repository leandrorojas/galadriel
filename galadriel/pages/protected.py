import reflex as rx
import reflex_local_auth
from ..ui.base import base_page

from .. import navigation

@reflex_local_auth.require_login
def protected_page() -> rx.Component:
    about_content = rx.vstack(
        rx.heading("Protected Page"),
        rx.text(
            "Somos los más grandes del mundo",
            size="5",
        ),
        rx.link(
            rx.button("Check out our ducks!"),
            href=navigation.routes.HOME_ROUTE,
            is_extgsernal=True,
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return base_page(about_content)