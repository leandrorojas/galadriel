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
            rx.table.body(
                rx.table.row(
                    rx.table.cell("TEST-001"),
                    rx.table.cell("some bug"),
                    rx.table.cell("To Do"),
                    rx.table.cell("2025-03-31"),
                ),
                rx.table.row(
                    rx.table.cell("TEST-002"),
                    rx.table.cell("another bug"),
                    rx.table.cell("In Progress"),
                    rx.table.cell("2025-03-18"),
                ),
                rx.table.row(
                    rx.table.cell("TEST-003"),
                    rx.table.cell("this bug"),
                    rx.table.cell("Open"),
                    rx.table.cell("2025-03-10"),
                ),
                rx.table.row(
                    rx.table.cell("TEST-004"),
                    rx.table.cell("that bug"),
                    rx.table.cell("Closed"),
                    rx.table.cell("2025-03-01"),
                ),
                rx.table.row(
                    rx.table.cell("TEST-005"),
                    rx.table.cell("some bug"),
                    rx.table.cell("To Do"),
                    rx.table.cell("2025-03-31"),
                ),
            ),
            variant="surface",
            size="3",
            width="100%",
        ),
    )

@reflex_local_auth.require_login
def dashboard_page() -> rx.Component:
    page_title = Badge()

    tmp_pie_chart_data = [
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
                    spacing="2",
                    flex_direction=["column", "column", "row"],
                    align="center",
                    width="100%",
                    top="0px",
                    padding_top="2em",
                ),
                rx.hstack(
                    StatCard().stat_card("Cycle(s) In Progress", 150, 743, "flask-round", "cyan"),
                    StatCard().stat_card("Skipped Case(s)", 2, 1, "test-tubes", "amber"),
                    StatCard().stat_card("Failed Case(s) / No bug", 10, 15, "bug-off", "bronze"),
                    spacing="4",
                ),
                rx.flex(
                    rx.card(
                        rx.text("Passed / Failed / Blocked Rate"),
                        rx.recharts.pie_chart(
                            rx.recharts.pie(
                                data=tmp_pie_chart_data,
                                data_key="value",
                                name_key="name",
                                fill="#8884d8",
                                label=True,
                            ),
                            width="100%",
                            height=250,
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