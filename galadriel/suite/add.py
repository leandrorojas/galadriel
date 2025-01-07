import reflex as rx
import reflex_local_auth

from ..navigation import routes
from ..pages.add import add_page
from .forms import suite_add_form

@reflex_local_auth.require_login
def suite_add_page() -> rx.Component:
    return add_page(suite_add_form, "New Test Suite", "beaker", "to Suites", routes.SUITES)