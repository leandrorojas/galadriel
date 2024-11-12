import reflex as rx
import reflex_local_auth

from ..pages import base_page
from ..navigation import routes
from ..ui.components import Badge

def __cycle_list_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevrons-left", size=26), 
                rx.text("to Cycles", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.CYCLES
        ), 
    )

@reflex_local_auth.require_login
def iteration_page() -> rx.Component:
    title_badge = Badge()

    cycle_edit_content = rx.vstack(
        rx.flex(
            title_badge.title("iteration-ccw", "Iteration"),
            rx.spacer(),
            __cycle_list_button(),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",
        ),
        rx.table(rx.table.cell("cell.1"),rx.table.cell("cell.2")),
        spacing="5",
        align="center",
        min_height="95vh",
    ),
    
    return base_page(cycle_edit_content)