import reflex as rx
import reflex_local_auth

from .. import navigation
from . import state, model
from ..pages import base_page
from ..ui.components import Badge, Tooltip, Table, Button
from ..utils import consts

def __case_detail_link(child: rx.Component, test_case: model.CaseModel):

    if test_case is None: return rx.fragment(child)
    
    case_id = test_case.id

    if case_id is None: return rx.fragment(child)

    root_path = navigation.routes.CASES
    case_detail_url = f"{root_path}/{case_id}"

    return rx.link(child, href=case_detail_url)

def __show_case(test_case:model.CaseModel):
    return rx.table.row(
         rx.table.cell(__case_detail_link(test_case.name, test_case)),
         rx.table.cell(test_case.created),
    )

def __table() -> rx.Component:
    table_component = Table()
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    table_component.header("name", "fingerprint"),
                    table_component.header("created", "calendar-check-2"),
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
    button_component = Button()

    case_list_content = rx.vstack(
        rx.flex(
            title_badge.title(consts.ICON_TEST_TUBES, "Test Cases"),
            title_tooltip.info("Individual Test Cases to be executed"),
            rx.spacer(),
            rx.hstack(button_component.add("Add Case", navigation.routes.CASE_ADD),),
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