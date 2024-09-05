import reflex as rx
#from ..ui.rx_base import rx_tutorial_base_page

from . import forms
from .state import EditSuiteState
from ..pages import base_page

def suite_edit_page() -> rx.Component:
    my_form = forms.suite_edit_form()
    suite = EditSuiteState.suite

    suite_content = rx.vstack(
        rx.heading("Editing ", suite.name),
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
        min_height="95vh",
    ),
    
    return base_page(suite_content)