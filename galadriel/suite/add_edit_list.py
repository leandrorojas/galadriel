"""Test suite list, add, and edit pages."""

import reflex as rx
from . import state, model
from .forms import suite_add_form, suite_edit_form

from ..navigation import routes

from ..pages import base_page
from ..pages.add import add_page
from ..pages.edit import edit_page

from ..ui.components import Table, PageHeader, Moment
from ..utils import consts
from ..auth.state import require_login, require_editor, Session

def __suite_detail_link(child: rx.Component, suite: model.SuiteModel):
    if suite is None: return rx.fragment(child)
    
    suite_id = suite.id

    if suite_id is None: return rx.fragment(child)

    root_path = routes.SUITES
    suite_detail_url = f"{root_path}/{suite_id}"

    return rx.link(child, href=suite_detail_url)

def __show_suite(suite:model.SuiteModel):
    moment_component = Moment()

    return rx.table.row(
         rx.table.cell(__suite_detail_link(suite.name, suite)),
         rx.table.cell(moment_component.moment(suite.created)),
    )

def __table() -> rx.Component:
    return rx.box(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    Table.sortable_header("name", "fingerprint", "name", state.SuiteState.sort_by, state.SuiteState.sort_asc, state.SuiteState.toggle_sort),
                    Table.sortable_header("created", "calendar-check-2", "created", state.SuiteState.sort_by, state.SuiteState.sort_asc, state.SuiteState.toggle_sort),
                ),
                position="sticky",
                top="0",
                z_index="1",
                background_color="var(--color-background)",
            ),
            rx.table.body(rx.foreach(state.SuiteState.sorted_suites, __show_suite)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.SuiteState.load_suites,
        ),
        overflow_y="auto",
        flex="1",
        width="100%",
    )

@require_login
def suites_list_page() -> rx.Component:
    """Render the test suites list page."""
    header_component = PageHeader()

    return base_page(
        rx.vstack(
            header_component.list("Test Suites", "beaker", "Add Suite", routes.SUITE_ADD, Session.can_edit, "Label for a group of Test Cases based on some criteria (i.e.: project)"),
            __table(),
            spacing="5", align="center", width="100%",
        ),
    )

@require_editor
def suite_add_page() -> rx.Component:
    """Render the add test suite page."""
    return add_page(suite_add_form, "New Test Suite", "beaker", "to Suites", routes.SUITES)

@require_editor
def suite_edit_page() -> rx.Component:
    """Render the edit test suite page."""
    return edit_page(suite_edit_form, "Edit Test Suite", "beaker", "to Suites", "to Suite Detail", routes.SUITES, state.EditSuiteState.suite_url)