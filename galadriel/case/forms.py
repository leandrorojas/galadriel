import reflex as rx
from .state import AddCaseState, EditCaseState, AddStepState

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

def step_add_form() -> rx.Component:
    test_case = AddStepState.case

    return rx.form(
        rx.box(
            rx.input(
                type="hidden",
                name="case_id",
                value=test_case.id
            ),
            display="none",
        ),
        rx.hstack(
            rx.input(name="action", placeholder="action", width="50%"), #rx.text_area() for multiline GAL-79
            rx.input(name="expected", placeholder="expected", width="50%"),
            rx.button(rx.icon("plus", size=26), type="submit",),
            spacing="2",
        ),
        on_submit=AddStepState.handle_submit,
        reset_on_submit=True,
    ),

def prerequisite_search_form() -> rx.Component:
    ...