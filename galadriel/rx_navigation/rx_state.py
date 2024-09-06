import reflex as rx
import reflex_local_auth
from . import routes

class RxTutorialNavigationState(rx.State):

    def rx_tutorial_to_home(self):
        return rx.redirect(routes.RX_TUTORIAL_HOME_ROUTE)
    
    def rx_tutorial_to_about(self):
        return rx.redirect(routes.RX_TUTORIAL_ABOUT_ROUTE)
    
    def rx_tutorial_to_pricing(self):
        return rx.redirect(routes.RX_TUTORIAL_PRICING_ROUTE)
    
    def rx_tutorial_to_contact(self):
        return rx.redirect(routes.RX_TUTORIAL_CONTACT_ROUTE)
    
    def rx_tutorial_to_blog_posts(self):
        return rx.redirect(routes.RX_TUTORIAL_BLOG_POSTS_ROUTE)
    
    def rx_tutorial_to_blog_post_add(self):
        return rx.redirect(routes.RX_TUTORIAL_BLOG_POST_ADD_ROUTE)
    
    def rx_tutorial_to_suites(self):
        return rx.redirect(routes.RX_TUTORIAL_SUITES_ROUTE)
    
    def rx_tutorial_to_suites_add(self):
        return rx.redirect(routes.RX_TUTORIAL_SUITE_ADD_ROUTE)
    
    def rx_tutorial_to_login(self):
        return rx.redirect(reflex_local_auth.routes.LOGIN_ROUTE)
    
    def rx_tutorial_to_signup(self):
        return rx.redirect(reflex_local_auth.routes.REGISTER_ROUTE)
    
    def rx_tutorial_to_logout(self):
        return rx.redirect(routes.RX_TUTORIAL_LOGOUT_ROUTE)