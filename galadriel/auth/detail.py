import reflex as rx
import reflex_local_auth

from ..navigation import routes
from ..user import state
from ..pages import base_page
from ..ui.components import Badge, Button, MomentBadge

from ..utils import consts

@reflex_local_auth.require_login
def user_detail_page() -> rx.Component:
    title_badge = Badge()
    can_edit = True
    button_component = Button()
    moment_badge_component = MomentBadge()

    edit_link_element = rx.cond(
        can_edit,
        button_component.edit(state.UserState.user_edit_url),
        rx.fragment("")
    )

    user_detail_content = rx.vstack(
        rx.flex(
            title_badge.title("user", "User Detail"),
            rx.spacer(),
            rx.hstack(button_component.to_list("to Users", routes.USERS), edit_link_element),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",
        ),
        rx.hstack(
            rx.heading(f"{state.UserState.user.username}", size="7",),
            moment_badge_component.moment_badge(state.UserState.user.created),
            rx.hstack(
                rx.icon("mail"), rx.text(state.UserState.user.email, size="5",),
                rx.icon("toggle-right"), rx.text(state.UserState.user.enabled, size="5",),
            ),
            align="center",
        ),

        spacing="5",
        align="start",
        min_height=consts.RELATIVE_VIEWPORT_85,
    ),
    
    return base_page(user_detail_content)