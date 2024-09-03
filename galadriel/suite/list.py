import reflex as rx
#from ..ui.rx_base import rx_tutorial_base_page

from .. import navigation
from . import state, model
from ..pages import base_page

def suite_detail_link(child: rx.Component, suite: model.SuiteModel):

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

def suite_list_item(suite: model.SuiteModel):
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
                href=navigation.routes.SUITE_ADD
            ),            
            rx.foreach(state.SuiteState.suites, suite_list_item),
            spacing="5",
            align="center",
            min_height="85vh"
        ),
    ),