import reflex as rx
import reflex_local_auth

from ..navigation import routes
from . import state, model
from ..pages import base_page
from ..ui.components import Table, PageHeader
from ..utils import consts

def __case_detail_link(child: rx.Component, test_case: model.CaseModel):

    if test_case is None: return rx.fragment(child)
    
    case_id = test_case.id

    if case_id is None: return rx.fragment(child)

    root_path = routes.CASES
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
    header_component = PageHeader()

    case_list_content = rx.vstack(
        header_component.list("Test Cases", consts.ICON_TEST_TUBES, "Add Case", routes.CASE_ADD, "Individual Test Cases to be executed"),
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