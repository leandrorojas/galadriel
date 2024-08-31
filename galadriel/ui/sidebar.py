import reflex as rx
from reflex.style import toggle_color_mode

from .. import navigation
from ..auth.state import SessionState

def sidebat_user_item() -> rx.Component:
    auth_user_info = SessionState.authenticated_user_info

    return rx.hstack(
        rx.icon_button(
            rx.icon("user"),
            size="3",
            radius="full",
        ),
        rx.vstack(
            rx.box(
                rx.text(
                    f"{SessionState.autheticated_username}",
                    #f"{auth_localuser_info.username}",
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

def sidebar_item(text: str, icon: str, href: str) -> rx.Component:
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

def sidebar_color_mode_toggle_item() -> rx.Component:
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

def sidebar_logout_item() -> rx.Component:
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
        on_click=navigation.RxTutorialNavigationState.rx_tutorial_to_logout,
        as_='button',
        underline="none",
        weight="medium",
        width="100%",
    )

def sidebar_items() -> rx.Component: 
    return rx.vstack(
        sidebar_item("Dashboard", "layout-dashboard", navigation.routes.RX_TUTORIAL_HOME_ROUTE),
        sidebar_item("Blog", "newspaper", navigation.routes.RX_TUTORIAL_BLOG_POSTS_ROUTE),
        sidebar_item("Create Post", "sticky-note", navigation.routes.RX_TUTORIAL_BLOG_POST_ADD_ROUTE),
        sidebar_item("Contact", "mail", navigation.routes.RX_TUTORIAL_CONTACT_ROUTE),
        sidebar_item("Contact History", "history", navigation.routes.RX_TUTORIAL_CONTACT_ENTRIES_ROUTE),
        # sidebar_item("Projects", "square-library", "/#"),
        # sidebar_item("Analytics", "bar-chart-4", "/#"),
        # sidebar_item("Messages", "mail", "/#"),
        spacing="1",
        width="100%",
    )

def sidebar() -> rx.Component:
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
                        href=navigation.routes.RX_TUTORIAL_HOME_ROUTE,
                    ),
                    align="center",
                    justify="start",
                    padding_x="0.5rem",
                    width="100%",
                ),
                sidebar_items(),
                rx.spacer(),
                rx.vstack(
                    rx.vstack(
                        #sidebar_item("Settings", "settings", "/#"),
                        sidebar_color_mode_toggle_item(),
                        sidebar_logout_item(),
                        spacing="1",
                        width="100%",
                    ),
                    rx.divider(),
                    sidebat_user_item(),
                    width="100%",
                    spacing="5",
                ),
                spacing="5",
                # position="fixed",
                # left="0px",
                # top="0px",
                # z_index="5",
                padding_x="1em",
                padding_y="1.5em",
                bg=rx.color("accent", 3),
                align="start",
                height="100vh",
                #height="650px",
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
                            sidebar_items(),
                            rx.spacer(),
                            rx.vstack(
                                rx.vstack(
                                    sidebar_color_mode_toggle_item(),
                                    sidebar_logout_item(),
                                    width="100%",
                                    spacing="1",
                                ),
                                rx.divider(margin="0"),
                                sidebat_user_item(),
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