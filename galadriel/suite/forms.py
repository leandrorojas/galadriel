import reflex as rx
from . import state

def suite_add_form() -> rx.Component:

    return rx.form(
        rx.vstack(
                rx.input(
                    name="name",
                    placeholder="Name",
                    width="100%",
                ),
            rx.button("Submit", type="submit", width="100%",),
        ),
        on_submit=state.AddSuiteState.handle_submit,
        reset_on_submit=True,
    ),