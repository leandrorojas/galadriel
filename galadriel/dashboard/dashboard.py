import reflex as rx
import reflex_local_auth

from .state import DashboardState

from ..pages import base_page
from typing import List

from ..ui.components import Badge, Table, Card, Chart
from ..utils import consts

TEXT_CASES = " Case(s)"

def __show_linked_bug(linked_bug: List[str]) -> rx.Component:
    return rx.table.row(rx.table.cell(rx.link(linked_bug[0], href=linked_bug[1])), rx.table.cell(linked_bug[2]), rx.table.cell(linked_bug[3]), rx.table.cell(linked_bug[4]),),

def __table() -> rx.Component:
    table_component = Table()
    
    return rx.table.root(
            rx.table.header(
                rx.table.row(
                    table_component.header("key","fingerprint"),
                    table_component.header("description", "signature"),
                    table_component.header("status", "activity"),
                    table_component.header("updated", "calendar-clock"),
                ),
            ),
            rx.table.body(rx.foreach(DashboardState.linked_bugs, __show_linked_bug)),
            variant="surface", size="3", width="100%",
            on_mount=DashboardState.load_linked_bugs,
        ),

@reflex_local_auth.require_login
def dashboard_page() -> rx.Component:
    page_title = Badge()
    charts = Chart()

    return base_page(
        rx.scroll_area(
            rx.vstack(
                rx.flex(
                    page_title.title("chart-no-axes-combined", "Dashboard"),
                    flex_direction=["column", "column", "row"],
                    align="center", width="100%", top="0px", padding_top="2em", spacing="2",
                ),
                rx.hstack(
                    Card().card(" Cycle(s)", DashboardState.cycle_count, "flask-round", "grass", suffix=" In Progress", header_size="5", subtext_size="3", icon_size=30),
                    Card().card(TEXT_CASES, DashboardState.blocked_cases, "cuboid", "red", suffix=" Blocked", header_size="5", subtext_size="3", icon_size=30),
                    Card().card(TEXT_CASES, DashboardState.skipped_cases, "test-tubes", "sky", suffix=" Skipped", header_size="5", subtext_size="3", icon_size=30),
                    Card().card(TEXT_CASES + " w/o Bug", DashboardState.cases_without_bug, "bug-off", "iris", suffix=" Failed", header_size="5", subtext_size="3", icon_size=30),
                    width="63vw", spacing="4",
                ),
                rx.flex(
                    rx.card(
                        rx.text("Passed / Failed / Blocked Rate"),
                        rx.recharts.pie_chart(
                            rx.recharts.pie(
                                data=DashboardState.get_pie_chart_data,
                                data_key="value",
                                name_key="name",
                                fill="#8884d8",
                                label=True,
                            ),
                            rx.recharts.legend(),
                            width="100%", height=350,
                        ),
                        width="26vw",
                    ),
                    rx.card(
                        rx.text("Trends"),
                        charts.composed(DashboardState.cases_trends, "name", "exec", "passed", "failed", "passed"),
                        width="36vw",
                    ),
                    spacing="4",
                ),
                rx.flex(
                    rx.scroll_area(__table(), type="hover", scrollbars="vertical", style={"height": "33%"}, width="63vw",),
                    spacing="4",
                ),                
                spacing="5", align="center",
            ),
            type="hover", scrollbars="vertical", style={"height": consts.RELATIVE_VIEWPORT_95},
        )
    )