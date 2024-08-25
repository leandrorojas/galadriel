import reflex as rx
from .state import BlogAEditFormState, BlogAddPostFormState

def blog_post_add_form() -> rx.Component:

    return rx.form(
        rx.vstack(
                rx.input(
                    name="title",
                    placeholder="Title",
                    width="100%",
                ),
            rx.text_area(
                name="content",
                placeholder="que dice el post?",
                required=True,
                height="50vh",
                width="100%",
            ),
            rx.button("Submit", type="submit", width="100%",),
        ),
        on_submit=BlogAddPostFormState.handle_submit,
        reset_on_submit=True,
    ),

def blog_post_edit_form() -> rx.Component:

    post = BlogAEditFormState.post
    title = post.title
    post_content = BlogAEditFormState.post_content

    return rx.form(
        rx.box(
            rx.input(
                type="hidden",
                name="post_id",
                value=post.id
            ),
            display="none",
        ),
        rx.vstack(
                rx.input(
                    default_value=title,
                    name="title",
                    placeholder="Title",
                    width="100%",
                ),
            rx.text_area(
                value=post_content,
                on_change=BlogAEditFormState.set_post_content,
                name="content",
                placeholder="que dice el post?",
                required=True,
                height="50vh",
                width="100%",
            ),
            rx.button("Submit", type="submit", width="100%",),
        ),
        on_submit=BlogAEditFormState.handle_submit,
    ),