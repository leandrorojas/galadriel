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

# def __case_list_item(test_case: model.CaseModel):
#     return rx.box(
#         __case_detail_link(
#             rx.heading(test_case.name),
#             test_case
#         ),
#         padding="1em"
#     )

def __show_cycle(cycle:model.CycleModel):
    return rx.table.row(
        rx.table.cell(__cycle_detail_link(cycle.name, cycle)),
        rx.table.cell(cycle.created),
        rx.table.cell(cycle.threshold, align="center"),
        rx.table.cell(
            rx.cond(
                (cycle.iteration_status_name != ""),
                rx.badge(cycle.iteration_status_name),
                rx.badge("n/a")
             ), 
             align="center"),
        rx.table.cell(
            rx.flex(
                rx.cond(
                    cycle.iteration_status_name != "", 
                    rx.button(rx.icon("list-todo"), on_click=lambda: state.CycleState.resume_iteration_snapshot(getattr(cycle, "id"))),
                    rx.button(rx.icon("list-video"), on_click=lambda: state.CycleState.add_iteration_snapshot(getattr(cycle, "id")))
                ),
                rx.button(rx.icon("copy-plus"), disabled=True), #, on_click=lambda: state.CycleState.move_child_down(getattr(cycle_child, "id"))), 
                spacing="2",
            )
        ),
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

def __header_cell(text: str, icon: str):
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
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
                    __header_cell("created", "calendar-check-2"),
                    __header_cell("threshold", "gauge"),
                    __header_cell("status", "activity"), 
                    __header_cell("actions","ellipsis"),
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
            __table(),
            spacing="5",
            align="center",
            min_height="85vh"
        ),

    return base_page(cycle_list_content)