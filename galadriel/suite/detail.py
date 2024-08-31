import reflex as rx
from ..ui.rx_base import rx_tutorial_base_page

from .. import navigation
from . import state

def suite_detail_page() -> rx.Component:
    can_edit = True
    edit_link = rx.link("Edit", href=f"{state.SuiteState.suite_edit_url}") #convert to button, like in line 28?

    edit_link_element = rx.cond(
        can_edit,
        edit_link,
        rx.fragment("")
    )
    
    my_child = rx.vstack(
        rx.hstack(
            rx.heading(f"Detail for suite: {state.SuiteState.suite.name}"),
            edit_link_element,
            align="center",
        ),
        rx.text(f"[{state.SuiteState.suite_id}]"),
        rx.text(
            f"c:[{state.SuiteState.suite.created}]",
            size="5",
            white_space='pre-wrap',
        ),
        spacing="5",
        align="center",
        min_height="85vh",
    ),
    
    return rx_tutorial_base_page(my_child)