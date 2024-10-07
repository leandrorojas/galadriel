import reflex as rx
from .state import AddCycleState

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

# def suite_edit_form() -> rx.Component:
#     suite = EditSuiteState.suite
#     suite_name = suite.name

#     return rx.form(
#         rx.box(
#             rx.input(
#                 type="hidden",
#                 name="suite_id",
#                 value=suite.id
#             ),
#             display="none",
#         ),
#         rx.vstack(
#                 rx.input(
#                     default_value=suite_name,
#                     name="name",
#                     placeholder="Suite name",
#                     width="100%",
#                 ),
#             rx.button("Save Suite", type="submit", width="100%",),
#         ),
#         on_submit=EditSuiteState.handle_submit, 
#     ),