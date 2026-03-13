"""User list and add pages for administration."""

import reflex as rx
from ..user import state, model
from ..navigation import routes
from ..pages import base_page
from ..pages.add import add_page

from ..ui.components import Table, PageHeader, Moment
from ..utils import consts
from ..auth.state import require_admin, Session

def __user_detail_link(child: rx.Component, galadriel_user: model.GaladrielUserDisplay):
    if galadriel_user is None: return rx.fragment(child)
    
    user_id = galadriel_user.galadriel_user_id

    if user_id is None: return rx.fragment(child)

    root_path = routes.USERS
    user_detail_url = f"{root_path}/{user_id}"

    return rx.link(child, href=user_detail_url)

def __show_user(galadriel_user:model.GaladrielUserDisplay):
    moment_component = Moment()
    return rx.table.row(
        rx.table.cell(__user_detail_link(galadriel_user.username, galadriel_user)),
        rx.table.cell(galadriel_user.email),
        rx.table.cell(galadriel_user.role),
        rx.table.cell(galadriel_user.enabled),
        rx.table.cell(moment_component.moment(galadriel_user.created))
    )

def __table() -> rx.Component:
    table_component = Table()
    return rx.fragment(
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    Table.sortable_header("username", "user-cog", "username", state.UserState.sort_by, state.UserState.sort_asc, state.UserState.toggle_sort),
                    Table.sortable_header("email", "mail", "email", state.UserState.sort_by, state.UserState.sort_asc, state.UserState.toggle_sort),
                    Table.sortable_header("role", "scan-eye", "role", state.UserState.sort_by, state.UserState.sort_asc, state.UserState.toggle_sort),
                    table_component.header("enabled", "toggle-right"),
                    Table.sortable_header("created", "calendar-check-2", "created", state.UserState.sort_by, state.UserState.sort_asc, state.UserState.toggle_sort),
                ),

            ),
            rx.table.body(rx.foreach(state.UserState.sorted_users, __show_user)),
            variant="surface",
            size="3",
            width="100%",
            on_mount=state.UserState.load_users,
        ),
    )

#region #LIST
@require_admin
def users_list_page() -> rx.Component:
    """Render the users list page."""
    header_component = PageHeader()

    return base_page(
        rx.vstack(
            header_component.list("Users", consts.ICON_USERS, "Add User", routes.USER_ADD, Session.is_admin, "Galadriel Users"),
            __table(),
            spacing="5", align="center", min_height=consts.RELATIVE_VIEWPORT_85,
        ),
    )
#endregion

#region ADD
def __user_add_form() -> rx.Component:
    """Render the form for adding a new user."""
    return rx.fragment(
        rx.form(
            rx.vstack(
                rx.input(name="username", placeholder="Username", width="100%"),
                rx.input(name="email", placeholder="Email", width="100%"),
                rx.select(
                    state.UserState.assignable_roles,
                    name="role",
                    placeholder="Select a role",
                    width="100%",
                ),
                rx.callout(
                    "A strong password will be auto-generated for the new user.",
                    icon="info",
                    color_scheme="blue",
                    width="100%",
                ),
                rx.button("Add User", type="submit", width="100%"),
                spacing="3",
            ),
            on_submit=state.AddUserState.handle_submit,
            reset_on_submit=False,
        ),
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title("User Created"),
                rx.dialog.description("Copy the generated password and send it to the new user. This password will not be shown again."),
                rx.vstack(
                    rx.text("Generated password:", weight="bold", size="2"),
                    rx.flex(
                        rx.code(state.AddUserState.generated_password, size="3"),
                        rx.icon_button(
                            rx.icon("copy", size=16),
                            size="1",
                            variant="ghost",
                            on_click=rx.set_clipboard(state.AddUserState.generated_password),
                        ),
                        align="center",
                        spacing="2",
                    ),
                    spacing="2",
                    width="100%",
                    padding_top="1em",
                    padding_bottom="1em",
                ),
                rx.dialog.close(
                    rx.button("Done", width="100%", on_click=state.AddUserState.close_password_dialog),
                ),
                padding="1.5em",
            ),
            open=state.AddUserState.show_password_dialog,
        ),
    )


@require_admin
def user_add_page() -> rx.Component:
    """Render the add user page."""
    return add_page(__user_add_form, "New User", consts.ICON_USERS, "to Users", routes.USERS)
#endregion