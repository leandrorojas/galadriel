import reflex as rx
import reflex_local_auth
import sqlmodel

from typing import Optional

from .model import RxTutorialUserInfo

class RxTutorialMyRegisterState(reflex_local_auth.RegistrationState):
    # This event handler must be named something besides `handle_registration`!!!
    def rx_tutorial_handle_registration_email(self, form_data):
        registration_result = self.handle_registration(form_data)
        if self.new_user_id >= 0:
            with rx.session() as session:
                session.add(
                    RxTutorialUserInfo(
                        email=form_data["email"],
                        user_id=self.new_user_id,
                    )
                )
                session.commit()
        return registration_result

class RxTutorialSessionState(reflex_local_auth.LocalAuthState):

    @rx.var(cache=True)
    def my_user_id(self) -> Optional[str]:
        if self.authenticated_user.id < 0:
            return
        return self.authenticated_user.id
        
    @rx.var(cache=True)
    def autheticated_username(self) -> Optional[str]:
        if self.authenticated_user.id < 0:
            return
        return self.authenticated_user.username

    @rx.var(cache=True)
    def authenticated_user_info(self) -> Optional[RxTutorialUserInfo]:        
        if self.authenticated_user.id < 0:
            return None

        with rx.session() as session:
            result = session.exec(
                sqlmodel.select(RxTutorialUserInfo).where(
                    RxTutorialUserInfo.user_id == self.authenticated_user.id
                ),
            ).one_or_none()

        if result is None:
            return None
        
        result.auth_user
        return result
        
    def on_load(self):
        if not self.is_authenticated:
            return reflex_local_auth.LoginState.redir
        
    def perform_logout(self):
        self.do_logout()
        return rx.redirect("/")