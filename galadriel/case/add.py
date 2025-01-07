import reflex as rx
import reflex_local_auth

from ..navigation import routes
from ..pages.add import add_page
from .forms import case_add_form

@reflex_local_auth.require_login
def case_add_page() -> rx.Component:
    return add_page(case_add_form, "New Test Case", "test-tubes", "to Cases", routes.CASES)