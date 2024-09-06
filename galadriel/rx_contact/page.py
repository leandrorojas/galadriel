import reflex as rx
from ..rx_ui.base import rx_tutorial_base_page

from .. import rx_navigation
from . import form, state, model

def contact_entry_list_item(contact: model.RxTutorialContactModel):
    return rx.box(
        rx.heading(contact.first_name, " (", contact.email, ")"),
        rx.text("Message: ", contact.contact_message),
        #rx.cond(contact.userid)
        padding="1em"
    )

def contact_entries_list_page() -> rx.Component:

    return rx_tutorial_base_page(
        rx.vstack(
            rx.heading("Contact Entries"),
            rx.foreach(state.RxTutorialContactState.entries, contact_entry_list_item),
            spacing="5",
            align="center",
            min_height="85vh"
        ),
    ),

def contact_page() -> rx.Component:
    contact_content = rx.vstack(
        rx.heading("Contact Us"),
        rx.cond(state.RxTutorialContactState.submitted, "Graciavóh, {email}".format(email=state.RxTutorialContactState.contact_email), ""),
        rx.desktop_only(
            rx.box(
                form.contact_form(),
                width="50vw",
            ),
        ),
        rx.mobile_and_tablet(
            rx.box(
                form.contact_form(),
                width="55vw"
            ),
        ),
        rx.link(
            rx.button("Check out our ducks!"),
            href=rx_navigation.routes.HOME_ROUTE,
            is_extgsernal=True,
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return rx_tutorial_base_page(contact_content)