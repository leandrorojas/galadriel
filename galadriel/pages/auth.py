import reflex as rx
from reflex_local_auth.pages.login import LoginState, login_form
from reflex_local_auth.pages.registration import RegistrationState
from ..auth.forms import rx_tutorial_register_form
from .. import navigation
from ..auth.state import RxTutorialSessionState

from ..ui.rx_base import rx_tutorial_base_page

from .base import base_page
from ..forms import auth
from ..states.auth import Session

def login() -> rx.Component:
    return base_page(
        rx.center(
            rx.cond(
                LoginState.is_hydrated,  # type: ignore
                rx.card(auth.login()),
            ),
            min_height="85vh",
        )
    )

def signup() -> rx.Component:
    return base_page(
        rx.center(
            rx.cond(
                RegistrationState.success,
                rx.vstack(
                    rx.text("Registration successful!"),
                ),
                rx.card(auth.sign_up()),
            ),
            min_height="85vh",
        ) 
    )

def logout() -> rx.Component:
    logout_content = rx.vstack(
        rx.heading("Are you sure you want to logout?", size="7"),
        rx.hstack(
            rx.link(rx.button("No", color_scheme="gray"), href=(navigation.rx_routes.RX_TUTORIAL_HOME_ROUTE)),
            rx.button("Yes, log me out", on_click=Session.perform_logout),
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return base_page(logout_content)