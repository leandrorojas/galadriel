"""Base page layouts for public and authenticated views."""

import reflex as rx
from ..ui.components import TopNavBar, SideBar
from ..auth.state import Session
from ..utils import consts
from ..user.state import UserRole

CONTENT_PADDING_X = ["1.5em", "1.5em", "3em"]

def _content_box(content: rx.Component) -> rx.Component:
    return rx.box(
        content,
        width="100%",
        flex="1",
        min_width="0",
        justify="center",
        align="center",
        min_height=consts.RELATIVE_VIEWPORT_85,
        justify_content="center",
        spacing="6",
        padding_x=CONTENT_PADDING_X,
        overflow_y="auto",
        height="100vh",
    )

def _sidebar_layout(content: rx.Component, **kwargs) -> rx.hstack:
    left_sidebar = SideBar()
    return rx.hstack(
        left_sidebar.sidebar(show_backoffice=Session.is_admin),
        _content_box(content),
        height="100vh",
        overflow="hidden",
        **kwargs,
    )

def public_page(content: rx.Component, *args) -> rx.Component:
    """Render a public page with top navigation bar."""
    top_navbar = TopNavBar()
    return rx.fragment(
        top_navbar.navbar(),
        rx.box(content),
        rx.color_mode.button(position="bottom-left"),
        *args,
    )

def private_page(content: rx.Component, *args) -> rx.Component:
    """Render a private page with sidebar layout."""
    return rx.fragment(
        _sidebar_layout(content),
        *args,
    )

def base_page(content: rx.Component, *args) -> rx.Component:
    """Render a page that adapts layout based on authentication status."""
    top_navbar = TopNavBar()
    return rx.cond(
        Session.is_authenticated,
        rx.fragment(
            _sidebar_layout(content),
            *args,
        ),
        rx.fragment(
            top_navbar.navbar(),
            rx.box(content),
            rx.color_mode.button(position="bottom-left"),
            *args,
        ),
    )