"""Authentication forms for login and user registration."""

import reflex as rx
from reflex_local_auth.pages.login import LoginState
from reflex_local_auth.pages.registration import RegistrationState
from reflex_local_auth.pages.components import input_100w, MIN_WIDTH
from .state import Register, Login

def __login_error() -> rx.Component:
    """Render the login error message."""
    return rx.cond(
        LoginState.error_message != "",
        rx.callout(
            LoginState.error_message,
            icon="triangle_alert",
            color_scheme="red",
            role="alert",
            width="100%",
        ),
    )

def __pending_approval() -> rx.Component:
    """Render the pending approval callout after self-registration."""
    return rx.cond(
        Login.pending_approval,
        rx.callout(
            rx.vstack(
                rx.text("Registration successful!", weight="bold", size="2"),
                rx.text("Your account is pending admin approval.", size="2"),
                rx.text("You will be able to log in once an administrator activates your account.", size="2"),
                spacing="1",
            ),
            icon="info",
            color_scheme="blue",
            size="1",
            width="100%",
        ),
    )

def login_form() -> rx.Component:
    """Render the login form with autofocus on the username field."""
    return rx.form(
        rx.vstack(
            rx.heading("Log in to your account", size="7"),
            __pending_approval(),
            __login_error(),
            rx.el.label("Username", html_for="username"),
            input_100w("username", auto_focus=True),
            rx.el.label("Password", html_for="password"),
            input_100w("password", type="password"),
            rx.button("Sign in", width="100%"),
            rx.center(
                rx.link("Register", on_click=RegistrationState.redir),
                width="100%",
            ),
            min_width=MIN_WIDTH,
        ),
        on_submit=Login.on_submit,
    )

def __register_error() -> rx.Component:
    """Render the registration error message."""
    return rx.cond(
        RegistrationState.error_message != "",
        rx.callout(
            RegistrationState.error_message,
            icon="triangle_alert",
            color_scheme="red",
            role="alert",
            width="100%",
        ),
    )

def register_form() -> rx.Component:
    """Render the registration form."""
    return rx.form(
        rx.vstack(
            rx.heading("Create an account", size="7"),
            __register_error(),
            rx.el.label("Username", html_for="username"),
            input_100w("username"),
            rx.el.label("Email", html_for="email"),
            input_100w("email", type="email"),
            rx.el.label("Password", html_for="password"),
            input_100w("password", type="password"),
            rx.el.label("Confirm Password", html_for="confirm_password"),
            input_100w("confirm_password", type="password"),
            rx.button("Sign up", width="100%"),
            rx.center(
                rx.link("Login", on_click=LoginState.redir),
                width="100%",
            ),
            min_width=MIN_WIDTH,
        ),
        on_submit=Register.handle_registration_email,
    )
