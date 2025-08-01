import reflex as rx
from reflex.style import toggle_color_mode
from rxconfig import config
from .. import navigation
from ..auth.state import Session
from ..utils import consts

from reflex.components.radix.themes.base import LiteralAccentColor

class TopNavBar():
    def navbar(self) -> rx.Component:
        buttons = Button()

        return rx.box(
            rx.desktop_only(
                rx.hstack(
                    rx.hstack(
                        rx.link(
                            rx.image(
                                src=config.img_src,
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
                            src=config.img_src,
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

class Button():
    def signup_and_login(self):
        return rx.hstack(
            rx.link(rx.button("Sign Up", size="3", variant="outline",), href=navigation.routes.SIGNUP,),
            rx.link(rx.button("Log In", size="3"), href=navigation.routes.LOGIN,),
            spacing="4",
            justify="end",
        ),

    def edit(self, link:str, disabled:bool = False) -> rx.Component:
        return rx.fragment(
            rx.link(
                rx.button(
                    rx.icon("pencil", size=26), 
                    rx.text("Edit", size="4", display=["none", "none", "block"]), 
                    size="3", 
                    disabled=disabled,
                ),
                href=link
            ), 
        )
    
    def to_list(self, list_name:str, link:str) -> rx.Component:
        return rx.fragment(
            rx.link(
                rx.button(
                    rx.icon("chevron-left", size=26), 
                    rx.text(f"{list_name}", size="4", display=["none", "none", "block"]), 
                    size="3", 
                ),
                href=link
            ),
        )
    
    def add(self, name:str, link:str, enabled:bool) -> rx.Component:
        return rx.fragment(
            rx.link(
                rx.button(
                    rx.icon("plus", size=26), 
                    rx.text(f"{name}", size="4", display=["none", "none", "block"]), 
                    disabled=~enabled,
                    size="3",
                ),
                href=link
            ), 
        )

class SideBar():

    X_PADDING = "0.5rem"
    Y_PADDING = "0.75rem"
    BORDER_RADIUS = "0.5em"

    def __sidebar_user_item(self) -> rx.Component:
        auth_user_info = Session.user_info

        return rx.hstack(
            rx.icon_button(
                rx.icon("user"),
                size="3",
                radius="full",
            ),
            rx.vstack(
                rx.box(
                    rx.text(
                        f"{Session.username}",
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
            padding_x= self.X_PADDING,
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
                padding_x= self.X_PADDING,
                padding_y=self.Y_PADDING,
                align="center",
                style={
                    "_hover": {
                        "bg": rx.color("accent", 4),
                        "color": rx.color("accent", 11),
                    },
                    "border_radius": self.BORDER_RADIUS,
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
                padding_x= self.X_PADDING,
                padding_y= self.Y_PADDING,
                align="center",
                style={
                    "_hover": {
                        "cursor": "pointer",
                        "bg": rx.color("accent", 4),
                        "color": rx.color("accent", 11),
                    },
                    "color": rx.color("accent", 11),
                    "border_radius": self.BORDER_RADIUS,
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
                padding_x=self.X_PADDING,
                padding_y=self.Y_PADDING,
                align="center",
                style={
                    "_hover": {
                        "cursor": "pointer",
                        "bg": rx.color("accent", 4),
                        "color": rx.color("accent", 11),
                    },
                    "color": rx.color("accent", 11),
                    "border_radius": self.BORDER_RADIUS,
                },
            ),
            on_click=navigation.NavigationState.to_logout,
            as_='button',
            underline="none",
            weight="medium",
            width="100%",
        )

    def __galadriel_sidebar_items(self) -> rx.Component: 
        return rx.vstack(
            self.__sidebar_item("Dashboard", "layout-dashboard", navigation.routes.DASHBOARD),
            self.__sidebar_item("Cycles", "flask-round", navigation.routes.CYCLES),
            rx.divider(),
            self.__sidebar_item("Suites", "beaker", navigation.routes.SUITES),
            self.__sidebar_item("Scenarios", "route", navigation.routes.SCENARIOS),
            self.__sidebar_item("Cases", consts.ICON_TEST_TUBES, navigation.routes.CASES),
            #self.__sidebar_item("[to do] Steps", "test-tube", navigation.routes.ABOUT),
            #self.__sidebar_item("[to do] Functions", "test-tube-diagonal", navigation.routes.ABOUT),
            spacing="1",
            width=
            "100%",
        )
    
    def __backoffice_sidebar_items(self) -> rx.Component: 
        return rx.vstack(
            self.__sidebar_item("Users", "users", navigation.routes.USERS),
            self.__sidebar_item("[to do] Settings", "settings", "/#"),            
            spacing="1",
            width="100%",
        )

    def sidebar(self, show_backoffice:bool=True) -> rx.Component:
        return rx.box(
            rx.desktop_only(
                rx.vstack(
                    rx.hstack(
                        rx.image(
                            src=config.img_src,
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
                        padding_x=self.X_PADDING,
                        width="100%",
                    ),
                    rx.cond(show_backoffice,
                        self.__backoffice_sidebar_items(),
                        self.__galadriel_sidebar_items()
                    ),
                    rx.spacer(),
                    rx.vstack(
                        rx.vstack(
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
                                self.__backoffice_sidebar_items(),
                                rx.spacer(),
                                rx.vstack(
                                    rx.vstack(
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

class PageHeader():
    def list(self, title:str, icon:str, button:str, button_link:str, button_enabled:bool, tootip:str="") -> rx.Component:
        title_badge = Badge()
        title_tooltip = Tooltip()
        button_component = Button()
        return rx.flex(
            title_badge.title(icon, title),
            rx.cond(tootip, title_tooltip.info(tootip), rx.fragment("")),
            rx.spacer(),
            rx.hstack(button_component.add(button, button_link, button_enabled),),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            top="0px",
            padding_top="2em",
        ),

class Table():
    def header(self, text: str, icon: str, hide_column:bool = False, info_tooltip:str = ""):
        title_tooltip = Tooltip()
        return rx.table.column_header_cell(
            rx.hstack(
                rx.icon(icon, size=18),
                rx.text(text),
                rx.cond(info_tooltip == "", rx.text(""), title_tooltip.info(info_tooltip)),
                align="center",
                spacing="2",
            ),
            hidden=hide_column,
        )

class StatCard():
    def stat_card(self, stat_name: str, value: int, icon: str, icon_color: LiteralAccentColor, extra_char: str = "", prev_value: int = 0) -> rx.Component:
        if prev_value == 0:
            percentage_change = 0 if value == 0 else float("inf")
        else:
            percentage_change = round(((value - prev_value) / prev_value) * 100, 2)
            
        change = "increase" if value > prev_value else "decrease"
        arrow_icon = "trending-up" if value > prev_value else "trending-down"
        arrow_color = "grass" if value > prev_value else "tomato"
        return rx.card(
            rx.vstack(
                rx.hstack(
                    rx.badge(rx.icon(tag=icon, size=34), color_scheme=str(icon_color), radius="full", padding="0.7rem",),
                    rx.vstack(
                        rx.heading(f"{extra_char}{value:,}", size="6", weight="bold",),
                        rx.text(stat_name, size="4", weight="medium"),
                        spacing="1", height="100%", align_items="start", width="100%",
                    ),
                    height="100%", spacing="4", align="center", width="100%",
                ),
                rx.hstack( 
                    rx.hstack(
                        rx.icon(tag=arrow_icon, size=24, color=rx.color(arrow_color, 9),),
                        rx.text(f"{percentage_change}%", size="3", color=rx.color(arrow_color, 9), weight="medium",),
                        spacing="2", align="center",
                    ),
                    rx.text(f"{change} from last month", size="2", color=rx.color("gray", 10),),
                    align="center", width="100%",
                ),
                spacing="3",
            ),
            size="1", width="100%", box_shadow="0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
        )

class Card():
    def card(self, card_name: str, value, icon: str, icon_color: LiteralAccentColor, header_size="6", subtext_size="4", icon_size:int = 34, prefix: str = "", suffix: str = "") -> rx.Component:
        return rx.card(
            rx.vstack(
                rx.hstack(
                    rx.badge(rx.icon(tag=icon, size=icon_size), color_scheme=str(icon_color), radius="full", padding="0.7rem",),
                    rx.vstack(
                        rx.heading(f"{prefix}{value}{suffix}", size=header_size, weight="bold",),
                        rx.text(card_name, size=subtext_size, weight="medium"),
                        spacing="1", height="100%", align_items="start", width="100%",
                    ),
                    height="100%", spacing="4", align="center", width="100%",
                ),
                spacing="3",
            ),
            size="1", width="100%", box_shadow="0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)",
        )
    
class Chart():
    def composed(self, data: list, name_key: str, area_key: str = "", bar_key: str = "", line_one_key: str = "", line_two_key: str = "", height:int=300) -> rx.Component:
        return rx.recharts.composed_chart(
            rx.cond(
                area_key!="", 
                rx.recharts.area(data_key=area_key, stroke="#8884d8", fill="#8884d8"),
                rx.fragment(),
            ),
            rx.cond(
                bar_key!="",
                rx.recharts.bar(data_key=bar_key, bar_size=20, fill="#413ea0"),
                rx.fragment(),
            ),
            rx.cond(
                line_one_key!="",
                rx.recharts.line(data_key=line_one_key, type_="monotone", stroke="#ff7300",),
                rx.fragment(),
            ),
            rx.cond(
                line_two_key!="",
                rx.recharts.line(data_key=line_two_key, type_="monotone", stroke="#82ca9d",),
                rx.fragment(),
            ),
            rx.recharts.x_axis(data_key=name_key),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            rx.recharts.legend(),
            data=data,
            height=height, 
        )
    
    def line(self, data: list, name_key: str, line_one_key: str, line_two_key: str, height:int=300) -> rx.Component:
        return rx.recharts.line_chart(
            rx.recharts.line(
                data_key=line_one_key,
                type_="monotone",
                stroke="#8884d8",
            ),
            rx.recharts.line(
                data_key=line_two_key,
                type_="monotone",
                stroke="#82ca9d",
            ),
            rx.recharts.x_axis(data_key=name_key),
            rx.recharts.y_axis(),
            rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
            rx.recharts.graphing_tooltip(),
            rx.recharts.legend(),
            data=data,
            height=height,
        ),

class Moment():
    def moment(self, date) -> rx.Component:
        return rx.moment(date, local=True, format="YYYY-MM-DD HH:mm", from_now=True, from_now_during=15552000000)
    
class MomentBadge():
    def moment_badge(self, date) -> rx.Component:
        moment_component = Moment()
        return rx.tooltip(rx.badge(moment_component.moment(date), variant="outline"), content=f"{date}")