import reflex as rx
from ..ui.base import base_page

from .. import navigation
from . import state

def suite_detail_page() -> rx.Component:
    about_content = rx.vstack(
        rx.heading(f"Detail for suite: {state.SuiteState.suite.name}"),
        rx.text(f"[{state.SuiteState.suite.id}]"),
        rx.text(
            f"c:[{state.SuiteState.suite.created}]",
            size="5",
        ),
        spacing="5",
        align="center",
        min_height="85vh",
    ),
    
    return base_page(about_content)