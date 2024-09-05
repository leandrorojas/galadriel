import reflex as rx
from .state import AddScenarioState, EditScenarioState

def scenario_add_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name="name",
                placeholder="Scenario name",
                width="100%",
            ),
            rx.button("Add Scenario", type="submit", width="100%",),
        ),
        on_submit=AddScenarioState.handle_submit,
        reset_on_submit=True,
    ),

def scenario_edit_form() -> rx.Component:
    scenario = EditScenarioState.scenario
    scenario_name = scenario.name

    return rx.form(
        rx.box(
            rx.input(
                type="hidden",
                name="scenario_id",
                value=scenario.id
            ),
            display="none",
        ),
        rx.vstack(
                rx.input(
                    default_value=scenario_name,
                    name="name",
                    placeholder="Scenario name",
                    width="100%",
                ),
            rx.button("Save Scenario", type="submit", width="100%",),
        ),
        on_submit=EditScenarioState.handle_submit,
    ),