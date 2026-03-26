"""Main application entry point: page registration, theming, and first-run seeding."""

import reflex as rx

#old.galadriel
from . import navigation
from . import suite
from . import scenario
from . import case
from . import cycle
from . import install
from . import dashboard
from . import user
from . import settings
from .utils import consts
from .utils import yaml  # local yaml.py with PyYAML helpers

from .auth import add_edit_list as user_add_edit_list
from .auth import detail as user_detail

#galadriel
from .pages import base_page, about_page, about_content, not_found_page
from .ui.components import Button
from .auth.pages import login_page, register_page, logout_page
from .auth.state import Login

from .auth.state import Session

def index() -> rx.Component:
    buttons = Button()
    
    index_content = rx.cond(
        Session.is_authenticated,
        about_content(),
        rx.vstack(
            rx.heading("Welcome to galadriel", size="9"),
            buttons.signup_and_login(),
            spacing="5",
            justify="center",
            align="center",
            min_height=consts.RELATIVE_VIEWPORT_85,
        ),
    ),

    return base_page(index_content)

app = rx.App(
    theme = rx.theme(
        accent_color="violet",
    ),
    stylesheets=["https://fonts.googleapis.com/css?family=Montserrat", "suneditor-dark.css", "sticky-table.css"],
    style = {
        "font_family": "Montserrat",
        "font_size": "16px",
    },
)

if not(yaml.read_setting("galadriel.yaml", "galadriel", "first_run")):
    try: # reflex db init run fails, this should run after the db is initialized
        seed = install.seed
        seed.seed_db()
        seed.set_first_run()
        yaml.write_setting("galadriel.yaml", "galadriel", "first_run", 1)
    except Exception as e:
        print(f"[galadriel] seed failed: {e}")

app.add_page(index, title="galadriel")

#galadriel pages
app.add_page(about_page, route=navigation.routes.ABOUT, title="About galadriel")
app.add_page(login_page, route=navigation.routes.LOGIN, title="Login", on_load=Login.clear_error)
app.add_page(register_page, route=navigation.routes.SIGNUP, title="Sign up", on_load=Login.clear_pending_approval)
app.add_page(logout_page, route=navigation.routes.LOGOUT, title="Logout")

#Test Suites
app.add_page(suite.suites_list_page, route=navigation.routes.SUITES, on_load=[Session.on_load, Session.require_non_admin, suite.SuiteState.load_suites])
app.add_page(suite.suite_add_page, route=navigation.routes.SUITE_ADD, on_load=[Session.on_load, Session.require_non_admin, Session.require_editor])
app.add_page(suite.suite_detail_page, route=navigation.routes.SUITE_DETAIL, on_load=[Session.on_load, Session.require_non_admin, suite.SuiteState.get_suite_detail])
app.add_page(suite.suite_edit_page, route=navigation.routes.SUITE_EDIT, on_load=[Session.on_load, Session.require_non_admin, Session.require_editor, suite.SuiteState.get_suite_detail])

#Test Scenarios
app.add_page(scenario.scenarios_list_page, route=navigation.routes.SCENARIOS, on_load=[Session.on_load, Session.require_non_admin, scenario.ScenarioState.load_scenarios])
app.add_page(scenario.scenario_add_page, route=navigation.routes.SCENARIO_ADD, on_load=[Session.on_load, Session.require_non_admin, Session.require_editor])
app.add_page(scenario.scenario_detail_page, route=navigation.routes.SCENARIO_DETAIL, on_load=[Session.on_load, Session.require_non_admin, scenario.ScenarioState.get_scenario_detail])
app.add_page(scenario.scenario_edit_page, route=navigation.routes.SCENARIO_EDIT, on_load=[Session.on_load, Session.require_non_admin, Session.require_editor, scenario.ScenarioState.get_scenario_detail])

#Test Cases
app.add_page(case.cases_list_page, route=navigation.routes.CASES, on_load=[Session.on_load, Session.require_non_admin, case.CaseState.load_cases])
app.add_page(case.case_add_page, route=navigation.routes.CASE_ADD, on_load=[Session.on_load, Session.require_non_admin, Session.require_editor, case.AddCaseState.clear_form])
app.add_page(case.case_detail_page, route=navigation.routes.CASE_DETAIL, on_load=[Session.on_load, Session.require_non_admin, case.CaseState.get_case_detail])
app.add_page(case.case_edit_page, route=navigation.routes.CASE_EDIT, on_load=[Session.on_load, Session.require_non_admin, Session.require_editor, case.CaseState.get_case_detail])

#Test Cycles
app.add_page(cycle.cycle_list_page, route=navigation.routes.CYCLES, on_load=[Session.on_load, Session.require_non_admin, cycle.CycleState.load_cycles])
app.add_page(cycle.cycle_add_page, route=navigation.routes.CYCLE_ADD, on_load=[Session.on_load, Session.require_non_admin, Session.require_editor, cycle.AddCycleState.clear_form])
app.add_page(cycle.cycle_detail_page, route=navigation.routes.CYCLE_DETAIL, on_load=[Session.on_load, Session.require_non_admin, cycle.CycleState.get_cycle_detail])
app.add_page(cycle.cycle_edit_page, route=navigation.routes.CYCLE_EDIT, on_load=[Session.on_load, Session.require_non_admin, Session.require_editor, cycle.CycleState.get_cycle_detail])
app.add_page(cycle.iteration_page, route=navigation.routes.CYCLE_ITERATION_DETAIL, on_load=[Session.on_load, Session.require_non_admin])

#Dashboard
app.add_page(dashboard.dashboard_page, route=navigation.routes.DASHBOARD, on_load=[Session.on_load, Session.require_non_admin, dashboard.DashboardState.load_dashboard])

# Settings
app.add_page(settings.settings_page, route=navigation.routes.SETTINGS, on_load=[Session.on_load, Session.require_super_admin])

# Users
app.add_page(user_add_edit_list.users_list_page, route=navigation.routes.USERS, on_load=[Session.on_load, Session.require_admin, user.UserState.load_users])
app.add_page(user_add_edit_list.user_add_page, route=navigation.routes.USER_ADD, on_load=[Session.on_load, Session.require_admin, user.UserState.load_assignable_roles])
app.add_page(user_detail.user_detail_page, route=navigation.routes.USER_DETAIL, on_load=[Session.on_load, Session.require_admin, user.UserState.get_user_detail])
app.add_page(user_add_edit_list.user_edit_page, route=navigation.routes.USER_EDIT, on_load=[Session.on_load, Session.require_admin, user.EditUserState.load_edit_user])

# Custom 404
app.add_page(not_found_page, route="/404", title="404 - Not Found")