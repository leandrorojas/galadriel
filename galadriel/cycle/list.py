import reflex as rx
import reflex_local_auth

from .. import navigation
from . import state, model
from ..pages import base_page
from ..ui.components import Badge, Tooltip

def __cycle_detail_link(child: rx.Component, cycle: model.CycleModel):

    if cycle is None:
        return rx.fragment(child)
    
    cycle_id = cycle.id
    if cycle_id is None:
        return rx.fragment(child)

    root_path = navigation.routes.CYCLES
    case_detail_url = f"{root_path}/{cycle_id}"

    return rx.link(
        child,
        href=case_detail_url
    )

def __badge(text: str, color=""):
    if (color != ""):
        return rx.badge(text, radius="full", variant="soft", size="3", color_scheme=color)
    else:
        return rx.badge(text, radius="full", variant="soft", size="3")

def __execution_status_badge(child_execution_status: str):
    badge_mapping = {
        "in progress": ("in progress", "blue"),
        "closed": ("closed", "red"),
        "completed": ("completed", "green"),
        "on hold": ("on hold", "yellow"),
        "[F] completed": ("[F] completed", "orange"),
        "not started": ("not started", "")
    }
    return __badge(*badge_mapping.get(child_execution_status, ("n/a", "")))

def __cycle_status_badge(cycle_status: str):
    badge_mapping = {
        "passed": ("passed", "green"),
        "failed": ("failed", "red"),
        "testing": ("testing", "blue"),
    }
    return __badge(*badge_mapping.get(cycle_status, ("n/a", "")))

def __show_cycle(cycle:model.CycleModel):
    return rx.table.row(
        rx.table.cell(__cycle_detail_link(cycle.name, cycle)),
        rx.table.cell(
            rx.match(
                cycle.cycle_status_name,
                ("passed", __cycle_status_badge("passed")),
                ("failed", __cycle_status_badge("failed")),
                ("testing", __cycle_status_badge("testing")),
            ),
            align="center"
        ),
        rx.table.cell(cycle.threshold, align="center"),
        rx.table.cell(
            rx.match(
                cycle.iteration_status_name,
                ("in progress", __execution_status_badge("in progress")),
                ("closed", __execution_status_badge("closed")),
                ("completed", __execution_status_badge("completed")),
                ("on hold", __execution_status_badge("on hold")),
                ("[F] completed", __execution_status_badge("[F] completed")),
                ("not started", __execution_status_badge("not started")),
            ),
            align="center"
        ),
        rx.table.cell(
            rx.flex(
                rx.cond(
                    cycle.iteration_status_name != "", 
                    rx.cond((cycle.iteration_status_name == "closed") | (cycle.iteration_status_name == "completed"),
                        rx.cond(cycle.iteration_status_name == "closed",
                            rx.button(rx.icon("eye"), color_scheme="jade", variant="soft", on_click=lambda: state.CycleState.view_iteration_snapshot(getattr(cycle, "id"))),
                            rx.cond((cycle.iteration_status_name == "[F] completed"),
                                rx.button(rx.icon("list-todo"), color_scheme="lime", variant="soft", on_click=lambda: state.CycleState.view_iteration_snapshot(getattr(cycle, "id"))),
                                rx.button(rx.icon("eye"), color_scheme="jade", variant="soft", on_click=lambda: state.CycleState.view_iteration_snapshot(getattr(cycle, "id"))))),
                        rx.button(rx.icon("list-todo"), color_scheme="lime", variant="soft", on_click=lambda: state.CycleState.view_iteration_snapshot(getattr(cycle, "id"))),
                    ),
                    rx.button(rx.icon("list-video"), on_click=lambda: state.CycleState.add_iteration_snapshot(getattr(cycle, "id")))
                ),
                rx.button(rx.icon("copy-plus"), variant="soft", on_click=lambda: state.CycleState.duplicate_cycle(getattr(cycle, "id"))), 
                spacing="2",
            )
        ),
        rx.table.cell(cycle.created),
    )

def __add_adhoc_cycle_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("plus", size=26), 
                rx.text("Add Cycle", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=navigation.routes.CYCLE_ADD
        ), 
    )

def __header_cell(text: str, icon: str, info_tooltip:str = ""):
    title_tooltip = Tooltip()

    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            rx.cond(info_tooltip == "", rx.text(""), title_tooltip.info(info_tooltip)),
            align="center",
            spacing="2",
        ),
    )    

def __table() -> rx.Component:
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    __header_cell("name", "fingerprint"),
                    __header_cell("status", "activity"),
                    __header_cell("% t/p/f", "gauge", "% of [t]hreshold / [p]assed / [f]ailed"),
                    __header_cell("execution", "activity", "[F] completed = completed with failed TCs"), 
                    __header_cell("","ellipsis"),
                    __header_cell("created", "calendar-check-2"),
                ),
            ),
            rx.table.body(rx.foreach(state.CycleState.cycles, __show_cycle)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.CycleState.load_cycles,
        ),
    )

@reflex_local_auth.require_login
def cycle_list_page() -> rx.Component:
    title_badge = Badge()
    title_tooltip = Tooltip()

    cycle_list_content = rx.vstack(
        rx.flex(
            title_badge.title("flask-round", "Cycles"),
            title_tooltip.info("List of Cycles to execute"),
            rx.spacer(),
            rx.hstack(__add_adhoc_cycle_button(),),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",
        ),
        rx.scroll_area(
            __table(),
            type="hover",
            scrollbars="vertical",
            style={"height": "85vh"},
        ),
        spacing="5",
        align="center",
        min_height="85vh"
    ),

    return base_page(cycle_list_content)