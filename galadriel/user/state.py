"""User state management and event handlers."""

import reflex as rx
import reflex_local_auth

import re
import secrets
import string
from typing import List, Optional
from sqlmodel import select

from .model import GaladrielUser, GaladrielUserRole, GaladrielUserDisplay
from ..navigation import routes
from ..utils import consts
from ..utils.mixins import toggle_sort_field, sort_items

from enum import Enum

USERS_ROUTE = consts.normalize_route(routes.USERS)

PASSWORD_LENGTH = 16
PASSWORD_ALPHABET = string.ascii_letters + string.digits + string.punctuation
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s.]+\.[^@\s.]+$")
USERNAME_RE = re.compile(r"^[a-zA-Z0-9._-]+$")

ERR_USERNAME_EMPTY = "Username cannot be empty"
ERR_USERNAME_INVALID = "Username can only contain letters, numbers, dots, hyphens, and underscores"
ERR_EMAIL_EMPTY = "Email cannot be empty"
ERR_EMAIL_INVALID = "Please enter a valid email address"
ERR_EMAIL_IN_USE = "Email address already in use"
ERR_ROLE_EMPTY = "Please select a role"
ERR_ROLE_INVALID = "Invalid role"


def generate_password() -> str:
    """Generate a strong random password."""
    while True:
        password = "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(PASSWORD_LENGTH))
        has_upper = any(c in string.ascii_uppercase for c in password)
        has_lower = any(c in string.ascii_lowercase for c in password)
        has_digit = any(c in string.digits for c in password)
        has_symbol = any(c in string.punctuation for c in password)
        if has_upper and has_lower and has_digit and has_symbol:
            return password


class UserRole(Enum):
    """Enumerates application-level user roles."""

    ADMIN = 0
    EDITOR = 2
    VIEWER = 1
    USER_ADMIN = 3

class UserState(rx.State):
    """Manages user listing and detail retrieval."""

    users: List['GaladrielUserDisplay'] = []
    user: Optional['GaladrielUserDisplay'] = None

    sort_by: str = ""
    sort_asc: bool = True

    @rx.var(cache=True)
    def user_id(self) -> Optional[int]:
        try:
            return int(self.router._page.params.get(consts.FIELD_ID, "0"))
        except ValueError:
            return None

    @rx.var(cache=True)
    def user_edit_url(self) -> str:
        if not self.user:
            return f"{USERS_ROUTE}"
        return f"{USERS_ROUTE}/{self.user.galadriel_user_id}/edit"

    def load_users(self):
        """Load all users with their roles and display info."""
        self.users.clear()
        with rx.session() as session:
            all_users = session.exec(GaladrielUser.select()).all()

            for single_user in all_users:
                local_user = session.exec(reflex_local_auth.LocalUser.select().where(reflex_local_auth.LocalUser.id == single_user.user_id)).one_or_none()

                if local_user:
                    role = session.exec(select(GaladrielUserRole).where(GaladrielUserRole.id == single_user.user_role)).one_or_none()
                    self.users.append(
                        GaladrielUserDisplay(
                            local_user_id=local_user.id,
                            galadriel_user_id=single_user.id,
                            username=local_user.username,
                            email=single_user.email,
                            role=role.name if role else "unknown",
                            enabled=local_user.enabled,
                            created=single_user.created,
                            updated=single_user.updated
                        )
                    )

    def toggle_sort(self, field: str):
        """Cycle sort: default → asc → desc → default."""
        self.sort_by, self.sort_asc = toggle_sort_field(self.sort_by, self.sort_asc, field)

    @rx.var(cache=True)
    def sorted_users(self) -> List['GaladrielUserDisplay']:
        """Return users sorted by the current sort field and direction."""
        return sort_items(self.users, self.sort_by, self.sort_asc)

    def get_user_detail(self):
        """Load a single user by their route ID."""
        with rx.session() as session:
            if self.user_id is None:
                self.user = None
                return
            galadriel_user = session.exec(GaladrielUser.select().where(GaladrielUser.id == self.user_id)).one_or_none()
            if galadriel_user is None:
                self.user = None
                return
            local_user = session.exec(reflex_local_auth.LocalUser.select().where(reflex_local_auth.LocalUser.id == galadriel_user.user_id)).one_or_none()
            if local_user is None:
                self.user = None
                return
            role = session.exec(select(GaladrielUserRole).where(GaladrielUserRole.id == galadriel_user.user_role)).one_or_none()
            self.user = GaladrielUserDisplay(
                local_user_id=local_user.id,
                galadriel_user_id=galadriel_user.id,
                username=local_user.username,
                email=galadriel_user.email,
                role=role.name if role else "unknown",
                enabled=local_user.enabled,
                created=galadriel_user.created,
                updated=galadriel_user.updated
            )

    def add_user(self, form_data: dict) -> tuple[Optional[str], str]:
        """Create a LocalUser and GaladrielUser, return (password, '') or (None, error)."""
        username = form_data.get("username", "").strip()
        email = form_data.get("email", "").strip()
        role_name = form_data.get("role", "").strip()

        if not username:
            return None, ERR_USERNAME_EMPTY
        if not email:
            return None, ERR_EMAIL_EMPTY

        with rx.session() as session:
            existing = session.exec(
                reflex_local_auth.LocalUser.select().where(
                    reflex_local_auth.LocalUser.username == username
                )
            ).one_or_none()
            if existing:
                return None, "Username already exists"

            existing_email = session.exec(
                GaladrielUser.select().where(GaladrielUser.email == email)
            ).one_or_none()
            if existing_email:
                return None, ERR_EMAIL_IN_USE

            role = session.exec(
                select(GaladrielUserRole).where(GaladrielUserRole.name == role_name)
            ).one_or_none()
            if role is None or role_name == "admin":
                return None, ERR_ROLE_INVALID

            password = generate_password()
            password_hash = reflex_local_auth.LocalUser.hash_password(password)
            local_user = reflex_local_auth.LocalUser(
                username=username,
                password_hash=password_hash,
                enabled=True,
            )
            session.add(local_user)
            session.flush()

            galadriel_user = GaladrielUser(
                email=email,
                user_id=local_user.id,
                user_role=role.id,
            )
            session.add(galadriel_user)
            session.commit()

        return password, ""

    assignable_roles: list[str] = []

    def load_assignable_roles(self):
        """Load role names that can be assigned (excludes admin)."""
        with rx.session() as session:
            roles = session.exec(select(GaladrielUserRole)).all()
            self.assignable_roles = [r.name for r in roles if r.name != "admin"]


