import reflex as rx
from ..ui.base import rx_tutorial_base_page

from . import forms
from .state import BlogEditFormState

def blog_post_edit_page() -> rx.Component:
    my_form = forms.blog_post_edit_form()
    post = BlogEditFormState.post

    contact_content = rx.vstack(
        rx.heading("Editing ", post.title),
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
    
    return rx_tutorial_base_page(contact_content)