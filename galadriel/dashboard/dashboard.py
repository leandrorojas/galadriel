import reflex as rx
import reflex_local_auth

from .state import DashboardState

from ..pages import base_page
from ..iteration.model import IterationSnapshotLinkedIssues
from typing import List

from ..ui.components import Badge, Table, Card
from ..utils import consts

TEXT_CASES = " Case(s)"

def __show_linked_bug(linked_bug: List[str]) -> rx.Component:
    print(linked_bug)
    #return rx.table.row(rx.table.cell("TEST-1"), rx.table.cell("some bug"), rx.table.cell("To Do"), rx.table.cell("2025-03-31"),),
    return rx.table.row(
        rx.table.cell(rx.link(linked_bug[0], href=linked_bug[1])), #rx.link(snapshot_element.linked_issue, href=jira.get_issue_url(snapshot_element.linked_issue)
        rx.table.cell(linked_bug[2]), 
        rx.table.cell(linked_bug[3]), 
        rx.table.cell(linked_bug[4]),
        ),

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

    tmp_chart_data = [
        {"name": "Page A", "uv": 4000, "pv": 2400, "amt": 2400},
        {"name": "Page B", "uv": 3000, "pv": 1398, "amt": 2210},
        {"name": "Page C", "uv": 2000, "pv": 9800, "amt": 2290},
        {"name": "Page D", "uv": 2780, "pv": 3908, "amt": 2000},
        {"name": "Page E", "uv": 1890, "pv": 4800, "amt": 2181},
        {"name": "Page F", "uv": 2390, "pv": 3800, "amt": 2500},
        {"name": "Page G", "uv": 3490, "pv": 4300, "amt": 2100},
    ]

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
                        width="27vw",
                    ),
                    rx.scroll_area(__table(), type="hover", scrollbars="vertical", style={"height": "33%"}),
                    spacing="4",
                ),
                rx.flex(
                    rx.card(
                        rx.text("Cases Executed"),
                        rx.recharts.composed_chart(
                            rx.recharts.area(
                                data_key="uv", stroke="#8884d8", fill="#8884d8"
                            ),
                            rx.recharts.bar(
                                data_key="amt", bar_size=20, fill="#413ea0"
                            ),
                            rx.recharts.line(
                                data_key="pv",
                                type_="monotone",
                                stroke="#ff7300",
                            ),
                            rx.recharts.x_axis(data_key="name"),
                            rx.recharts.y_axis(),
                            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                            rx.recharts.graphing_tooltip(),
                            data=tmp_chart_data,
                            height=300, 
                        ),
                        width="31vw",
                    ),
                    rx.card(
                        rx.text("Pass/Fail trends"),
                        rx.recharts.line_chart(
                            rx.recharts.line(
                                data_key="pv",
                                type_="monotone",
                                stroke="#8884d8",
                            ),
                            rx.recharts.line(
                                data_key="uv",
                                type_="monotone",
                                stroke="#82ca9d",
                            ),
                            rx.recharts.x_axis(data_key="name"),
                            rx.recharts.y_axis(),
                            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
                            rx.recharts.graphing_tooltip(),
                            rx.recharts.legend(),
                            data=tmp_chart_data,
                            height=300,
                        ),
                        width="31vw", 
                    ),
                    spacing="4",
                ),
                spacing="5", align="center",
            ),
            type="hover", scrollbars="vertical", style={"height": consts.RELATIVE_VIEWPORT_95},
        )
    )