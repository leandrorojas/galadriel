import reflex as rx
import reflex_local_auth

from ..navigation import routes
from ..pages.add import add_page
from .forms import cycle_add_form

@reflex_local_auth.require_login
def cycle_add_page() -> rx.Component:
    return add_page(cycle_add_form, "New Cycle", "flask-round", "to Cycles", routes.CYCLES)