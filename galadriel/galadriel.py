import reflex as rx
from rxconfig import config

from .ui.base import base_page
from . import pages, navigation, contact

class State(rx.State):
    """The app state."""

    ...

def index() -> rx.Component:
    index_content = rx.vstack(
        rx.text(
            "Get started by editing ",
            rx.code(f"{config.app_name}/{config.app_name}.py"),
            size="5",
        ),
        rx.link(
            rx.button("Check out our docs!"),
            href="https://reflex.dev/docs/getting-started/introduction/",
            is_extgsernal=True,
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return base_page(index_content)

app = rx.App(
    theme = rx.theme(
        accent_color="violet"
    ),
    style = {
        "font_family": "Montserrat",
        "font_size": "16px",        
    }
)
app.add_page(index)
app.add_page(pages.about_page, route=navigation.routes.ABOUT_ROUTE)
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_ROUTE)

app.add_page(
    contact.contact_entries_list_page, 
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.ContactState.list_entries)

app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)