"""Reusable UI components for the Galadriel application."""

import reflex as rx
from reflex.style import toggle_color_mode
from rxconfig import config
from .. import navigation
from ..auth.state import Session
from ..utils import consts

from reflex.components.radix.themes.base import LiteralAccentColor

class TopNavBar():
    """Top navigation bar for public pages."""

    def navbar(self) -> rx.Component:
        """Render the top navigation bar."""
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
                            "galadriel", size="6", weight="bold"
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
                            rx.cond(
                                Session.is_authenticated,
                                rx.fragment(
                                    rx.menu.item("Dashboard", on_click=rx.redirect(navigation.routes.DASHBOARD)),
                                    rx.menu.item("Logout", on_click=navigation.NavigationState.to_logout),
                                ),
                                rx.fragment(
                                    rx.menu.item("Log in", on_click=navigation.NavigationState.to_login),
                                    rx.menu.item("Sign up", on_click=navigation.NavigationState.to_signup),
                                ),
                            ),
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
    """Common button components used across pages."""

    def signup_and_login(self):
        """Render the sign-up and login button pair."""
        return rx.hstack(
            rx.link(rx.button("Sign Up", size="3", variant="outline",), href=navigation.routes.SIGNUP,),
            rx.link(rx.button("Log In", size="3"), href=navigation.routes.LOGIN,),
            spacing="4",
            justify="end",
        ),

    def edit(self, link:str, disabled:bool = False) -> rx.Component:
        """Render an edit button linking to the given URL."""
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
        """Render a back-to-list navigation button."""
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
        """Render an add button linking to the given URL."""
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
    """Sidebar navigation for authenticated pages."""

    X_PADDING = "0.5rem"
    Y_PADDING = "0.75rem"
    BORDER_RADIUS = "0.5em"
    COLLAPSED_WIDTH = "3.5em"
    EXPANDED_WIDTH = "16em"
    TRANSITION = "width 0.2s ease-in-out"

    def __sidebar_user_item(self) -> rx.Component:
        return rx.hstack(
            rx.icon("user", flex_shrink="0"),
            rx.text(
                f"{Session.username}",
                size="4",
                weight="bold",
                white_space="nowrap",
            ),
            width="100%",
            padding_x=self.X_PADDING,
            padding_y=self.Y_PADDING,
            align="center",
            overflow="hidden",
            style={
                "color": rx.color("accent", 11),
                "border_radius": self.BORDER_RADIUS,
            },
        ),

    def __sidebar_item(self, text: str, icon: str, href: str) -> rx.Component:
        return rx.link(
            rx.hstack(
                rx.icon(icon, flex_shrink="0"),
                rx.text(text, size="4", white_space="nowrap"),
                width="100%",
                padding_x=self.X_PADDING,
                padding_y=self.Y_PADDING,
                align="center",
                overflow="hidden",
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
                    light=rx.icon("moon", flex_shrink="0"),
                    dark=rx.icon("sun", flex_shrink="0"),
                ),
                rx.text(
                    rx.color_mode_cond(
                        light="Dark Mode",
                        dark="Light Mode",
                    ),
                    size="4",
                    white_space="nowrap",
                ),
                width="100%",
                padding_x=self.X_PADDING,
                padding_y=self.Y_PADDING,
                align="center",
                overflow="hidden",
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
                rx.icon("log-out", flex_shrink="0"),
                rx.text("Logout", size="4", white_space="nowrap"),
                width="100%",
                padding_x=self.X_PADDING,
                padding_y=self.Y_PADDING,
                align="center",
                overflow="hidden",
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
            spacing="1",
            width="100%",
        )

    def __backoffice_sidebar_items(self) -> rx.Component:
        return rx.vstack(
            self.__sidebar_item("Users", "users", navigation.routes.USERS),
            self.__sidebar_item("[to do] Settings", "settings", "/#"),
            spacing="1",
            width="100%",
        )

    def __sidebar_toggle_button(self) -> rx.Component:
        collapsed = navigation.NavigationState.sidebar_collapsed

        return rx.box(
            rx.hstack(
                rx.cond(collapsed, rx.icon("panel-left-open", flex_shrink="0"), rx.icon("panel-left-close", flex_shrink="0")),
                padding_x=self.X_PADDING,
                padding_y=self.Y_PADDING,
                align="center",
                justify="center",
                overflow="hidden",
                style={
                    "_hover": {
                        "bg": rx.color("accent", 4),
                        "color": rx.color("accent", 11),
                    },
                    "color": rx.color("accent", 11),
                    "border_radius": self.BORDER_RADIUS,
                },
            ),
            on_click=navigation.NavigationState.toggle_sidebar,
            as_='button',
            cursor="pointer",
            position="absolute",
            right="0",
            top="50%",
            transform="translateY(-50%)",
        )

    def sidebar(self, show_backoffice:bool=True) -> rx.Component:
        """Render the sidebar with navigation items."""
        collapsed = navigation.NavigationState.sidebar_collapsed

        return rx.box(
            rx.desktop_only(
                rx.vstack(
                    rx.box(
                        rx.link(
                            rx.hstack(
                                rx.image(
                                    src=config.img_src,
                                    width="2.25em",
                                    height="auto",
                                    border_radius="25%",
                                    flex_shrink="0",
                                ),
                                rx.heading(
                                    "galadriel", size="7", weight="bold", white_space="nowrap",
                                ),
                                align="center",
                                gap="2",
                                flex_wrap="nowrap",
                            ),
                            href=navigation.routes.ABOUT,
                            underline="none",
                            pointer_events=rx.cond(collapsed, "none", "auto"),
                            white_space="nowrap",
                        ),
                        self.__sidebar_toggle_button(),
                        position="relative",
                        width="100%",
                        overflow="hidden",
                        white_space="nowrap",
                        display="flex",
                        align_items="center",
                        padding_left=self.X_PADDING,
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
                        spacing="2",
                    ),
                    spacing="5",
                    padding_x="0.5em",
                    padding_top="1.5em",
                    padding_bottom="0.5em",
                    bg=rx.color("accent", 3),
                    align="start",
                    height="100vh",
                    width=rx.cond(collapsed, self.COLLAPSED_WIDTH, self.EXPANDED_WIDTH),
                    overflow="hidden",
                    transition=self.TRANSITION,
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
                                rx.cond(show_backoffice,
                                    self.__backoffice_sidebar_items(),
                                    self.__galadriel_sidebar_items()
                                ),
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
    """Badge components for page titles and labels."""

    def title(self, icon:str, heading:str) -> rx.Component:
        """Render a title badge with an icon and heading."""
        return rx.badge(
            rx.icon(tag=icon, size=28),
            rx.heading(heading, size="6"),
            radius="large",
            align="center",
            variant="surface",
            padding="0.65rem",
        ),

class Tooltip():
    """Tooltip components for displaying contextual help."""

    def info(self, legend:str) -> rx.Component:
        """Render an info tooltip with the given legend text."""
        return rx.tooltip(rx.icon("info", size=18, color=rx.color("gray", 10)), content=legend, side="right")

class PageHeader():
    """Page header components with title and action buttons."""

    def list(self, title:str, icon:str, button:str, button_link:str, button_enabled:bool, tooltip:str="") -> rx.Component:
        """Render a list page header with title badge and add button."""
        title_badge = Badge()
        title_tooltip = Tooltip()
        button_component = Button()
        return rx.flex(
            title_badge.title(icon, title),
            rx.cond(tooltip, title_tooltip.info(tooltip), rx.fragment("")),
            rx.spacer(),
            rx.hstack(button_component.add(button, button_link, button_enabled),),
            spacing="2",
            flex_direction=["column", "column", "row"],
            align="center",
            width="100%",
            padding_top="2em",
            padding_bottom="0.5em",
            position="sticky",
            top="0",
            z_index="3",
            background_color="var(--color-background)",
        ),

class Table():
    """Table helper components for column headers."""

    def header(self, text: str, icon: str, hide_column:bool = False, info_tooltip:str = ""):
        """Render a table column header cell with icon and optional tooltip."""
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

    @staticmethod
    def sortable_header(text: str, icon: str, field: str, sort_by_var, sort_asc_var, on_click, info_tooltip: str = "") -> rx.Component:
        """Render a clickable table column header with sort direction indicator."""
        title_tooltip = Tooltip()
        return rx.table.column_header_cell(
            rx.hstack(
                rx.icon(icon, size=18),
                rx.text(text),
                rx.cond(
                    sort_by_var == field,
                    rx.cond(sort_asc_var, rx.icon("arrow-up", size=14), rx.icon("arrow-down", size=14)),
                    rx.icon("arrow-up-down", size=14, opacity=0.3),
                ),
                rx.cond(info_tooltip == "", rx.text(""), title_tooltip.info(info_tooltip)),
                align="center",
                spacing="2",
                cursor="pointer",
                on_click=on_click(field),
                _hover={"opacity": 0.7},
            ),
        )

class StatCard():
    """Statistic card with trend indicator."""

    def stat_card(self, stat_name: str, value: int, icon: str, icon_color: LiteralAccentColor, extra_char: str = "", prev_value: int = 0) -> rx.Component:
        """Render a stat card with value and percentage change."""
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
    """Simple display card with icon and value."""

    def card(self, card_name: str, value, icon: str, icon_color: LiteralAccentColor, header_size="6", subtext_size="4", icon_size:int = 34, prefix: str = "", suffix: str = "") -> rx.Component:
        """Render a card with an icon badge and a labeled value."""
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
    """Chart components wrapping Recharts."""

    def composed(self, data: list, name_key: str, area_key: str = "", bar_key: str = "", line_one_key: str = "", line_two_key: str = "", height:int=300) -> rx.Component:
        """Render a composed chart with optional area, bar, and line series."""
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
        """Render a line chart with two data series."""
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

class SearchTable():
    """Search table components with badge helpers."""

    def header(self):
        """Render the search table header row."""
        table_component = Table()
        return rx.table.header(
            rx.table.row(
                table_component.header("", "ellipsis"),
                table_component.header("name", "fingerprint"),
                table_component.header("created", "calendar-check-2"),
            ),
        ),

    @staticmethod
    def badge_with_icon(icon: str, text: str):
        """Render a badge with an icon and text."""
        return rx.badge(rx.icon(icon, size=16), text, radius="full", variant="soft", size="3")

    @staticmethod
    def badge_with_color(text: str, color=""):
        """Render a badge with optional color scheme."""
        if color:
            return rx.badge(text, radius="full", variant="soft", size="3", color_scheme=color)
        return rx.badge(text, radius="full", variant="soft", size="3")

    @staticmethod
    def badge_with_icon_and_color(icon: str, text: str, color=""):
        """Render a badge with an icon, text, and optional color scheme."""
        if color:
            return rx.badge(rx.icon(icon, size=16), text, radius="full", variant="soft", size="3", color_scheme=color)
        return rx.badge(rx.icon(icon, size=16), text, radius="full", variant="soft", size="3")

    @staticmethod
    def empty_case_row(test_case) -> rx.Component:
        """Render a greyed-out row for a case without steps."""
        moment_component = Moment()
        return rx.table.row(
            rx.table.cell(rx.icon("ban", size=16, color=consts.COLOR_MUTED)),
            rx.table.cell(rx.text(test_case.name, color=consts.COLOR_MUTED)),
            rx.table.cell(rx.text(moment_component.moment(test_case.created), color=consts.COLOR_MUTED)),
        )

    @staticmethod
    def empty_cases_section(empty_cases_var) -> rx.Component:
        """Render a conditional section for cases without steps."""
        table_component = Table()
        return rx.cond(
            empty_cases_var.length() > 0,
            rx.vstack(
                rx.text("Cases without steps (not available to add)", size="2", color=consts.COLOR_MUTED, padding_top="1em"),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            table_component.header("", "ellipsis"),
                            table_component.header("name", "fingerprint"),
                            table_component.header("created", "calendar-check-2"),
                        ),
                    ),
                    rx.table.body(rx.foreach(empty_cases_var, SearchTable.empty_case_row)),
                    variant="surface",
                    size="3",
                    width="100%",
                ),
                width="100%",
            ),
        )

class Moment():
    """Date display using relative time formatting."""

    def moment(self, date) -> rx.Component:
        """Render a date with relative time display."""
        return rx.moment(date.to(str), local=True, format="YYYY-MM-DD HH:mm", from_now=True, from_now_during=15552000000)
    
class MomentBadge():
    """Badge displaying a date with tooltip for full timestamp."""

    def moment_badge(self, date) -> rx.Component:
        """Render a date badge with a tooltip showing the full date."""
        moment_component = Moment()
        return rx.tooltip(rx.badge(moment_component.moment(date), variant="outline"), content=f"{date}")