import reflex as rx
from reflex_local_auth.pages.login import LoginState, login_form
from reflex_local_auth.pages.registration import RegistrationState
from .forms import register_form
from ..pages.base import base_page
from ..pages.about import about_content
from .. import navigation
from .state import Session
from ..utils import consts

def login_page() -> rx.Component:
    return base_page(
        rx.cond(
            ~LoginState.is_authenticated, # "~" equals "not" (in this case not authenticated)
            rx.center(
                rx.cond(
                    LoginState.is_hydrated,  # type: ignore
                    rx.card(login_form()),
                ),
                min_height=consts.RELATIVE_VIEWPORT_85,
            ),
            rx.container(about_content())
        )
    )

def register_page() -> rx.Component:
    return base_page(
        rx.cond(
            ~LoginState.is_authenticated,
            rx.center(
                rx.cond(
                    RegistrationState.success,
                    rx.vstack(
                        rx.text("Registration successful!"),
                    ),
                    rx.card(register_form()),
                ),
                min_height=consts.RELATIVE_VIEWPORT_85,
            ),
            rx.container(about_content())
        )
    )

def logout_page() -> rx.Component:
    return base_page(
        rx.vstack(
            rx.heading("Are you sure you want to logout?", size="7"),
            rx.hstack(
                rx.link(rx.button("No", color_scheme="gray"), href=(navigation.routes.HOME)),
                rx.button("Yes, log me out", on_click=Session.perform_logout),
            ),
            spacing="5",
            justify="center",
            align="center",
            min_height=consts.RELATIVE_VIEWPORT_85,
        ),
    )