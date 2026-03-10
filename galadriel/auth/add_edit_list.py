"""User list page for administration."""

import reflex as rx
from ..user import state, model
from ..navigation import routes
from ..pages import base_page

from ..ui.components import Table, PageHeader, Moment
from ..utils import consts
from ..auth.state import require_login, Session

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
@require_login
def users_list_page() -> rx.Component:
    """Render the users list page."""
    header_component = PageHeader()

    return base_page(
        rx.vstack(
            header_component.list("Users", consts.ICON_USERS, "Add User", routes.USER_ADD, Session.is_admin, "Galadriel Users"), # Add User button enabled only for admins
            rx.scroll_area(__table(), type="hover", scrollbars="vertical", style={"height": consts.RELATIVE_VIEWPORT_85},),
            spacing="5", align="center", min_height=consts.RELATIVE_VIEWPORT_85,
        ),
    )
#endregion

# #region ADD
# @require_login
# def case_add_page() -> rx.Component:
#     return add_page(case_add_form, "New Test Case", consts.ICON_TEST_TUBES, "to Cases", routes.CASES)
# #endregion

# #region EDIT
# @require_login
# def case_edit_page() -> rx.Component:
#     return edit_page(case_edit_form, "Edit Test Case", consts.ICON_TEST_TUBES, "to Cases", "to Case Detail", routes.CASES, state.EditCaseState.case_url)
# #endregion