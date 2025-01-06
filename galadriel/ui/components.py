import reflex as rx

from .. import navigation

from reflex.style import toggle_color_mode
from reflex.components.radix.themes.base import (LiteralAccentColor,)

from .. import navigation
from ..auth.state import Session

class TopNavBar():
    def navbar(self) -> rx.Component:
        buttons = Buttons()

        return rx.box(
            rx.desktop_only(
                rx.hstack(
                    rx.hstack(
                        rx.link(
                            rx.image(
                                src="/galadriel.320x320.jpg",
                                width="2.25em",
                                height="auto",
                                border_radius="25%",
                            ),
                            href=navigation.routes.HOME
                        ),
                        rx.link(
                            rx.heading(
                                "galadriel", size="7", weight="bold"
                            ),
                            href=navigation.routes.HOME,
                        ),
                        align_items="center",
                    ),
                    rx.hstack(
                        self.__navbar_link("Home", navigation.routes.HOME),
                        self.__navbar_link("About", navigation.routes.ABOUT),
                        justify="between",
                        align_items="center",                        
                        spacing="5",
                    ),
                    buttons.signup_and_login(),
                    justify="between",
                    align_items="center",
                ),
            ),
            rx.mobile_and_tablet(
                rx.hstack(
                    rx.hstack(
                        rx.image(
                            src="/galadriel.320x320.jpg",
                            width="2em",
                            height="auto",
                            border_radius="25%",
                        ),
                        rx.heading(
                            "Reflex", size="6", weight="bold"
                        ),
                        align_items="center",
                    ),
                    rx.menu.root(
                        rx.menu.trigger(
                            rx.icon("menu", size=30)
                        ),
                        rx.menu.content(
                            rx.menu.item("Home", on_click=navigation.NavigationState.to_home),
                            rx.menu.item("About", on_click=navigation.NavigationState.to_about),
                            rx.menu.separator(),
                            rx.menu.item("Log in", on_click=navigation.NavigationState.to_login),
                            rx.menu.item("Sign up", on_click=navigation.NavigationState.to_signup),
                        ),
                        justify="end",
                    ),
                    justify="between",
                    align_items="center",
                ),
            ),
            bg=rx.color("accent", 3),
            padding="1em",
            width="100%",
        )

    def __navbar_link(self, text: str, url: str) -> rx.Component:
        return rx.link(
            rx.text(text, size="4", weight="medium"), href=url
        )
    
class Buttons():
    def signup_and_login(self):
        return rx.hstack(
            rx.link(rx.button("Sign Up", size="3", variant="outline",), href=navigation.routes.SIGNUP,),
            rx.link(rx.button("Log In", size="3"), href=navigation.routes.LOGIN,),
            spacing="4",
            justify="end",
        ),

