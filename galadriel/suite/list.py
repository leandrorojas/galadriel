import reflex as rx
import reflex_local_auth

from .. import navigation
from . import state, model
from ..pages import base_page
from ..ui.components import Badge, Tooltip, Table

from ..utils import consts

def __suite_detail_link(child: rx.Component, suite: model.SuiteModel):

    if suite is None:
        return rx.fragment(child)
    
    suite_id = suite.id
    if suite_id is None:
        return rx.fragment(child)

    root_path = navigation.routes.SUITES
    suite_detail_url = f"{root_path}/{suite_id}"

    return rx.link(
        child,
        href=suite_detail_url
    )

def __show_suite(suite:model.SuiteModel):
    return rx.table.row(
         rx.table.cell(__suite_detail_link(suite.name, suite)),
         rx.table.cell(suite.created),
    )

def __add_suite_button() -> rx.Component:
    return rx.fragment(
        rx.link(
            rx.button(
                rx.icon("plus", size=26), 
                rx.text("Add Suite", size="4", display=["none", "none", "block"]), 
                size="3", 
            ),
            href=navigation.routes.SUITE_ADD
        ), 
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
    title_badge = Badge()
    title_tooltip = Tooltip()

    suite_list_content = rx.vstack(
        rx.flex(
            title_badge.title("beaker", "Test Suites"),
            title_tooltip.info("Label for a group of Test Cases based on some criteria (i.e.: project)"),
            rx.spacer(),
            rx.hstack(__add_suite_button(),),
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

    return base_page(suite_list_content)