class AddUserState(UserState):
    """Handles the add-user form submission."""

    form_data: dict = rx.Field(default_factory=dict)
    generated_password: str = ""
    show_password_dialog: bool = False

    def handle_submit(self, form_data: dict):
        """Validate and create a new user from the form."""
        self.form_data = form_data

        username = form_data.get("username", "").strip()
        email = form_data.get("email", "").strip()
        role_name = form_data.get("role", "").strip()

        if not username:
            return rx.toast.error(ERR_USERNAME_EMPTY)
        if not USERNAME_RE.match(username):
            return rx.toast.error(ERR_USERNAME_INVALID)
        if not email:
            return rx.toast.error(ERR_EMAIL_EMPTY)
        if not EMAIL_RE.match(email):
            return rx.toast.error(ERR_EMAIL_INVALID)
        if not role_name:
            return rx.toast.error(ERR_ROLE_EMPTY)

        password, error = self.add_user(form_data)
        if password is None:
            return rx.toast.error(error)

        self.generated_password = password
        self.show_password_dialog = True
        return None

    def close_password_dialog(self):
        """Close the password dialog and redirect to users list."""
        self.show_password_dialog = False
        self.generated_password = ""
        return rx.redirect(routes.USERS)


class EditUserState(UserState):
    """Handles the edit-user form submission."""

    edit_email: str = ""
    edit_role: str = ""
    edit_enabled: bool = True

    def load_edit_user(self):
        """Load the current user data into form fields."""
        self.get_user_detail()
        if self.user is None:
            return rx.redirect(routes.USERS)
        self.edit_email = self.user.email
        self.edit_role = self.user.role
        self.edit_enabled = self.user.enabled
        self.load_assignable_roles()
        return None

    def handle_submit(self, form_data: dict):
        """Validate and save user edits."""
        email = form_data.get("email", "").strip()
        role_name = form_data.get("role", "").strip()
        enabled = form_data.get("enabled") == "on"

        if not email:
            return rx.toast.error(ERR_EMAIL_EMPTY)
        if not EMAIL_RE.match(email):
            return rx.toast.error(ERR_EMAIL_INVALID)
        if not role_name:
            return rx.toast.error(ERR_ROLE_EMPTY)

        with rx.session() as session:
            galadriel_user = session.exec(
                GaladrielUser.select().where(GaladrielUser.id == self.user_id)
            ).one_or_none()
            if galadriel_user is None:
                return rx.toast.error("User not found")

            # Check email uniqueness (excluding current user)
            existing_email = session.exec(
                select(GaladrielUser).where(
                    GaladrielUser.email == email,
                    GaladrielUser.id != self.user_id,
                )
            ).one_or_none()
            if existing_email:
                return rx.toast.error(ERR_EMAIL_IN_USE)

            role = session.exec(
                select(GaladrielUserRole).where(GaladrielUserRole.name == role_name)
            ).one_or_none()
            if role is None or role_name == "admin":
                return rx.toast.error(ERR_ROLE_INVALID)

            galadriel_user.email = email
            galadriel_user.user_role = role.id

            local_user = session.exec(
                reflex_local_auth.LocalUser.select().where(
                    reflex_local_auth.LocalUser.id == galadriel_user.user_id
                )
            ).one_or_none()
            if local_user:
                local_user.enabled = enabled

            session.commit()

        return rx.redirect(f"{USERS_ROUTE}/{self.user_id}")
