import reflex as rx
import reflex_local_auth

from . import state, model
from .forms import suite_add_form, suite_edit_form

from ..navigation import routes

from ..pages import base_page
from ..pages.add import add_page
from ..pages.edit import edit_page

from ..ui.components import Table, PageHeader, Moment
from ..utils import consts

def __suite_detail_link(child: rx.Component, suite: model.SuiteModel):
    if suite is None: return rx.fragment(child)
    
    suite_id = ~suite.id

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
    table_component = Table()
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    table_component.header("name", "fingerprint"),
                    table_component.header("created", "calendar-check-2"),
                ),
            ),
            rx.table.body(rx.foreach(state.SuiteState.suites, __show_suite)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.SuiteState.load_suites,
        ),
    )

@reflex_local_auth.require_login
def suites_list_page() -> rx.Component:
    header_component = PageHeader()

    return base_page(
        rx.vstack(
            header_component.list("Test Suites", "beaker", "Add Suite", routes.SUITE_ADD, "Label for a group of Test Cases based on some criteria (i.e.: project)"),
            rx.scroll_area(__table(), type="hover", scrollbars="vertical", style={"height": consts.RELATIVE_VIEWPORT_85},),
            spacing="5", align="center", min_height=consts.RELATIVE_VIEWPORT_85,
        ),
    )

@reflex_local_auth.require_login
def suite_add_page() -> rx.Component:
    return add_page(suite_add_form, "New Test Suite", "beaker", "to Suites", routes.SUITES)

@reflex_local_auth.require_login
def suite_edit_page() -> rx.Component:
    return edit_page(suite_edit_form, "Edit Test Suite", "route", "to Suites", "to Suite Detail", routes.SUITES, state.EditSuiteState.suite_url)