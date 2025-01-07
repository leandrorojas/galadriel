import reflex as rx
import reflex_local_auth

from ..navigation import routes
from ..pages.add import add_page
from .forms import scenario_add_form

@reflex_local_auth.require_login
def scenario_add_page() -> rx.Component:
    return add_page(scenario_add_form, "New Test Scenario", "route", "to Scenarios", routes.SCENARIOS)