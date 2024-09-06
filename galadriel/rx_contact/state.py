
import asyncio
import reflex as rx

from typing import List
from sqlalchemy import select

from .model import RxTutorialContactModel
from ..rx_auth.state import RxTutorialSessionState

class RxTutorialContactState(RxTutorialSessionState):
    form_data: dict = {}
    submitted: bool = False
    entries: List['RxTutorialContactModel'] = []

    @rx.var
    def contact_email(self):
        return self.form_data.get("email")

    async def handle_submit(self, form_data: dict):
        #print(form_data)
        self.form_data = form_data

        #helps to narrow the data that only has values on it. This should go to a generic function
        clean_data = {}

        for key, value in form_data.items():
            if value == "" or value is None:
                continue
            clean_data[key] = value

        if self.my_user_id is not None:
            clean_data["user_id"] = self.my_user_id

        #print(clean_data)

        with rx.session() as session:
            contact = RxTutorialContactModel(**clean_data)
            session.add(contact)
            session.commit()            
            self.submitted = True
            yield

        await asyncio.sleep(5)
        self.submitted = False
        yield

    def list_entries(self):
        with rx.session() as session:
            entries = session.exec(RxTutorialContactModel.select()).all()
            #print(entries)
            self.entries = entries