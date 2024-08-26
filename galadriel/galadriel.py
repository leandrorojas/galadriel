import reflex as rx
from rxconfig import config

from .ui.base import base_page

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
app.add_page(pages.about_page, route=navigation.routes.ABOUT_ROUTE)
app.add_page(contact.contact_page, route=navigation.routes.CONTACT_ROUTE)

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
    route="/blog/[blog_id]",
    on_load=blog.BlogPostState.get_post_detail
)

app.add_page(
    blog.blog_post_edit_page,
    route="/blog/[blog_id]/edit",
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
    route="/suites/[id]", 
    on_load=suite.SuiteState.get_suite_detail
)

app.add_page(
    suite.blog_post_edit_page, 
    route="/suites/[id]/edit", 
    on_load=suite.SuiteState.get_suite_detail
)

#Pricing
app.add_page(pages.pricing_page, route=navigation.routes.PRICING_ROUTE)