import reflex as rx
import reflex_local_auth

from . import state, model
from .forms import cycle_add_form, cycle_edit_form

from ..navigation import routes

from ..pages.add import add_page
from ..pages.edit import edit_page
from ..pages import base_page

from ..ui.components import Table, PageHeader, Moment
from ..utils import consts

def __cycle_detail_link(child: rx.Component, cycle: model.CycleModel):
    if cycle is None: return rx.fragment(child)
    
    cycle_id = ~cycle.id
    
    if cycle_id is None: return rx.fragment(child)

    root_path = routes.CYCLES
    case_detail_url = f"{root_path}/{cycle_id}"

    return rx.link(child, href=case_detail_url)

def __badge(text: str, color=""):
    if (color != ""):
        return rx.badge(text, radius="full", variant="soft", size="3", color_scheme=color)
    else:
        return rx.badge(text, radius="full", variant="soft", size="3")

def __execution_status_badge(child_execution_status: str):
    badge_mapping = {
        consts.STATUS_EXECUTION_IN_PROGRESS: (consts.STATUS_EXECUTION_IN_PROGRESS, "blue"),
        consts.STATUS_EXECUTION_CLOSED: (consts.STATUS_EXECUTION_CLOSED, "red"),
        consts.STATUS_EXECUTION_COMPLETED: (consts.STATUS_EXECUTION_COMPLETED, "green"),
        consts.STATUS_EXECUTION_ON_HOLD: (consts.STATUS_EXECUTION_ON_HOLD, "yellow"),
        consts.STATUS_EXECUTION_COMPLETED_FAILED: (consts.STATUS_EXECUTION_COMPLETED_FAILED, "orange"),
        consts.STATUS_EXECUTION_NOT_STARTED: (consts.STATUS_EXECUTION_NOT_STARTED, "")
    }
    return __badge(*badge_mapping.get(child_execution_status, ("n/a", "")))

def __cycle_status_badge(cycle_status: str):
    badge_mapping = {
        consts.STATUS_CYCLE_PASSED: (consts.STATUS_CYCLE_PASSED, "green"),
        consts.STATUS_CYCLE_FAILED: (consts.STATUS_CYCLE_FAILED, "red"),
        "testing": ("testing", "blue"),
    }
    return __badge(*badge_mapping.get(cycle_status, ("n/a", "")))

def __show_cycle(cycle:model.CycleModel):
    moment_component = Moment()
    
    return rx.table.row(
        rx.table.cell(__cycle_detail_link(cycle.name, cycle)),
        rx.table.cell(
            rx.match(
                cycle.cycle_status_name,
                (consts.STATUS_CYCLE_PASSED, __cycle_status_badge(consts.STATUS_CYCLE_PASSED)),
                (consts.STATUS_CYCLE_FAILED, __cycle_status_badge(consts.STATUS_CYCLE_FAILED)),
                ("testing", __cycle_status_badge("testing")),
            ),
            align="center"
        ),
        rx.table.cell(cycle.threshold, align="center"),
        rx.table.cell(
            rx.match(
                cycle.iteration_status_name,
                (consts.STATUS_EXECUTION_IN_PROGRESS, __execution_status_badge(consts.STATUS_EXECUTION_IN_PROGRESS)),
                (consts.STATUS_EXECUTION_CLOSED, __execution_status_badge(consts.STATUS_EXECUTION_CLOSED)),
                (consts.STATUS_EXECUTION_COMPLETED, __execution_status_badge(consts.STATUS_EXECUTION_COMPLETED)),
                (consts.STATUS_EXECUTION_ON_HOLD, __execution_status_badge(consts.STATUS_EXECUTION_ON_HOLD)),
                (consts.STATUS_EXECUTION_COMPLETED_FAILED, __execution_status_badge(consts.STATUS_EXECUTION_COMPLETED_FAILED)),
                (consts.STATUS_EXECUTION_NOT_STARTED, __execution_status_badge(consts.STATUS_EXECUTION_NOT_STARTED)),
            ),
            align="center"
        ),
        rx.table.cell(
            rx.flex(
                rx.cond(
                    cycle.iteration_status_name != "", 
                    rx.cond((cycle.iteration_status_name == consts.STATUS_EXECUTION_CLOSED) | (cycle.iteration_status_name == consts.STATUS_EXECUTION_COMPLETED),
                        rx.cond(cycle.iteration_status_name == consts.STATUS_EXECUTION_CLOSED,
                            rx.button(rx.icon("eye"), color_scheme="jade", variant="soft", on_click=lambda: state.CycleState.view_iteration_snapshot(getattr(cycle, consts.FIELD_ID))),
                            rx.cond((cycle.iteration_status_name == consts.STATUS_EXECUTION_COMPLETED_FAILED),
                                rx.button(rx.icon("list-todo"), color_scheme="lime", variant="soft", on_click=lambda: state.CycleState.view_iteration_snapshot(getattr(cycle, consts.FIELD_ID))),
                                rx.button(rx.icon("eye"), color_scheme="jade", variant="soft", on_click=lambda: state.CycleState.view_iteration_snapshot(getattr(cycle, consts.FIELD_ID))))),
                        rx.button(rx.icon("list-todo"), color_scheme="lime", variant="soft", on_click=lambda: state.CycleState.view_iteration_snapshot(getattr(cycle, consts.FIELD_ID))),
                    ),
                    rx.button(rx.icon("list-video"), on_click=lambda: state.CycleState.add_iteration_snapshot(getattr(cycle, consts.FIELD_ID)))
                ),
                rx.button(rx.icon("copy-plus"), variant="soft", on_click=lambda: state.CycleState.duplicate_cycle(getattr(cycle, consts.FIELD_ID))), 
                spacing="2",
            )
        ),
        rx.table.cell(moment_component.moment(cycle.created)),
    )

def __table() -> rx.Component:
    table_component = Table()
    
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    table_component.header("name", "fingerprint"),
                    table_component.header("status", "activity"),
                    table_component.header("% t/p/f", "gauge", info_tooltip= "% of [t]hreshold / [p]assed / [f]ailed"),
                    table_component.header("execution", "activity", info_tooltip=f"{consts.STATUS_EXECUTION_COMPLETED_FAILED} = completed with failed TCs"), 
                    table_component.header("","ellipsis"),
                    table_component.header("created", "calendar-check-2"),
                ),
            ),
            rx.table.body(rx.foreach(state.CycleState.cycles, __show_cycle)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.CycleState.load_cycles,
        ),
    )

#region LIST
@reflex_local_auth.require_login
def cycle_list_page() -> rx.Component:
    page_component = PageHeader()

    return base_page(
        rx.vstack(
            page_component.list("Cycles", "flask-round", "Add Cycle", routes.CYCLE_ADD, "List of Cycles to execute"),
            rx.scroll_area(__table(), type="hover", scrollbars="vertical", style={"height": consts.RELATIVE_VIEWPORT_85},),
            spacing="5", align="center", min_height=consts.RELATIVE_VIEWPORT_85,
        ),
    )
#endregion

#region ADD
@reflex_local_auth.require_login
def cycle_add_page() -> rx.Component:
    return add_page(cycle_add_form, "New Cycle", "flask-round", "to Cycles", routes.CYCLES)
#endregion

#region EDIT
@reflex_local_auth.require_login
def cycle_edit_page() -> rx.Component:
    return edit_page(cycle_edit_form, "Edit Test Cycle", "beaker", "to Cycles", "back to Detail", routes.CYCLES, state.EditCycleState.cycle_url)
#endregion