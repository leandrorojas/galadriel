import reflex as rx
import reflex_local_auth

from .forms import cycle_edit_form
from .state import EditCycleState
from ..navigation import routes
from ..pages.edit import edit_page

@reflex_local_auth.require_login
def cycle_edit_page() -> rx.Component:
    return edit_page(cycle_edit_form, "Edit Test Cycle", "beaker", "to Cycles", "back to Detail", routes.CYCLES, EditCycleState.cycle_url)