
import asyncio
import reflex as rx

from typing import List
from sqlalchemy import select

from .model import ContactModel

class ContactState(rx.State):
    form_data: dict = {}
    submitted: bool = False
    entries: List['ContactModel'] = []

    @rx.var
    def contact_email(self):
        return self.form_data.get("email")

    async def handle_submit(self, form_data: dict):
        print(form_data)
        self.form_data = form_data

        #helps to narrow the data that only has values on it. This should go to a generic function
        clean_data = {}

        for key, value in form_data.items():
            if value == "" or value is None:
                continue
            clean_data[key] = value

        print(clean_data)

        with rx.session() as session:
            contact = ContactModel(**clean_data)
            session.add(contact)
            session.commit()            
            self.submitted = True
            yield

        await asyncio.sleep(5)
        self.submitted = False
        yield

    def list_entries(self):
        with rx.session() as session:
            entries = session.exec(select(ContactModel)).all()
            print(entries)
            self.entries = entries