class SideBar():
    def __sidebar_user_item(self) -> rx.Component:
        auth_user_info = Session.authenticated_user_info

        return rx.hstack(
            rx.icon_button(
                rx.icon("user"),
                size="3",
                radius="full",
            ),
            rx.vstack(
                rx.box(
                    rx.text(
                        f"{Session.autheticated_username}",
                        size="3",
                        weight="bold",
                    ),
                    rx.text(
                        f"{auth_user_info.email}",
                        size="2",
                        weight="medium",
                    ),
                    width="100%",
                ),
                spacing="0",
                align="start",
                justify="start",
                width="100%",
            ),
            padding_x="0.5rem",
            align="center",
            justify="start",
            width="100%",
        ),    

    def __sidebar_item(self, text: str, icon: str, href: str) -> rx.Component:
        return rx.link(
            rx.hstack(
                rx.icon(icon),
                rx.text(text, size="4"),
                width="100%",
                padding_x="0.5rem",
                padding_y="0.75rem",
                align="center",
                style={
                    "_hover": {
                        "bg": rx.color("accent", 4),
                        "color": rx.color("accent", 11),
                    },
                    "border_radius": "0.5em",
                },
            ),
            href=href,
            underline="none",
            weight="medium",
            width="100%",
        )

    def __sidebar_color_mode_toggle_item(self) -> rx.Component:
        return rx.box(
            rx.hstack(
                rx.color_mode_cond(
                    light=rx.icon("moon"),
                    dark=rx.icon("sun"),
                ),
                rx.text(
                    rx.color_mode_cond(
                        light="Dark Mode",
                        dark="Light Mode",
                    ),
                    size="4"),
                width="100%",
                padding_x="0.5rem",
                padding_y="0.75rem",
                align="center",
                style={
                    "_hover": {
                        "cursor": "pointer",
                        "bg": rx.color("accent", 4),
                        "color": rx.color("accent", 11),
                    },
                    "color": rx.color("accent", 11),
                    "border_radius": "0.5em",
                },
            ),
            on_click=toggle_color_mode,
            as_='button',
            underline="none",
            weight="medium",
            width="100%",
        )

    def __sidebar_logout_item(self) -> rx.Component:
        return rx.box(
            rx.hstack(
                rx.icon("log-out"),
                rx.text("Logout", size="4"),
                width="100%",
                padding_x="0.5rem",
                padding_y="0.75rem",
                align="center",
                style={
                    "_hover": {
                        "cursor": "pointer",
                        "bg": rx.color("accent", 4),
                        "color": rx.color("accent", 11),
                    },
                    "color": rx.color("accent", 11),
                    "border_radius": "0.5em",
                },
            ),
            on_click=navigation.NavigationState.to_logout,
            as_='button',
            underline="none",
            weight="medium",
            width="100%",
        )

    def __sidebar_items(self) -> rx.Component: 
        return rx.vstack(
            self.__sidebar_item("[to do] Dashboard", "layout-dashboard", navigation.routes.ABOUT),
            self.__sidebar_item("Cycles", "flask-round", navigation.routes.CYCLES),
            rx.divider(),
            self.__sidebar_item("Suites", "beaker", navigation.routes.SUITES),
            self.__sidebar_item("Scenarios", "route", navigation.routes.SCENARIOS),
            self.__sidebar_item("Cases", "test-tubes", navigation.routes.CASES),
            self.__sidebar_item("[to do] Steps", "test-tube", navigation.routes.ABOUT),
            self.__sidebar_item("[to do] Functions", "test-tube-diagonal", navigation.routes.ABOUT),
            spacing="1",
            width="100%",
        )

    def sidebar(self) -> rx.Component:
        return rx.box(
            rx.desktop_only(
                rx.vstack(
                    rx.hstack(
                        rx.image(
                            src="/galadriel.320x320.jpg",
                            width="2.25em",
                            height="auto",
                            border_radius="25%",
                        ),
                        rx.link(
                            rx.heading(
                                "galadriel", size="7", weight="bold"
                            ),
                            href=navigation.routes.ABOUT,
                        ),
                        align="center",
                        justify="start",
                        padding_x="0.5rem",
                        width="100%",
                    ),
                    self.__sidebar_items(),
                    rx.spacer(),
                    rx.vstack(
                        rx.vstack(
                            self.__sidebar_item("[to do] Settings", "settings", navigation.routes.ABOUT),
                            self.__sidebar_color_mode_toggle_item(),
                            self.__sidebar_logout_item(),
                            spacing="1",
                            width="100%",
                        ),
                        rx.divider(),
                        self.__sidebar_user_item(),
                        width="100%",
                        spacing="5",
                    ),
                    spacing="5",
                    padding_x="1em",
                    padding_y="1.5em",
                    bg=rx.color("accent", 3),
                    align="start",
                    height="100vh",
                    width="16em",
                ),
            ),
            rx.mobile_and_tablet(
                rx.drawer.root(
                    rx.drawer.trigger(
                        rx.icon("align-justify", size=30)
                    ),
                    rx.drawer.overlay(z_index="5"),
                    rx.drawer.portal(
                        rx.drawer.content(
                            rx.vstack(
                                rx.box(
                                    rx.drawer.close(
                                        rx.icon("x", size=30)
                                    ),
                                    width="100%",
                                ),
                                self.__sidebar_items(),
                                rx.spacer(),
                                rx.vstack(
                                    rx.vstack(
                                        self.__sidebar_item("[to do] Settings", "settings", "/#"),
                                        self.__sidebar_color_mode_toggle_item(),
                                        self.__sidebar_logout_item(),
                                        width="100%",
                                        spacing="1",
                                    ),
                                    rx.divider(margin="0"),
                                    self.__sidebar_user_item(),
                                    width="100%",
                                    spacing="5",
                                ),
                                spacing="5",
                                width="100%",
                            ),
                            top="auto",
                            right="auto",
                            height="100%",
                            width="20em",
                            padding="1.5em",
                            bg=rx.color("accent", 2),
                        ),
                        width="100%",
                    ),
                    direction="left",
                ),
                padding="1em",
            ),
        )

class Badge():
    def title(self, icon:str, heading:str) -> rx.Component:
        return rx.badge(
            rx.icon(tag=icon, size=28),
            rx.heading(heading, size="6"),
            radius="large",
            align="center",
            variant="surface",
            padding="0.65rem",
        ),
    
class Tooltip():
    def info(self, legend:str) -> rx.Component:
        return rx.tooltip(rx.icon("info", size=18, color=rx.color("gray", 10)), content=legend, side="right")