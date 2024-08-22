import reflex as rx
from ..ui.base import base_page

from .. import navigation
from . import state

def blog_post_detail_page() -> rx.Component:
    about_content = rx.vstack(
        rx.heading(f"Blog Post Detail for {state.BlogPostState.post.title}"),
        rx.text(f"[{state.BlogPostState.blog_post_id}]"),
        rx.text(
            state.BlogPostState.post.content,
            size="5",
        ),
        rx.link(
            rx.button("Check out our ducks!"),
            href=navigation.routes.HOME_ROUTE,
            is_extgsernal=True,
        ),
        spacing="5",
        align="center",
        min_height="85vh",
    ),
    
    return base_page(about_content)