import reflex as rx

from typing import List, Optional

from .model import GaladrielUser

from sqlmodel import select, cast, String

class UserState(rx.State):
    users: List['GaladrielUser'] = []
    user: Optional['GaladrielUser'] = None

    search_value:str = ""

    def load_users(self):
        with rx.session() as session:
            query = select(GaladrielUser)
            if self.search_value:
                search_value = (f"%{str(self.search_value).lower()}%")
                query = query.where(cast(GaladrielUser.email, String).ilike(search_value))

            results = session.exec(query).all()
            self.users = results