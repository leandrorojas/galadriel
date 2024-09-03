import reflex as rx
from . import routes
    
class NavigationState(rx.State):
    def to_home(self):
        return rx.redirect(routes.HOME)
    
    def to_about(self):
        return rx.redirect(routes.ABOUT)
    
    def to_login(self):
        return rx.redirect(routes.LOGIN)
    
    def to_signup(self):
        return rx.redirect(routes.SIGNUP)
    
    def to_logout(self):
        return rx.redirect(routes.LOGOUT)
    
    def to_suites(self):
        return rx.redirect(routes.SUITES)
    
    def to_suites_add(self):
        return rx.redirect(routes.SUITE_ADD)