"""Forms for adding and editing test cases and steps."""

import reflex as rx
from .state import AddCaseState, EditCaseState, AddStepState

def case_add_form() -> rx.Component:
    """Render the form for adding a new test case."""
    return rx.form(
        rx.vstack(
            rx.input(
                name="name",
                placeholder="Case name",
                value=AddCaseState.case_name_input,
                on_change=AddCaseState.set_case_name,
                width="100%",
            ),
            rx.hstack(
                rx.button("Add Case", type="submit", flex="1"),
                rx.button("Add & Configure", type="submit", flex="1", variant="outline", on_click=AddCaseState.set_navigate_to_edit),
                width="100%",
            ),
        ),
        on_submit=AddCaseState.handle_submit,
        reset_on_submit=False,
    ),

def case_edit_form() -> rx.Component:
    """Render the form for editing an existing test case."""
    case = EditCaseState.case
    case_name = case.name

    return rx.form(
        rx.box(
            rx.input(
                type="hidden",
                name="case_id",
                value=rx.cond(case.id, case.id, "")
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

def step_add_form(disable_edit:bool) -> rx.Component:
    """Render the inline form for adding a step to a test case."""
    test_case = AddStepState.case

    return rx.form(
        rx.box(rx.el.input(type="hidden", name="case_id", value=rx.cond(test_case.id, test_case.id, "")), display="none",),
        rx.hstack(
            rx.input(name="action", placeholder="Action", width="50%"),
            rx.input(name="expected", placeholder="Expected", width="50%"),
            rx.button(rx.icon("plus", size=26), disabled=disable_edit, type="submit",),
            spacing="2",
        ),
        on_submit=AddStepState.handle_submit,
        reset_on_submit=True,
    ),