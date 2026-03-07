import reflex as rx
import reflex_local_auth

from typing import List, Optional
from sqlmodel import select

from .model import GaladrielUser, GaladrielUserRole, GaladrielUserDisplay
from ..navigation import routes
from ..utils import consts

from enum import Enum

USERS_ROUTE = consts.normalize_route(routes.USERS)

class UserRole(Enum):
    ADMIN = 0
    EDITOR = 2
    VIEWER = 1

class UserState(rx.State):
    users: List['GaladrielUserDisplay'] = []
    user: Optional['GaladrielUserDisplay'] = None

    @rx.var(cache=True)
    def user_id(self) -> int:
        try:
            return int(self.router.page.params.get(consts.FIELD_ID, "0"))
        except ValueError:
            return -1

    @rx.var(cache=True)
    def user_edit_url(self) -> str:
        if not self.user:
            return f"{USERS_ROUTE}"
        return f"{USERS_ROUTE}/{self.user.galadriel_user_id}/edit"

    def load_users(self):
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

    def get_user_detail(self):
        with rx.session() as session:
            if (self.user_id == -1):
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
