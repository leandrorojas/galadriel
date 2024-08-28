import reflex as rx
import reflex_local_auth
import sqlmodel

from .model import UserInfo

class MyRegisterState(reflex_local_auth.RegistrationState):
    # This event handler must be named something besides `handle_registration`!!!
    def handle_registration_email(self, form_data):
        print(f"before super().handle_registration: {form_data}")
        registration_result = super().handle_registration(form_data)
        if self.new_user_id >= 0:
            print(f"after super().handle_registration: {self.new_user_id}")
            with rx.session() as session:
                session.add(
                    UserInfo(
                        email=form_data["email"],
                        user_id=self.new_user_id,
                    )
                )
                session.commit()
                print(f"after session.commit: {self.new_user_id}")
        return registration_result
    
class SessionState(reflex_local_auth.LocalAuthState):
    @rx.var(cache=True)
    def authenticated_user_info(self) -> UserInfo | None:
        print(f"auth_user_info: {self.authenticated_user.id}")
        if self.authenticated_user.id < 0:
            return
        with rx.session() as session:
            return session.exec(
                sqlmodel.select(UserInfo).where(
                    UserInfo.user_id == self.authenticated_user.id
                ),
            ).one_or_none()
        
    def on_load(self):
        if not self.is_authenticated:
            return reflex_local_auth.LoginState.redir
        print(f"onload {self.authenticated_user_info}")