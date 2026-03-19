"""Public page components: base layout, about page, about content, and 404."""

from .base import base_page
from .about import about_page, about_content
from .not_found import not_found_page

__all__ = [
    'about_content',
    'about_page',
    'base_page',
    'not_found_page',
]