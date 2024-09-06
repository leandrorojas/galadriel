import reflex as rx
import reflex_local_auth

from .. import rx_navigation

def rx_navbar_link(text: str, url: str) -> rx.Component:
    return rx.link(
        rx.text(text, size="4", weight="medium"), href=url
    )

def rx_tutorial_navbar() -> rx.Component:
    return rx.box(
        rx.desktop_only(
            rx.hstack(
                rx.hstack(
                    rx.link(
                        rx.image(
                            src="/logo.jpg",
                            width="2.25em",
                            height="auto",
                            border_radius="25%",
                        ),
                        href=rx_navigation.routes.HOME_ROUTE,
                    ),
                    rx.link(
                        rx.heading(
                            "galadriel", size="7", weight="bold"
                        ),
                        href=rx_navigation.routes.HOME_ROUTE,
                    ),
                    align_items="center",
                ),
                rx.hstack(
                    rx_navbar_link("Home", rx_navigation.routes.HOME_ROUTE),
                    rx_navbar_link("About", rx_navigation.routes.ABOUT_ROUTE),
                    rx_navbar_link("Pricing", rx_navigation.routes.PRICING_ROUTE),
                    rx_navbar_link("Blog", rx_navigation.routes.BLOG_POSTS_ROUTE),
                    rx_navbar_link("Contact", rx_navigation.routes.CONTACT_ROUTE),
                    #rx_navbar_link("Suites", rx_navigation.routes.SUITES_ROUTE),
                    spacing="5",
                ),
                rx.hstack(
                    rx.link(
                        rx.button(
                            "Sign Up",
                            size="3",
                            variant="outline",
                        ),
                        href=reflex_local_auth.routes.REGISTER_ROUTE,
                    ),
                    rx.link(
                        rx.button("Log In", size="3"),
                        href=reflex_local_auth.routes.LOGIN_ROUTE,
                    ),
                    spacing="4",
                    justify="end",
                ),
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
                        rx.menu.item("Home", on_click=rx_navigation.RxTutorialNavigationState.to_home),
                        rx.menu.item("About", on_click=rx_navigation.RxTutorialNavigationState.to_about),
                        rx.menu.item("Pricing", on_click=rx_navigation.RxTutorialNavigationState.to_pricing),
                        rx.menu.item("Blog", on_click=rx_navigation.RxTutorialNavigationState.to_blog_posts),
                        rx.menu.item("Contact", on_click=rx_navigation.RxTutorialNavigationState.to_contact),
                        #rx.menu.item("Suites", on_click=rx_navigation.RxTutorialNavigationState.to_suites),
                        rx.menu.separator(),
                        rx.menu.item("Log in", on_click=rx_navigation.RxTutorialNavigationState.to_login),
                        rx.menu.item("Sign up", on_click=rx_navigation.RxTutorialNavigationState.to_signup),
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