import reflex as rx
import reflex_local_auth
import sqlmodel

from typing import Optional

from ..user.model import GaladrielUser, GaladrielUserRole
from ..user.state import UserRole

class Register(reflex_local_auth.RegistrationState):
    # This event handler must be named something besides `handle_registration`!!!
    def handle_registration_email(self, form_data):
        registration_result = self.handle_registration(form_data)
        if self.new_user_id >= 0:
            with rx.session() as session:
                role = session.exec(GaladrielUserRole.select().where(GaladrielUserRole.name == "viewer")).one_or_none()
                session.add(GaladrielUser(email=form_data["email"], user_id=self.new_user_id, user_role=role.id))
                session.commit()

        return registration_result
class Session(reflex_local_auth.LocalAuthState):

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
            galadriel_user = session.exec(GaladrielUser.select().where(GaladrielUser.id == self.user_id)).one_or_none()
            if not galadriel_user:
                return UserRole.VIEWER
            return UserRole(galadriel_user.user_role)

    def on_load(self):
        if not self.is_authenticated: return reflex_local_auth.LoginState.redir

    def perform_logout(self):
        self.do_logout()
        return rx.redirect("/")