import reflex as rx
import reflex_local_auth

from .state import EditCaseState
from ..navigation import routes

from .forms import case_edit_form
from ..pages.edit import edit_page

from ..utils import consts

@reflex_local_auth.require_login
def case_edit_page() -> rx.Component:
    return edit_page(case_edit_form, "Edit Test Case", consts.ICON_TEST_TUBES, "to Cases", "to Case Detail", routes.CASES, EditCaseState.case_url)