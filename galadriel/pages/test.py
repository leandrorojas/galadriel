import reflex as rx
import reflex_local_auth
from ..pages.base import base_page

from .. import navigation
from ..utils import consts

@reflex_local_auth.require_login
def protetected_page() -> rx.Component:
    about_content = rx.vstack(
        rx.heading("Protected Page"),
        rx.text(
            "Somos los más grandes del mundo",
            size="5",
        ),
        rx.link(
            rx.button("Check out our about page!"),
            href=navigation.routes.ABOUT,
            is_extgsernal=True,
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height=consts.RELATIVE_VIEWPORT_85,
    ),
    
    return base_page(about_content)