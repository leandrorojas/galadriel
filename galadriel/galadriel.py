import reflex as rx
import reflex_local_auth
from rxconfig import config

from .ui.rx_base import rx_tutorial_base_page
from .auth.pages import rx_tutorial_login_page, rx_tutorial_signup_page, rx_tutorial_logout_page
from .auth.state import RxTutorialSessionState

#demo
from . import blog, contact, pages, navigation

#old.galadriel
from . import suite
from . import scenario

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
        accent_color="violet"
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


app.add_page(protetected_page, route="/protected_page", on_load=Session.on_load)

# reflex_local_auth canned pages
# app.add_page(rx_tutorial_login_page, route=reflex_local_auth.routes.LOGIN_ROUTE, title="Login")
# app.add_page(rx_tutorial_signup_page, route=reflex_local_auth.routes.REGISTER_ROUTE, title="Register")

# rx tutorial custom pages
# app.add_page(rx_tutorial_logout_page, route=navigation.rx_routes.RX_TUTORIAL_LOGOUT_ROUTE, title="Logout")
app.add_page(pages.rx_tutorial_about_page, route=navigation.rx_routes.RX_TUTORIAL_ABOUT_ROUTE)
app.add_page(contact.contact_page, route=navigation.rx_routes.RX_TUTORIAL_CONTACT_ROUTE)

#app.add_page(pages.rx_tutorial_protected_page, route="/protected_page", on_load=RxTutorialSessionState.on_load)

app.add_page(contact.contact_entries_list_page, route=navigation.rx_routes.RX_TUTORIAL_CONTACT_ENTRIES_ROUTE, on_load=contact.ContactState.list_entries)

app.add_page(blog.blog_post_list_page, route=navigation.rx_routes.RX_TUTORIAL_BLOG_POSTS_ROUTE, on_load=blog.BlogPostState.load_posts)
app.add_page(blog.blog_post_add_page, route=navigation.rx_routes.RX_TUTORIAL_BLOG_POST_ADD_ROUTE)
app.add_page(blog.blog_post_detail_page, route=navigation.rx_routes.RX_TUTORIAL_BLOG_POST_DETAIL_ROUTE, on_load=blog.BlogPostState.get_post_detail)
app.add_page(blog.blog_post_edit_page, route=navigation.rx_routes.RX_TUTORIAL_BLOG_POST_EDIT_ROUTE, on_load=blog.BlogPostState.get_post_detail)

#Pricing
app.add_page(pages.rx_tutorial_pricing_page, route=navigation.rx_routes.RX_TUTORIAL_PRICING_ROUTE)
app.add_page(pages.rx_tutorial_pricing_page, route=navigation.rx_routes.RX_TUTORIAL_PRICING_ROUTE)