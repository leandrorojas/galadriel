import reflex as rx
import reflex_local_auth

from .state import EditScenarioState
from ..navigation import routes

from .forms import scenario_edit_form
from ..pages.edit import edit_page

@reflex_local_auth.require_login
def scenario_edit_page() -> rx.Component:
    return edit_page(scenario_edit_form, "Edit Test Scenario", "route", "to Scenarios", "to Scenario Detail", routes.SCENARIOS, EditScenarioState.scenario_url)