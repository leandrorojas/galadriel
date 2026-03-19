"""Custom 404 page for unmatched routes."""

import reflex as rx
from .base import base_page
from ..utils import consts


def not_found_page() -> rx.Component:
    """Render a custom 404 Not Found page."""
    return base_page(
        rx.vstack(
            rx.icon("circle-x", size=64, color=rx.color("gray", 9)),
            rx.heading("404 - Page Not Found", size="7"),
            rx.text("The page you are looking for does not exist.", size="4", color=rx.color("gray", 10)),
            rx.link(
                rx.button(
                    rx.icon("house", size=20),
                    "Go Home",
                    size="3",
                ),
                href="/",
            ),
            spacing="5",
            justify="center",
            align="center",
            min_height=consts.RELATIVE_VIEWPORT_85,
        ),
    )
