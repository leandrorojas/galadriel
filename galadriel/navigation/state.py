import reflex as rx
import reflex_local_auth
from . import routes

class NavigationState(rx.State):

    def to_home(self):
        return rx.redirect(routes.HOME_ROUTE)
    
    def to_about(self):
        return rx.redirect(routes.ABOUT_ROUTE)
    
    def to_pricing(self):
        return rx.redirect(routes.PRICING_ROUTE)
    
    def to_contact(self):
        return rx.redirect(routes.CONTACT_ROUTE)
    
    def to_blog_posts(self):
        return rx.redirect(routes.BLOG_POSTS_ROUTE)
    
    def to_blog_post_add(self):
        return rx.redirect(routes.BLOG_POST_ADD_ROUTE)
    
    def to_suites(self):
        return rx.redirect(routes.SUITES_ROUTE)
    
    def to_suites_add(self):
        return rx.redirect(routes.SUITE_ADD_ROUTE)
    
    def to_login(self):
        return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
    
    def to_signup(self):
        return rx.redirect(reflex_local_auth.routes.REGISTER_ROUTE)
    
    def to_logout(self):
        return rx.redirect(routes.LOGOUT_ROUTE)