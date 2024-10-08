import reflex as rx
import reflex_local_auth
from rxconfig import config

from .rx_ui.base import rx_tutorial_base_page
from .rx_auth.pages import rx_tutorial_login_page, rx_tutorial_signup_page, rx_tutorial_logout_page
from .rx_auth.state import RxTutorialSessionState

#demo
from . import rx_blog, rx_contact, rx_pages, rx_navigation

#old.galadriel
from . import navigation
from . import suite
from . import scenario
from . import case
from . import cycle

#galadriel
from .pages import base_page, about_page
from .pages import protetected_page
from .ui.components import Buttons
from .auth.pages import login_page, register_page, logout_page

from .auth.state import Session

class State(rx.State):
    """The app state."""
 
    ...

def index() -> rx.Component:
    galadriel_enabled = True

    if galadriel_enabled:
        buttons = Buttons()
        
        index_content = rx.vstack(
            rx.heading("Welcome to galadriel", size="9"),
            buttons.signup_and_login(),
            spacing="5",
            justify="center",
            align="center",
            min_height="85vh",
        ),
    
        return base_page(index_content)
    else:        
        # my_user_obj = RxTutorialSessionState.authenticated_user_info

        index_content = rx.vstack(
            #rx.heading(State.label, size="9"),
            # rx.text("just obj: ", my_user_obj.to_string()),
            # rx.text("tostr: ", my_user_obj.auth_user.to_string()),
            # rx.text("user: ", my_user_obj.auth_user.username),
            rx.text(
                "Get started by editing ",
                rx.code(f"{config.app_name}/{config.app_name}.py"),
                size="5",
            ),
            rx.link(
                rx.button("Check out our docs!"),
                href="https://reflex.dev/docs/getting-started/introduction/",
                is_external=True,
            ),
            spacing="5",
            justify="center",
            align="center",
            min_height="85vh",
        ),
    
        return rx_tutorial_base_page(index_content)

app = rx.App(
    theme = rx.theme(
        accent_color="violet",
    ),
    stylesheets=["https://fonts.googleapis.com/css?family=Montserrat",],
    style = {
        "font_family": "Montserrat",
        "font_size": "16px",        
    },
)

app.add_page(index, title="galadriel")

#galadriel pages
app.add_page(about_page, route=navigation.routes.ABOUT, title="About galadriel")
app.add_page(login_page, route=navigation.routes.LOGIN, title="Login")
app.add_page(register_page, route=navigation.routes.SIGNUP, title="Sign up")
app.add_page(logout_page, route=navigation.routes.LOGOUT, title="Logout")

#Test Suites
app.add_page(suite.suites_list_page, route=navigation.routes.SUITES, on_load=suite.SuiteState.load_suites)
app.add_page(suite.suite_add_page, route=navigation.routes.SUITE_ADD)
app.add_page(suite.suite_detail_page, route=navigation.routes.SUITE_DETAIL, on_load=suite.SuiteState.get_suite_detail)
app.add_page(suite.suite_edit_page, route=navigation.routes.SUITE_EDIT, on_load=suite.SuiteState.get_suite_detail)

#Test Scenarios
app.add_page(scenario.scenarios_list_page, route=navigation.routes.SCENARIOS, on_load=scenario.ScenarioState.load_scenarios)
app.add_page(scenario.scenario_add_page, route=navigation.routes.SCENARIO_ADD)
app.add_page(scenario.scenario_detail_page, route=navigation.routes.SCENARIO_DETAIL, on_load=scenario.ScenarioState.get_scenario_detail)
app.add_page(scenario.scenario_edit_page, route=navigation.routes.SCENARIO_EDIT, on_load=scenario.ScenarioState.get_scenario_detail)

#Test Cases
app.add_page(case.cases_list_page, route=navigation.routes.CASES, on_load=case.CaseState.load_cases)
app.add_page(case.case_add_page, route=navigation.routes.CASE_ADD)
app.add_page(case.case_detail_page, route=navigation.routes.CASE_DETAIL, on_load=case.CaseState.get_case_detail)
app.add_page(case.case_edit_page, route=navigation.routes.CASE_EDIT, on_load=case.CaseState.get_case_detail)

#Test Cycles
app.add_page(cycle.cycle_list_page, route=navigation.routes.CYCLES, on_load=cycle.CycleState.load_cycles)
app.add_page(cycle.cycle_add_page, route=navigation.routes.CYCLE_ADD)
app.add_page(cycle.cycle_detail_page, route=navigation.routes.CYCLE_DETAIL, on_load=cycle.CycleState.get_cycle_detail)
app.add_page(cycle.cycle_edit_page, route=navigation.routes.CYCLE_EDIT, on_load=cycle.CycleState.get_cycle_detail)

#protected test page
app.add_page(protetected_page, route="/protected_page", on_load=Session.on_load)

#reflex tutorial pages
# reflex_local_auth canned pages
# app.add_page(rx_tutorial_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE, title="Login")
# app.add_page(rx_tutorial_signup_page, route=reflex_local_auth.routes.REGISTER_ROUTE, title="Register")

# rx tutorial custom pages
# app.add_page(rx_tutorial_logout_page, route=navigation.routes.LOGOUT_ROUTE, title="Logout")
app.add_page(rx_pages.rx_tutorial_about_page, route=rx_navigation.routes.ABOUT_ROUTE)
app.add_page(rx_contact.contact_page, route=rx_navigation.routes.CONTACT_ROUTE)

#app.add_page(pages.protected_page, route="/protected_page", on_load=RxTutorialSessionState.on_load)

app.add_page(rx_contact.contact_entries_list_page, route=rx_navigation.routes.CONTACT_ENTRIES_ROUTE, on_load=rx_contact.RxTutorialContactState.list_entries)

app.add_page(rx_blog.blog_post_list_page, route=rx_navigation.routes.BLOG_POSTS_ROUTE, on_load=rx_blog.RxTutorialBlogPostState.load_posts)
app.add_page(rx_blog.blog_post_add_page, route=rx_navigation.routes.BLOG_POST_ADD_ROUTE)
app.add_page(rx_blog.blog_post_detail_page, route=rx_navigation.routes.BLOG_POST_DETAIL_ROUTE, on_load=rx_blog.RxTutorialBlogPostState.get_post_detail)
app.add_page(rx_blog.blog_post_edit_page, route=rx_navigation.routes.BLOG_POST_EDIT_ROUTE, on_load=rx_blog.RxTutorialBlogPostState.get_post_detail)

#Pricing
app.add_page(rx_pages.rx_tutorial_pricing_page, route=rx_navigation.routes.PRICING_ROUTE)
app.add_page(rx_pages.rx_tutorial_pricing_page, route=rx_navigation.routes.PRICING_ROUTE)