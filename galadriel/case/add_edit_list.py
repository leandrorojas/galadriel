"""Test case list, add, and edit pages."""

import reflex as rx
from . import state, model
from .forms import case_add_form, case_edit_form

from ..navigation import routes

from ..pages import base_page
from ..pages.add import add_page
from ..pages.edit import edit_page

from ..ui.components import Table, PageHeader, Moment
from ..utils import consts

from ..auth.state import require_login, require_editor, Session

def __case_detail_link(child: rx.Component, test_case: model.CaseModel):
    if test_case is None: return rx.fragment(child)
    
    case_id = test_case.id

    if case_id is None: return rx.fragment(child)

    root_path = routes.CASES
    case_detail_url = f"{root_path}/{case_id}"

    return rx.link(child, href=case_detail_url)

def __show_case(test_case:model.CaseModel):
    moment_component = Moment()
    return rx.table.row(
        rx.table.cell(__case_detail_link(test_case.name, test_case)),
        rx.table.cell(moment_component.moment(test_case.created)) 
    )

def __table() -> rx.Component:
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    Table.sortable_header("name", "fingerprint", "name", state.CaseState.sort_by, state.CaseState.sort_asc, state.CaseState.toggle_sort),
                    Table.sortable_header("created", "calendar-check-2", "created", state.CaseState.sort_by, state.CaseState.sort_asc, state.CaseState.toggle_sort),
                ),

            ),
            rx.table.body(rx.foreach(state.CaseState.sorted_cases, __show_case)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.CaseState.load_cases,
        ),
    )

#region #LIST
@require_login
def cases_list_page() -> rx.Component:
    """Render the test cases list page."""
    header_component = PageHeader()

    return base_page(
        rx.vstack(
            header_component.list("Test Cases", consts.ICON_TEST_TUBES, "Add Case", routes.CASE_ADD, Session.can_edit, "Individual Test Cases to be executed"),
            __table(),
            spacing="5", align="center", min_height=consts.RELATIVE_VIEWPORT_85,
        ),
    )
#endregion

#region ADD
@require_editor
def case_add_page() -> rx.Component:
    """Render the add test case page."""
    return add_page(case_add_form, "New Test Case", consts.ICON_TEST_TUBES, "to Cases", routes.CASES)
#endregion

#region EDIT
@require_editor
def case_edit_page() -> rx.Component:
    """Render the edit test case page."""
    return edit_page(case_edit_form, "Edit Test Case", consts.ICON_TEST_TUBES, "to Cases", "to Case Detail", routes.CASES, state.EditCaseState.case_url)
#endregion