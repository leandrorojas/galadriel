import reflex as rx

from . import forms
from .state import CaseState
from ..pages import base_page
from ..navigation import routes
from ..ui.components import Badge
from .model import CaseModel, PrerequisiteModel

def __case_prerequisite_list_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("chevrons-left", size=26), 
                rx.text("to List", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),            
            href=routes.CASES
        ), 
        # rx.link(
        #     rx.button(
        #         rx.icon("chevron-left", size=26), 
        #         rx.text("to Case Detal", size="4", display=["none", "none", "block"]), 
        #         size="3", 
        #     ),
        #     href=routes.CASES
        # )
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

def __show_case(test_case:CaseModel):
    return rx.table.row(
        rx.table.cell(rx.button(rx.icon("plus"))),
        rx.table.cell(test_case.name),
        rx.table.cell(test_case.created),
    )

def __table() -> rx.Component:
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    __header_cell("", "ellipsis"),
                    __header_cell("name", "fingerprint"),
                    __header_cell("created", "calendar-check-2"),
                ),
            ),
            rx.table.body(rx.foreach(CaseState.cases, __show_case)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=CaseState.load_cases,
        ),
    )

def case_prerequisite_search_page() -> rx.Component:
    test_case = CaseState.case
    title_badge = Badge() 

    #TODO: to forms
    my_form = rx.box(
        rx.box(rx.input(type="hidden", name="case_id", value=test_case.id), display="none",),
        rx.vstack(
            rx.hstack(
                rx.input(placeholder="search Test Case"),
                rx.button(rx.icon("search", size=18)),
            ),
            __table(),
        ),
    ),

    search_prerequisite_content = rx.vstack(
        rx.flex(
            title_badge.title("test-tubes", "Search Prerequisite (Test Case)"),
            rx.spacer(),
            __case_prerequisite_list_button(),
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",                   
        ),
        rx.desktop_only(
            rx.box( 
                my_form,
                width="77vw",
            ),
        ),
        rx.mobile_and_tablet(
            rx.box(
                my_form,
                width="82vw"
            ),
        ),
        spacing="5",
        align="center",
        min_height="95vh",
    )
    
    return base_page(search_prerequisite_content)