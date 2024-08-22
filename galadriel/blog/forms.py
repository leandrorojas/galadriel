import reflex as rx
from . import state

def blog_post_add_form() -> rx.Component:

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
        on_submit=state.BlogAddPostFormState.handle_submit,
        reset_on_submit=True,
    ),