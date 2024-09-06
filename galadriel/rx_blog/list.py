import reflex as rx
from ..rx_ui.base import rx_tutorial_base_page

from .. import rx_navigation
from . import state, model

def blog_post_detail_link(child: rx.Component, post: model.RxTutorialBlogPostModel):

    if post is None:
        return rx.fragment(child)
    
    post_id = post.id
    if post_id is None:
        return rx.fragment(child)

    root_path = rx_navigation.routes.BLOG_POSTS_ROUTE
    post_detail_url = f"{root_path}/{post_id}"

    return rx.link(
        child,
        href=post_detail_url
    )

def blog_post_list_item(post: model.RxTutorialBlogPostModel):
    return rx.box(
        blog_post_detail_link(
            rx.heading(post.title),
            post
        ),
        padding="1em"
    )

def blog_post_list_page() -> rx.Component:

    return rx_tutorial_base_page(
        rx.vstack(
            rx.heading("Blog Posts"),
            rx.link(
                rx.button("New Post"),
                href=rx_navigation.routes.BLOG_POST_ADD_ROUTE
            ),
            rx.foreach(state.RxTutorialBlogPostState.posts, blog_post_list_item),
            spacing="5",
            align="center",
            min_height="85vh"
        ),
    ),