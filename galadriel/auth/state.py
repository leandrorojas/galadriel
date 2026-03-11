"""Authentication state, session management, and role-based access control."""

import reflex as rx
import reflex_local_auth
from reflex_local_auth.login import LoginState
import sqlmodel

from typing import Optional

from ..user.model import GaladrielUser, GaladrielUserRole
from ..user.state import UserRole


def require_login(page: rx.app.ComponentCallable) -> rx.app.ComponentCallable:
    """Custom require_login that redirects unauthenticated users to login."""
    def protected_page():
        return rx.fragment(
            rx.cond(
                LoginState.is_hydrated & LoginState.is_authenticated,
                page(),
                rx.center(
                    rx.spinner(size="3"),
                    min_height="100vh",
                    on_mount=LoginState.redir,
                ),
            )
        )
    protected_page.__name__ = page.__name__
    return protected_page

class Login(LoginState):
    """Extends LoginState with additional event handlers."""

    def clear_error(self):
        """Clear the login error message."""
        self.error_message = ""

class Register(reflex_local_auth.RegistrationState):
    """Extends registration to create a Galadriel user with a default role."""

    # This event handler must be named something besides `handle_registration`!!!
    def handle_registration_email(self, form_data):
        """Register a new user and assign the default viewer role."""
        registration_result = self.handle_registration(form_data)
        if self.new_user_id >= 0:
            with rx.session() as session:
                role = session.exec(GaladrielUserRole.select().where(GaladrielUserRole.name == "viewer")).one_or_none()
                if role is None:
                    return rx.toast.error("default role not found")
                session.add(GaladrielUser(email=form_data["email"], user_id=self.new_user_id, user_role=role.id))
                session.commit()

        return registration_result
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
        return self.role == UserRole.ADMIN
    
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
        """Redirect non-admin users to the dashboard."""
        if not self.is_admin:
            return rx.redirect("/dashboard")

    def perform_logout(self):
        """Log out the current user and redirect to the home page."""
        self.do_logout()
        return rx.redirect("/")