import reflex as rx
import reflex_local_auth

from .. import navigation
from . import state, model
from ..pages import base_page
from ..ui.components import Badge, Tooltip
from ..utils import consts

def __case_detail_link(child: rx.Component, test_case: model.CaseModel):

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

def __show_case(test_case:model.CaseModel):
    return rx.table.row(
         rx.table.cell(__case_detail_link(test_case.name, test_case)),
         rx.table.cell(test_case.created),
    )

def __add_case_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("plus", size=26), 
                rx.text("Add Case", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=navigation.routes.CASE_ADD
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
                ),
            ),
            rx.table.body(rx.foreach(state.CaseState.cases, __show_case)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.CaseState.load_cases,
        ),
    )

@reflex_local_auth.require_login
def cases_list_page() -> rx.Component:
    title_badge = Badge()
    title_tooltip = Tooltip()

    case_list_content = rx.vstack(
        rx.flex(
            title_badge.title(consts.ICON_TEST_TUBES, "Test Cases"),
            title_tooltip.info("Individual Test Cases to be executed"),
            rx.spacer(),
            rx.hstack(__add_case_button(),),
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
            style={"height": consts.RELATIVE_VIEWPORT_85},
        ),
        spacing="5",
        align="center",
        min_height=consts.RELATIVE_VIEWPORT_85,
    ),

    return base_page(case_list_content)