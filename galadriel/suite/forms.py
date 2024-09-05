import reflex as rx
from .state import AddSuiteState, EditSuiteState

def suite_add_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name="name",
                placeholder="Suite name",
                width="100%",
            ),
            rx.button("Add Suite", type="submit", width="100%",),
        ),
        on_submit=AddSuiteState.handle_submit,
        reset_on_submit=True,
    ),

def suite_edit_form() -> rx.Component:
    suite = EditSuiteState.suite
    suite_name = suite.name

    return rx.form(
        rx.box(
            rx.input(
                type="hidden",
                name="suite_id",
                value=suite.id
            ),
            display="none",
        ),
        rx.vstack(
                rx.input(
                    default_value=suite_name,
                    name="name",
                    placeholder="Suite name",
                    width="100%",
                ),
            rx.button("Save Suite", type="submit", width="100%",),
        ),
        on_submit=EditSuiteState.handle_submit,
    ),