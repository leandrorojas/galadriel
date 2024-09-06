import reflex as rx
from .state import RxTutorialBlogEditFormState, RxTutorialBlogAddPostFormState

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
        on_submit=RxTutorialBlogAddPostFormState.handle_submit,
        reset_on_submit=True,
    ),

def blog_post_edit_form() -> rx.Component:

    post = RxTutorialBlogEditFormState.post
    title = post.title
    publish_active = post.publish_active
    post_content = RxTutorialBlogEditFormState.post_content

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
                on_change=RxTutorialBlogEditFormState.set_post_content,
                name="content",
                placeholder="que dice el post?",
                required=True,
                height="50vh",
                width="100%", 
            ),
            rx.flex(
                rx.switch(
                    default_checked=RxTutorialBlogEditFormState.post_publish_active, 
                    name="publish_active",
                    on_change=RxTutorialBlogEditFormState.set_post_publish_active,
                    ),
                rx.text("Publish Active"),
                spacing="2",
            ),
            rx.cond(
                RxTutorialBlogEditFormState.post_publish_active,
                rx.box(
                    rx.hstack(
                        rx.input(
                            default_value=RxTutorialBlogEditFormState.publish_display_date,
                            type="date",
                            name="publish_date",
                            width="100%",
                        ),
                        rx.input(
                            default_value=RxTutorialBlogEditFormState.publish_display_time,
                            type="time",
                            name="publish_time",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    width="100%",
                ),
            ),
            rx.button("Submit", type="submit", width="100%",),
        ),
        on_submit=RxTutorialBlogEditFormState.handle_submit,
    ),