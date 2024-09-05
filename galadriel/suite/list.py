import reflex as rx
#from ..ui.rx_base import rx_tutorial_base_page

from .. import navigation
from . import state, model
from ..pages import base_page
from ..ui.components import Badge, Tooltip

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

def __suite_list_item(suite: model.SuiteModel):
    return rx.box(
        __suite_detail_link(
            rx.heading(suite.name),
            suite
        ),
        padding="1em"
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
            rx.table.body(rx.foreach(state.SuiteState.suites, __show_suite)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.SuiteState.load_suites,
        ),
    )

def suites_list_page() -> rx.Component:
    title_badge = Badge()
    title_tooltip = Tooltip()

    return base_page(
        rx.vstack(
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
            __table(),
            spacing="5",
            align="center",
            min_height="85vh"
        ),
    ),