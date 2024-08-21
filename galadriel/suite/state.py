from typing import List, Optional
import reflex as rx
from .model import Suite

class SuiteState(rx.State):
    suites: List['Suite'] = []
    suite: Optional['Suite'] = None

    def load_suites(self):
        ...

    def get_suite(self):
        ...