"""Authentication state, session management, and role-based access control."""

import reflex as rx
import reflex_local_auth
from reflex_local_auth.login import LoginState
import sqlmodel

from typing import Optional

from ..user.model import GaladrielUser, GaladrielUserRole
from ..user.state import UserRole


def require_login(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    """Custom require_login that redirects unauthenticated users to login and admin/user_admin users to /users."""
    def protected_page():
        return rx.fragment(
            rx.cond(
                LoginState.is_hydrated & LoginState.is_authenticated & ~Session.is_admin,
                page(),
                rx.cond(
                    LoginState.is_hydrated & LoginState.is_authenticated & Session.is_admin,
                    rx.center(
                        rx.spinner(size="3"),
                        min_height="100vh",
                        on_mount=Session.require_non_admin,
                    ),
                    rx.center(
                        rx.spinner(size="3"),
                        min_height="100vh",
                        on_mount=LoginState.redir,
                    ),
                ),
            )
        )
    protected_page.__name__ = page.__name__
    return protected_page


def require_editor(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    """Wrap a page so only editor (and above) users see it; viewers get a spinner then redirect."""
    def editor_page():
        return rx.fragment(
            rx.cond(
                LoginState.is_hydrated & LoginState.is_authenticated & (Session.role != UserRole.VIEWER),
                page(),
                rx.center(
                    rx.spinner(size="3"),
                    min_height="100vh",
                    on_mount=Session.require_editor,
                ),
            )
        )
    editor_page.__name__ = page.__name__
    return editor_page


def require_admin(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    """Wrap a page so only admin/user_admin users see it; others get a spinner then redirect."""
    def admin_page():
        return rx.fragment(
            rx.cond(
                LoginState.is_hydrated & LoginState.is_authenticated & Session.is_admin,
                page(),
                rx.center(
                    rx.spinner(size="3"),
                    min_height="100vh",
                ),
            )
        )
    admin_page.__name__ = page.__name__
    return admin_page


def require_super_admin(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    """Wrap a page so only admin users see it; user_admin and others get a spinner then redirect."""
    def super_admin_page():
        return rx.fragment(
            rx.cond(
                LoginState.is_hydrated & LoginState.is_authenticated & Session.is_super_admin,
                page(),
                rx.center(
                    rx.spinner(size="3"),
                    min_height="100vh",
                ),
            )
        )
    super_admin_page.__name__ = page.__name__
    return super_admin_page

PENDING_APPROVAL_MESSAGE = "Registration successful! Your account is pending admin approval. You will be able to log in once an administrator activates your account."

class Login(LoginState):
    """Extends LoginState with additional event handlers."""

    pending_approval: bool = False

    def clear_error(self):
        """Clear the login error message."""
        self.error_message = ""

    def clear_pending_approval(self):
        """Clear the pending approval banner."""
        self.pending_approval = False

    def on_submit(self, form_data):
        """Clear the pending approval banner and handle login."""
        self.pending_approval = False
        return super().on_submit(form_data)

    def show_pending_approval(self):
        """Show the pending-approval banner on the login page."""
        self.pending_approval = True

class Register(reflex_local_auth.RegistrationState):
    """Extends registration to create a Galadriel user with a default role."""

    # This event handler must be named something besides `handle_registration`!!!
    def handle_registration_email(self, form_data):
        """Register a new user as a disabled viewer pending admin activation."""
        self.handle_registration(form_data)
        if self.new_user_id >= 0:
            with rx.session() as session:
                # Disable the account first — before any early returns
                local_user = session.exec(
                    reflex_local_auth.LocalUser.select().where(
                        reflex_local_auth.LocalUser.id == self.new_user_id
                    )
                ).one_or_none()
                if local_user:
                    local_user.enabled = False

                role = session.exec(GaladrielUserRole.select().where(GaladrielUserRole.name == "viewer")).one_or_none()
                if role is None:
                    session.commit()
                    return rx.toast.error("default role not found")
                session.add(GaladrielUser(email=form_data["email"], user_id=self.new_user_id, user_role=role.id))

                session.commit()

            # Redirect to login and show the pending-approval banner there
            self.error_message = ""
            self.new_user_id = -1
            return [rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE), Login.show_pending_approval]

        # Registration failed — return validation errors from parent
        return None
class Session(reflex_local_auth.LocalAuthState):
    """Manages the authenticated session, user info, and role checks."""

    @rx.var(cache=True)
    def user_id(self) -> Optional[int]:
        if self.authenticated_user.id < 0:
            return None
        return self.authenticated_user.id

    @rx.var(cache=True)
    def username(self) -> Optional[str]:
        if self.authenticated_user.id < 0:
            return None
        return self.authenticated_user.username

    @rx.var(cache=True)
    def user_info(self) -> Optional[GaladrielUser]:
        if self.authenticated_user.id < 0: return None
        with rx.session() as session:
            result = session.exec(sqlmodel.select(GaladrielUser).where(GaladrielUser.user_id == self.authenticated_user.id),).one_or_none()
        return result

    @rx.var(cache=True)
    def can_edit(self) -> bool:
        return self.role == UserRole.EDITOR

    @rx.var(cache=True)
    def is_admin(self) -> bool:
        """True for admin and user manager roles."""
        with rx.session() as session:
            if self.authenticated_user.id < 0:
                return False
            galadriel_user = session.exec(GaladrielUser.select().where(GaladrielUser.user_id == self.user_id)).one_or_none()
            if not galadriel_user:
                return False
            return galadriel_user.user_role in (UserRole.ADMIN.value, UserRole.USER_ADMIN.value)

    @rx.var(cache=True)
    def is_super_admin(self) -> bool:
        """True only for the admin role (excludes user_admin)."""
        with rx.session() as session:
            if self.authenticated_user.id < 0:
                return False
            galadriel_user = session.exec(GaladrielUser.select().where(GaladrielUser.user_id == self.user_id)).one_or_none()
            if not galadriel_user:
                return False
            return galadriel_user.user_role == UserRole.ADMIN.value

    @rx.var(cache=True)
    def role(self) -> UserRole:
        with rx.session() as session:
            if self.authenticated_user.id < 0:
                return UserRole.VIEWER
            galadriel_user = session.exec(GaladrielUser.select().where(GaladrielUser.user_id == self.user_id)).one_or_none()
            if not galadriel_user:
                return UserRole.VIEWER
            return UserRole(galadriel_user.user_role)

    def on_load(self):
        """Redirect unauthenticated users to the login page."""
        if not self.is_authenticated: return reflex_local_auth.LoginState.redir

    def require_admin(self):
        """Redirect non-admin/user_admin users to the dashboard."""
        if not self.is_admin:
            return rx.redirect("/dashboard")

    def require_super_admin(self):
        """Redirect non-admin users (including user_admin) to the dashboard."""
        if not self.is_super_admin:
            return rx.redirect("/dashboard")

    def require_non_admin(self):
        """Redirect admin/user_admin users to the users page."""
        if self.is_admin:
            return rx.redirect("/users")
        return None

    def require_editor(self):
        """Redirect unauthenticated users to login and viewers to the dashboard."""
        if not self.is_authenticated:
            return reflex_local_auth.LoginState.redir
        if self.role == UserRole.VIEWER:
            return rx.redirect("/dashboard")
        return None

    def perform_logout(self):
        """Log out the current user and redirect to the home page."""
        self.do_logout()
        return rx.redirect("/")
