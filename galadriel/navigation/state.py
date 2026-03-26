"""Navigation state and redirect event handlers."""

import reflex as rx
from . import routes
    
class NavigationState(rx.State):
    """Provides redirect event handlers for all application routes."""

    sidebar_collapsed: bool = False

    def toggle_sidebar(self):
        """Toggle the sidebar between expanded and collapsed states."""
        self.sidebar_collapsed = not self.sidebar_collapsed

    def to_home(self):
        """Redirect to the home page."""
        return rx.redirect(routes.HOME)

    def to_about(self):
        """Redirect to the about page."""
        return rx.redirect(routes.ABOUT)

    def to_login(self):
        """Redirect to the login page."""
        return rx.redirect(routes.LOGIN)

    def to_signup(self):
        """Redirect to the signup page."""
        return rx.redirect(routes.SIGNUP)

    def to_logout(self):
        """Redirect to the logout page."""
        return rx.redirect(routes.LOGOUT)

    def to_suites(self):
        """Redirect to the suites list page."""
        return rx.redirect(routes.SUITES)

    def to_suites_add(self):
        """Redirect to the add-suite page."""
        return rx.redirect(routes.SUITE_ADD)

    def to_scenarios(self):
        """Redirect to the scenarios list page."""
        return rx.redirect(routes.SCENARIOS)

    def to_scenarios_add(self):
        """Redirect to the add-scenario page."""
        return rx.redirect(routes.SCENARIO_ADD)

    def to_cases(self):
        """Redirect to the cases list page."""
        return rx.redirect(routes.CASES)

    def to_cases_add(self):
        """Redirect to the add-case page."""
        return rx.redirect(routes.CASE_ADD)