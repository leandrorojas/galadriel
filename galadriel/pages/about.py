import reflex as rx
from .base import base_page
from ..utils import consts

def about_content() -> rx.Component:
    about_content_var = rx.vstack(
        rx.heading("About galadriel"),
        rx.heading("galadriel is a Test Management System", size="4"),
        rx.vstack(
            rx.text("A simple but yet straight to the point and functional Test Management System. Inspiration drawn from ", rx.link(rx.code("testlink™"), href="https://testlink.org/")),
            rx.spacer(), rx.spacer(),
            rx.text("want to contribute? have a question? need attention and tender love?"),
            rx.flex(
                rx.text("visit us on"), rx.icon("github"),
                    rx.link(rx.code("https://github.com/leandrorojas/galadriel"), href="https://github.com/leandrorojas/galadriel"),
                    spacing="1"
            ),
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height=consts.RELATIVE_VIEWPORT_85,
    ),

    return about_content_var

def about_page() -> rx.Component:
    about_content_var = about_content()
    return base_page(about_content_var, rx.logo())