import reflex as rx
import reflex_local_auth

from typing import List, Optional

from .model import GaladrielUser, GaladrielUserRole, GaladrielUserDisplay

from sqlmodel import select, cast, String

class UserState(rx.State):
    users: List['GaladrielUserDisplay'] = []
    user: Optional['GaladrielUserDisplay'] = None

    search_value:str = ""

    def load_users(self):
        self.users.clear()
        with rx.session() as session:
            all_users = session.exec(GaladrielUser.select()).all()

            for single_user in all_users:
                local_user = session.exec(reflex_local_auth.LocalUser.select().where(reflex_local_auth.LocalUser.id == single_user.user_id)).one_or_none()

                if local_user:

                    self.users.append(
                        GaladrielUserDisplay(
                            local_user_id=local_user.id,
                            galadriel_user_id=single_user.id,
                            username=local_user.username,
                            email=single_user.email,
                            role=session.exec(select(GaladrielUserRole).where(GaladrielUserRole.id == single_user.user_role)).one_or_none().name,
                            enabled=local_user.enabled,
                            created=single_user.created,
                            updated=single_user.updated
                        )
                    )