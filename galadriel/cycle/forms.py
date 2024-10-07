import reflex as rx
from .state import AddCycleState, EditCycleState

def cycle_add_form() -> rx.Component:
    return rx.form(
        rx.vstack(
            rx.input(
                name="name",
                placeholder="Cycle name",
                width="100%",
            ),
            rx.input(
                name="threshold",
                placeholder="Pass Cases Threshold",
                default_value="80",
                width="100%",
                type="number", min="0", max="100"
            ),
            rx.button("Add Cycle", type="submit", width="100%",),
        ),
        on_submit=AddCycleState.handle_submit,
        reset_on_submit=True,
    ),

def cycle_edit_form() -> rx.Component:
    cycle = EditCycleState.cycle
    cycle_name = cycle.name
    cycle_threshold = cycle.threshold

    return rx.form(
        rx.box(
            rx.input(
                type="hidden",
                name="cycle_id",
                value=cycle.id
            ),
            display="none",
        ),
        rx.vstack(
                rx.input(
                    default_value=cycle_name,
                    name="name",
                    placeholder="Cycle name",
                    width="100%",
                ),
                rx.input(
                    default_value=f"{cycle_threshold}",
                    name="threshold",
                    placeholder="Pass Cases Threshold",
                    width="100%",
                    #type="number", min="0", max="100"
                ),                
            rx.button("Save Cycle", type="submit", width="100%",),
        ),
        on_submit=EditCycleState.handle_submit, 
    ),