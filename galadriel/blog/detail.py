import reflex as rx
from ..ui.base import rx_tutorial_base_page

from .. import navigation
from . import state

def blog_post_detail_page() -> rx.Component:
    can_edit = True
    edit_link = rx.link("Edit", href=f"{state.BlogPostState.blog_post_edit_url}") #convert to button, like in line 28?
    
    edit_link_element = rx.cond(
        can_edit,
        edit_link,
        rx.fragment("")
    )

    my_child = rx.vstack(
        rx.hstack(
            rx.heading(f"Blog Post Detail for {state.BlogPostState.post.title}"),
            edit_link_element,
            align="center"
        ),
        rx.text(f"[{state.BlogPostState.blog_post_id}]"),
        rx.text(f"{state.BlogPostState.post.published}"),
        rx.text(
            state.BlogPostState.post.content,
            size="5",
            white_space='pre-wrap',
        ),
        rx.link(
            rx.button("Check out our ducks!"),
            href=navigation.rx_routes.RX_TUTORIAL_HOME_ROUTE,
            is_extgsernal=True,
        ),
        spacing="5",
        align="center",
        min_height="85vh",
    ),
    
    return rx_tutorial_base_page(my_child)