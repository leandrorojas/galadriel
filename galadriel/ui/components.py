import reflex as rx

from .. import navigation

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
                            href=navigation.rx_routes.RX_TUTORIAL_HOME_ROUTE,
                        ),
                        rx.link(
                            rx.heading(
                                "galadriel", size="7", weight="bold"
                            ),
                            href=navigation.rx_routes.RX_TUTORIAL_HOME_ROUTE,
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
            # position="fixed",
            # top="0px",
            # z_index="5",
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