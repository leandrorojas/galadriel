import reflex as rx
from ..ui.components import TopNavBar, SideBar
from ..auth.state import Session
from ..utils import consts
from ..user.state import UserRole

def public_page(content: rx.Component, *args) -> rx.Component:
    top_navbar = TopNavBar()
    return rx.fragment(
        top_navbar.navbar(),
        rx.box( 
            content,
        ),
        rx.color_mode.button(position="bottom-left"),
        *args,
    )

def private_page(content: rx.Component, *args) -> rx.Component:
    left_sidebar = SideBar()
    return rx.fragment(
        rx.hstack(
            left_sidebar.sidebar(show_backoffice=(Session.role == UserRole.ADMIN)),
            rx.box(
                content,
                width="100%",
                justify="center",
                align="center",
                min_height=consts.RELATIVE_VIEWPORT_85,
                justify_content="center",
                spacing="6",
                padding_x=["1.5em", "1.5em", "3em"],
                overflow_y="auto",
                height="100vh",
            ),
            height="100vh",
            overflow="hidden",
        ),
        *args,
    )

#galadriel home page
def base_page(content: rx.Component, *args) -> rx.Component:
    top_navbar = TopNavBar()
    left_sidebar = SideBar()
    return rx.fragment(
        rx.hstack(
            left_sidebar.sidebar(show_backoffice=(Session.role == UserRole.ADMIN)),
            rx.box(
                content,
                width="100%",
                justify="center",
                align="center",
                min_height=consts.RELATIVE_VIEWPORT_85,
                justify_content="center",
                spacing="6",
                padding_x=["1.5em", "1.5em", "3em"],
                overflow_y="auto",
                height="100vh",
            ),
            height="100vh",
            overflow="hidden",
            display=rx.cond(Session.is_authenticated, "flex", "none"),
        ),
        rx.box(
            top_navbar.navbar(),
            rx.box(content),
            rx.color_mode.button(position="bottom-left"),
            display=rx.cond(Session.is_authenticated, "none", "block"),
        ),
        *args,
    )