import reflex as rx
from reflex_local_auth.pages.login import LoginState, login_form
from reflex_local_auth.pages.registration import RegistrationState
from .forms import my_register_form
from .. import navigation
from .state import SessionState

from ..ui.base import base_page

def my_login_page() -> rx.Component:
    return base_page(
        rx.center(
            rx.cond(
                LoginState.is_hydrated,  # type: ignore
                rx.card(login_form()),
            ),
            min_height="85vh",
        )
    )

def my_signup_page() -> rx.Component:
    return base_page(
        rx.center(
            rx.cond(
                RegistrationState.success,
                rx.vstack(
                    rx.text("Registration successful!"),
                ),
                rx.card(my_register_form()),
            ),
            min_height="85vh",
        ) 
    )

def my_logout_page() -> rx.Component:
    index_content = rx.vstack(
        rx.heading("Are you sure you want to logoxut?", size="7"),
        rx.hstack(
            rx.link(rx.button("No", color_scheme="gray"), href=(navigation.routes.HOME_ROUTE)),
            rx.button("Yes, log me out", on_click=SessionState.perform_logout),
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return base_page(index_content)