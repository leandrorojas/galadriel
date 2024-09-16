import reflex as rx
from .state import AddCaseState, EditCaseState

def case_add_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name="name",
                placeholder="Case name",
                width="100%",
            ),
            rx.button("Add Case", type="submit", width="100%",),
        ),
        on_submit=AddCaseState.handle_submit,
        reset_on_submit=True,
    ),

def case_edit_form() -> rx.Component:
    case = EditCaseState.case
    case_name = case.name

    return rx.form(
        rx.box(
            rx.input(
                type="hidden",
                name="case_id",
                value=case.id
            ),
            display="none",
        ),
        rx.vstack(
                rx.input(
                    default_value=case_name,
                    name="name",
                    placeholder="Case name",
                    width="100%",
                ),
            rx.button("Save Case", type="submit", width="100%",),
        ),
        on_submit=EditCaseState.handle_submit,
    ),