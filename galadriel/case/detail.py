import reflex as rx

from ..navigation import routes
from .. pages import base_page
from ..ui.components import Badge
from .. import navigation
from . import model, state
#from .. import step
from .forms import step_add_form    

first_row = True
last_row = False

def __header_cell(text: str, icon: str):
    return rx.table.column_header_cell(
        rx.hstack(
            rx.icon(icon, size=18),
            rx.text(text),
            align="center",
            spacing="2",
        ),
    )

#prerequisites
def __prerequisite_detail_link(child: rx.Component, test_case: model.CaseModel):

    if test_case is None:
        return rx.fragment(child)
    
    case_id = test_case.id
    if case_id is None:
        return rx.fragment(child)

    root_path = navigation.routes.CASES
    case_detail_url = f"{root_path}/{case_id}"

    return rx.link(
        child,
        href=case_detail_url
    )

def __show_prerequisite(test_case:model.CaseModel):
    return rx.table.row(
        rx.table.cell("0"),
        rx.table.cell(__prerequisite_detail_link(test_case.name, test_case)),
        rx.table.cell(
            rx.flex(
                rx.button(rx.icon("arrow-big-up")), 
                rx.button(rx.icon("arrow-big-down")), 
                rx.button(rx.icon("pencil")), 
                rx.button(rx.icon("trash-2")),
                spacing="2",
            )
        ),
    )

def __prerequisites_table() -> rx.Component:
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    __header_cell("order", "list-ordered"),
                    __header_cell("test case", "pickaxe"),
                    __header_cell("", "ellipsis"),
                ),
            ),
            rx.table.body(rx.foreach(state.CaseState.cases, __show_prerequisite)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.CaseState.load_prerequisites,
        ),
    )

def __case_list_button():
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevron-left", size=26), 
                rx.text("to Cases", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.CASES
        ), 
    )

def __case_edit_button():
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("pencil", size=26), 
                rx.text("Edit", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=routes.CASE_EDIT
        ), 
    )

#steps
def __step_detail_link(child: rx.Component, test_case: model.CaseModel):

    if test_case is None:
        return rx.fragment(child)
    
    case_id = test_case.id
    if case_id is None:
        return rx.fragment(child)

    root_path = navigation.routes.CASES
    case_detail_url = f"{root_path}/{case_id}"

    return rx.link(
        child,
        href=case_detail_url
    )

def __show_step(test_step:model.StepModel):
    return rx.table.row(
        rx.table.cell(test_step.order),
        rx.table.cell(test_step.action),
        rx.table.cell(test_step.expected),
        rx.table.cell(
            rx.flex(
                rx.button(rx.icon("arrow-big-up"), disabled=True), 
                rx.button(rx.icon("arrow-big-down"), disabled=True), 
                rx.button(rx.icon("pencil"), disabled=True), 
                rx.button(rx.icon("trash-2"), disabled=True),
                spacing="2",
            )
        ),
    )

def __steps_table() -> rx.Component:
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    __header_cell("order", "list-ordered"),
                    __header_cell("action", "pickaxe"),
                    __header_cell("expected", "gem"),
                    __header_cell("", "ellipsis"),
                ),
            ),
            rx.table.body(rx.foreach(state.CaseState.steps, __show_step)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.CaseState.load_steps,
        ),
    )

#page
def case_detail_page() -> rx.Component:
    title_badge = Badge()
    test_case = state.AddStepState.case
    can_edit = True #TODO: add roles and privileges
    edit_link = __case_edit_button()

    edit_link_element = rx.cond(
        can_edit,
        edit_link,
        rx.fragment("")
    )
    
    case_detail_content = rx.vstack(
        rx.flex(
            title_badge.title("beaker", "Test Case Detail"),
            rx.spacer(),
            rx.hstack(__case_list_button(), edit_link_element),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",       
        ),
        rx.hstack(
            rx.heading(
                f"{state.CaseState.case.name}",
                size="7",
            ),
            rx.badge(f"{state.CaseState.case.created}", variant="outline"),
            align="center",
        ),
        rx.vstack(
            rx.hstack(
                rx.heading("Prerequisites", size="5",),
                rx.button(rx.icon("plus", size=26),),
            ),
            __prerequisites_table(),
        ),        
        rx.vstack(
            rx.heading("Steps", size="5",),
            #rx.hstack(step_add_form()),
            step_add_form(),
            __steps_table(),
        ),
        spacing="5",
        align="left",
        min_height="85vh",
    ),
    
    return base_page(case_detail_content)