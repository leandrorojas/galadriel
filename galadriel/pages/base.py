import reflex as rx
from ..ui.components import TopNavBar, SideBar
from ..auth.state import Session
from ..utils import consts
from ..user.state import UserState

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
            left_sidebar.sidebar(Session.is_admin),
            rx.box(
                content,
                width="100%",
                justify="center",
                align="center",
                min_height=consts.RELATIVE_VIEWPORT_85,
                justify_content = "center",
                spacing="6",
                padding_x=["1.5em", "1.5em", "3em"],
            ),
        ),
        *args, 
    )

#galadriel home page
def base_page(content: rx.Component, *args) -> rx.Component:
    return rx.cond(
        Session.is_authenticated,
        private_page(content, *args),
        public_page(content, *args)
    )