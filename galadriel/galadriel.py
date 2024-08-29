import reflex as rx
import reflex_local_auth
from rxconfig import config

from .ui.base import base_page
from .auth.pages import my_login_page, my_signup_page, my_logout_page
from .auth.state import SessionState

#demo
from . import blog, contact, pages, navigation

#galadriel
from . import suite

class State(rx.State):
    """The app state."""

    ...

def index() -> rx.Component:
    index_content = rx.vstack(
        rx.text(
            "Get started by editing ",
            rx.code(f"{config.app_name}/{config.app_name}.py"),
            size="5",
        ),
        rx.link(
            rx.button("Check out our docs!"),
            href="https://reflex.dev/docs/getting-started/introduction/",
            is_extgsernal=True,
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return base_page(index_content)

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
app.add_page(index)

#reflex_local_auth canned page
app.add_page(
    my_login_page,
    route=reflex_local_auth.routes.LOGIN_ROUTE,
    title="Login",
)
#reflex_local_auth canned page
app.add_page(
    my_signup_page,
    route=reflex_local_auth.routes.REGISTER_ROUTE,
    title="Register",
)

#custom pages
app.add_page(my_logout_page, route=navigation.routes.LOGOUT_ROUTE, title="Logout")
app.add_page(pages.about_page, route=navigation.routes.ABOUT_ROUTE)
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_ROUTE)

app.add_page(pages.protected_page, route="/protected_page", on_load=SessionState.on_load)

app.add_page(
    contact.contact_entries_list_page, 
    route=navigation.routes.CONTACT_ENTRIES_ROUTE,
    on_load=contact.ContactState.list_entries
)

app.add_page(
    blog.blog_post_list_page,
    route=navigation.routes.BLOG_POSTS_ROUTE,
    on_load=blog.BlogPostState.load_posts
)

app.add_page(
    blog.blog_post_add_page,
    route=navigation.routes.BLOG_POST_ADD_ROUTE,
)

app.add_page(
    blog.blog_post_detail_page,
    route=navigation.routes.BLOG_POST_DETAIL_ROUTE,
    on_load=blog.BlogPostState.get_post_detail
)

app.add_page(
    blog.blog_post_edit_page,
    route=navigation.routes.BLOG_POST_EDIT_ROUTE,
    on_load=blog.BlogPostState.get_post_detail
)

#Test Suites
app.add_page(
    suite.suites_list_page, 
    route=navigation.routes.SUITES_ROUTE, 
    on_load=suite.SuiteState.load_suites
)
app.add_page(
    suite.suite_add_page, 
    route=navigation.routes.SUITE_ADD_ROUTE
)
app.add_page(
    suite.suite_detail_page, 
    route=navigation.routes.SUITE_DETAIL_ROUTE, 
    on_load=suite.SuiteState.get_suite_detail
)

app.add_page(
    suite.suite_edit_page, 
    route=navigation.routes.SUITE_EDIT_ROUTE, 
    on_load=suite.SuiteState.get_suite_detail
)

#Pricing
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)