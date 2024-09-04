import reflex as rx
from ..ui.components import TopNavBar, SideBar
from ..auth.state import RxTutorialSessionState

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
            left_sidebar.sidebar(),
            rx.box( 
                content,
                width="100%",
                #spacing="5",
                justify="center",
                align="center",
                min_height="85vh",
                justify_content = "center",
                spacing="6",
                padding_x=["1.5em", "1.5em", "3em"],
            ),
        ),
        *args,
    )

#galadriel home page
def base_page(content: rx.Component, *args) -> rx.Component:
    #TODO: validate all params...always, in every def and class
    # if not isinstance(content, rx.Component):
    #     content = rx.heading("this is not a valid content element")

    return rx.cond(
        RxTutorialSessionState.is_authenticated,
        private_page(content, *args),
        public_page(content, *args)
    )