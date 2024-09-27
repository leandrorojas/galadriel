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
            self.__sidebar_item("[to do] Dashboard", "layout-dashboard", navigation.routes.HOME),
            self.__sidebar_item("[to do] Cycles", "flask-round", navigation.routes.HOME),
            self.__sidebar_item("[wip]Cases", "test-tubes", navigation.routes.CASES),
            self.__sidebar_item("Scenarios", "route", navigation.routes.SCENARIOS),            
            self.__sidebar_item("Suites", "beaker", navigation.routes.SUITES),
            self.__sidebar_item("[to do] Steps", "test-tube", navigation.routes.HOME),
            self.__sidebar_item("[to do] Functions", "test-tube-diagonal", navigation.routes.HOME),
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
                            href=navigation.routes.HOME,
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
                            self.__sidebar_item("[to do] Settings", "settings", "/#"),
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

# class Table(): #this should be on each form with a "TODO: get tables to a component"
    # def __badge(self, icon: str, text: str, color_scheme: str):
    #     return rx.badge(rx.icon(icon, size=16), text, color_scheme=color_scheme, radius="full", variant="soft", size="3")

    # def __status_badge(self, status: str):
    #     badge_mapping = {
    #         "Delivered": ("check", "Delivered", "green"),
    #         "Pending": ("loader", "Pending", "yellow"),
    #         "Cancelled": ("ban", "Cancelled", "red")
    #     }
    #     return self.__badge(*badge_mapping.get(status, ("loader", "Pending", "yellow")))
    
    # def __show_customer(self, user: Customer):
    #     """Show a customer in a table row."""

    #     return rx.table.row(
    #         rx.table.cell(user.name),
    #         rx.table.cell(user.email),
    #         rx.table.cell(user.phone),
    #         rx.table.cell(user.address),
    #         rx.table.cell(f"${user.payments:,}"),
    #         rx.table.cell(user.date),
    #         rx.table.cell(rx.match(
    #             user.status,
    #             ("Delivered", self.__status_badge("Delivered")),
    #             ("Pending", self.__status_badge("Pending")),
    #             ("Cancelled", self.__status_badge("Cancelled")),
    #             self.__status_badge("Pending")
    #         )),
    #         rx.table.cell(
    #             rx.hstack(
    #                 update_customer_dialog(user),
    #                 rx.icon_button(
    #                     rx.icon("trash-2", size=22),
    #                     on_click=lambda: State.delete_customer(getattr(user, "id")),
    #                     size="2",
    #                     variant="solid",
    #                     color_scheme="red",
    #                 ),
    #             )
    #         ),
    #         style={"_hover": {"bg": rx.color("gray", 3)}},
    #         align="center",
    #     )
    
    # def __add_customer_button(self) -> rx.Component:
    #     return rx.dialog.root(
    #     rx.dialog.trigger(
    #         rx.button(
    #             rx.icon("plus", size=26),
    #             rx.text("Add Customer", size="4", display=[
    #                     "none", "none", "block"]),
    #             size="3",
    #         ),
    #     ),
    #     rx.dialog.content(
    #         rx.hstack(
    #             rx.badge(
    #                 rx.icon(tag="users", size=34),
    #                 color_scheme="grass",
    #                 radius="full",
    #                 padding="0.65rem",
    #             ),
    #             rx.vstack(
    #                 rx.dialog.title(
    #                     "Add New Customer",
    #                     weight="bold",
    #                     margin="0",
    #                 ),
    #                 rx.dialog.description(
    #                     "Fill the form with the customer's info",
    #                 ),
    #                 spacing="1",
    #                 height="100%",
    #                 align_items="start",
    #             ),
    #             height="100%",
    #             spacing="4",
    #             margin_bottom="1.5em",
    #             align_items="center",
    #             width="100%",
    #         ),
    #         rx.flex(
    #             rx.form.root(
    #                 rx.flex(
    #                     # Name
    #                     form_field(
    #                         "Name",
    #                         "Customer Name",
    #                         "text",
    #                         "name",
    #                         "user",
    #                     ),
    #                     # Email
    #                     form_field(
    #                         "Email", "user@reflex.dev", "email", "email", "mail"
    #                     ),
    #                     # Phone
    #                     form_field(
    #                         "Phone",
    #                         "Customer Phone",
    #                         "tel",
    #                         "phone",
    #                         "phone"
    #                     ),
    #                     # Address
    #                     form_field(
    #                         "Address",
    #                         "Customer Address",
    #                         "text",
    #                         "address",
    #                         "home"
    #                     ),
    #                     # Payments
    #                     form_field(
    #                         "Payment ($)",
    #                         "Customer Payment",
    #                         "number",
    #                         "payments",
    #                         "dollar-sign"
    #                     ),
    #                     # Status
    #                     rx.vstack(
    #                         rx.hstack(
    #                             rx.icon("truck", size=16, stroke_width=1.5),
    #                             rx.text("Status"),
    #                             align="center",
    #                             spacing="2",
    #                         ),
    #                         rx.radio(
    #                             ["Delivered", "Pending", "Cancelled"],
    #                             name="status",
    #                             direction="row",
    #                             as_child=True,
    #                             required=True,
    #                         ),
    #                     ),
    #                     direction="column",
    #                     spacing="3",
    #                 ),
    #                 rx.flex(
    #                     rx.dialog.close(
    #                         rx.button(
    #                             "Cancel",
    #                             variant="soft",
    #                             color_scheme="gray",
    #                         ),
    #                     ),
    #                     rx.form.submit(
    #                         rx.dialog.close(
    #                             rx.button("Submit Customer"),
    #                         ),
    #                         as_child=True,
    #                     ),
    #                     padding_top="2em",
    #                     spacing="3",
    #                     mt="4",
    #                     justify="end",
    #                 ),
    #                 on_submit=State.add_customer_to_db,
    #                 reset_on_submit=False,
    #             ),
    #             width="100%",
    #             direction="column",
    #             spacing="4",
    #         ),
    #         style={"max_width": 450},
    #         box_shadow="lg",
    #         padding="1.5em",
    #         border=f"2px solid {rx.color('accent', 7)}",
    #         border_radius="25px",
    #     ),
    # )

    # def __header_cell(self, text: str, icon: str):
    #     return rx.table.column_header_cell(
    #         rx.hstack(
    #             rx.icon(icon, size=18),
    #             rx.text(text),
    #             align="center",
    #             spacing="2",
    #         ),
    #     )    

    # def table(self) -> rx.Component:
    #     return rx.fragment(
    #         rx.flex(
    #             self.__add_customer_button(),
    #             rx.spacer(),
    #             rx.hstack(
    #                 rx.cond(
    #                     State.sort_reverse,
    #                     rx.icon("arrow-down-z-a", size=28, stroke_width=1.5, cursor="pointer", on_click=State.toggle_sort),
    #                     rx.icon("arrow-down-a-z", size=28, stroke_width=1.5, cursor="pointer", on_click=State.toggle_sort),
    #                 ),
    #                 rx.select(
    #                     ["name", "email", "phone", "address", "payments", "date", "status"],
    #                     placeholder="Sort By: Name",
    #                     size="3",
    #                     on_change=lambda sort_value: State.sort_values(sort_value),
    #                 ),
    #                 rx.input(
    #                     placeholder="Search here...",
    #                     size="3",
    #                     on_change=lambda value: State.filter_values(value),
    #                 ),
    #                 spacing="3",
    #                 align="center",
    #             ),
    #             spacing="3",
    #             wrap="wrap",
    #             width="100%",
    #             padding_bottom="1em",
    #         ),
    #         rx.table.root(
    #             rx.table.header(
    #                 rx.table.row(
    #                     self.__header_cell("Name", "user"),
    #                     self.__header_cell("Email", "mail"),
    #                     self.__header_cell("Phone", "phone"),
    #                     self.__header_cell("Address", "home"),
    #                     self.__header_cell("Payments", "dollar-sign"),
    #                     self.__header_cell("Date", "calendar"),
    #                     self.__header_cell("Status", "truck"),
    #                     self.__header_cell("Actions", "cog"),
    #                 ),
    #             ),
    #             rx.table.body(rx.foreach(State.users, self.__show_customer)),
    #             variant="surface",
    #             size="3",
    #             width="100%",
    #             on_mount=State.load_entries,
    #         ),
    #     )
