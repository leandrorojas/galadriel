import reflex as rx
import reflex_local_auth

from ..pages import base_page

from ..ui.components import Badge, StatCard, Table
from ..utils import consts

def __table() -> rx.Component:
    table_component = Table()
    
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    table_component.header("key","fingerprint"),
                    table_component.header("description", "signature"),
                    table_component.header("status", "activity"),
                    table_component.header("updated", "calendar-clock"),
                ),
            ),
            #rx.table.body(None),
            variant="surface",
            size="3",
            width="100%",
            #on_mount=state.CycleState.load_cycles,
        ),
    )

@reflex_local_auth.require_login
def dashboard_page() -> rx.Component:
    page_title = Badge()

    data01 = [
        {"name": "Group A", "value": 400},
        {"name": "Group B", "value": 300, "fill": "#AC0E08FF"},
        {
            "name": "Group C",
            "value": 300,
            "fill": "rgb(80,40, 190)",
        },
        {
            "name": "Group D",
            "value": 200,
            "fill": rx.color("yellow", 10),
        },
        {"name": "Group E", "value": 278, "fill": "purple"},
        {"name": "Group F", "value": 189, "fill": "orange"},
    ]

    return base_page(
        rx.scroll_area(
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
                rx.hstack(
                    StatCard().stat_card("Cycle(s) In Progress", 1, 0, "flask-round", "cyan"),
                    StatCard().stat_card("Skipped Case(s)", 2, 1, "test-tubes", "amber"),
                    StatCard().stat_card("Failed Case(s) / No bug", 3, 2, "bug-off", "bronze"),
                ),
                rx.hstack(
                    rx.flex(
                        rx.card(
                            rx.text("Passed / Failed / Blocked Rate"),
                            rx.recharts.pie_chart(
                                rx.recharts.pie(
                                    data=data01,
                                    data_key="value",
                                    name_key="name",
                                    fill="#8884d8",
                                    label=True,
                                ),
                                width="100%",
                                height=100,
                            ),
                        ),
                        rx.scroll_area(__table(), type="hover", scrollbars="vertical", style={"height": consts.RELATIVE_VIEWPORT_85},),
                    ),
                ),
                rx.text("This is the Cases In Time section"),
                spacing="5", align="center", min_height=consts.RELATIVE_VIEWPORT_85,
            ),
            type="hover", scrollbars="vertical", style={"height": consts.RELATIVE_VIEWPORT_95},
        )
    )