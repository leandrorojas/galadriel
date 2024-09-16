import reflex as rx
from .state import AddCaseState, EditCaseState

def case_add_form() -> rx.Component:
    tmp_suites = {"oc":"1", "mmc":2, "None":-1}
    tmp_scenarios = {"check-in new member":"1", "check-in existing memeber":2, "None":-1}
    return rx.form(
        rx.vstack(
            rx.input(
                name="name",
                placeholder="Case name",
                width="100%",
            ),
            rx.hstack(
                rx.select(tmp_suites, placeholder="Select Suite"),
                rx.select(tmp_scenarios, placeholder="Select Scenario"),
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