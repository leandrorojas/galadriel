import reflex as rx
from ..ui.base import base_page

# from . import forms

class EditExampleState(rx.State):
    def handle_submit(self, form_data):
        print(form_data)

def blog_post_edit_sample_form() -> rx.Component:

    return rx.form(
        rx.vstack(
                rx.input(
                    name="title",
                    placeholder="Title",
                    width="100%",
                ),
            rx.text_area(
                name="content",
                placeholder="que dice el post?",
                required=True,
                height="50vh",
                width="100%",
            ),
            rx.button("Submit", type="submit", width="100%",),
        ),
        on_submit=EditExampleState.handle_submit,
        reset_on_submit=True,
    ),

def blog_post_edit_page() -> rx.Component:
    my_form = blog_post_edit_sample_form

    contact_content = rx.vstack(
        rx.heading("Edit Blog Post"),
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
    
    return base_page(contact_content)