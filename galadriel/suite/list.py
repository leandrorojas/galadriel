import reflex as rx
from ..ui.base import base_page

from .. import navigation
from . import state, model

def suite_detail_link(child: rx.Component, suite: model.Suite):

    if suite is None:
        return rx.fragment(child)
    
    suite_id = suite.id
    if suite_id is None:
        return rx.fragment(child)

    root_path = navigation.routes.SUITES_ROUTE
    suite_detail_url = f"{root_path}/{suite_id}"

    return rx.link(
        child,
        href=suite_detail_url
    )

def suite_list_item(suite: model.Suite):
    return rx.box(
        suite_detail_link(
            rx.heading(suite.name),
            suite
        ),
        padding="1em"
    )

def suites_list_page() -> rx.Component:

    return base_page(
        rx.vstack(
            rx.heading("Test Suites"),
            rx.link(
                rx.button("New Suite"),
                href=navigation.routes.SUITE_ADD_ROUTE
            ),            
            rx.foreach(state.SuiteState.suites, suite_list_item),
            spacing="5",
            align="center",
            min_height="85vh"
        ),
    ),