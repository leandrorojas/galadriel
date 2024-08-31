import reflex as rx
from ..ui.components import TopNavBar
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

def pivate_page(content: rx.Component, *args) -> rx.Component:
    return rx.fragment(
        rx.text("auth"),
    )    

#galadriel home page
def base_page(content: rx.Component, *args) -> rx.Component:
    #TODO: validate all params...always
    # if not isinstance(content, rx.Component):
    #     content = rx.heading("this is not a valid content element")

    return rx.cond(
        RxTutorialSessionState.is_authenticated,
        pivate_page(content, *args),
        public_page(content, *args)
    )