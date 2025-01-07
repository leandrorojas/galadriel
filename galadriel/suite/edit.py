import reflex as rx
import reflex_local_auth

from .forms import suite_edit_form
from .state import EditSuiteState
from ..navigation import routes
from ..pages.edit import edit_page

@reflex_local_auth.require_login
def suite_edit_page() -> rx.Component:
    return edit_page(suite_edit_form, "Edit Test Suite", "route", "to Suites", "to Suite Detail", routes.SUITES, EditSuiteState.suite_url)