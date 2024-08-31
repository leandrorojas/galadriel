import reflex as rx
from ..ui.base import rx_tutorial_base_page

from . import forms

def suite_add_page() -> rx.Component:
    my_form = forms.suite_add_form()

    contact_content = rx.vstack(
        rx.heading("New Test Suite"),
        rx.desktop_only(
            rx.box(
                my_form,
                width="50vw",
            ),
        ),
        rx.mobile_and_tablet(
            rx.box(
                my_form,
                width="55vw"
            ),
        ),
        spacing="5",
        align="center",
        #min_height="95vh",
    ),
    
    return rx_tutorial_base_page(contact_content)