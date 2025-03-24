import reflex as rx
import reflex_local_auth

from ..pages import base_page

from ..ui.components import Badge
from ..utils import consts

@reflex_local_auth.require_login
def dashboard_page() -> rx.Component:
    page_title = Badge()

    return base_page(
        rx.vstack(
            rx.flex(
                page_title.title("chart-no-axes-combined", "Dashboard"),
                spacing="2",
                flex_direction=["column", "column", "row"],
                align="center",
                width="100%",
                top="0px",
                padding_top="2em",
            ),
            rx.text("This is the In Progress section"),
            rx.text("This is the Cases In Time section"),
            spacing="5", align="center", min_height=consts.RELATIVE_VIEWPORT_85,
        ),
    )