from datetime import datetime, timezone
import asyncio
import reflex as rx
import sqlalchemy as sa
from ..ui.base import base_page
from sqlmodel import Field

from .. import navigation

def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)

class ContactModel(rx.Model, table=True):
    first_name:str | None = None
    last_name:str | None = None
    email:str
    contact_message:str
    created: datetime = Field(
        default_factory=get_utc_now, 
        sa_type=sa.DateTime(timezone=True),
        sa_column_kwargs={
            'server_default': sa.func.now()
        },
        nullable=False,
    )

class ContactState(rx.State):
    form_data: dict = {}
    submitted: bool = False

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

@rx.page(route=navigation.routes.CONTACT_ROUTE)
def contact_page() -> rx.Component:

    contact_form = rx.form(
        rx.vstack(
            rx.hstack(
                rx.input(
                    name="first_name",
                    placeholder="First Name",
                    width="100%",
                ),
                rx.input(
                    name="last_name",
                    placeholder="Last Name",
                    width="100%",
                ),
                width="100%",
            ),
            rx.input(
                name="email",
                placeholder="name@domain.com",
                type="email", 
                required=True,
                width="100%",
            ),
            rx.text_area(
                name="contact_message",
                placeholder="Escríbanos su mensaje",
                required=True,
                width="100%",
            ),
            rx.button("Submit", type="submit", width="100%",),
        ),
        on_submit=ContactState.handle_submit,
        reset_on_submit=True,
    ),

    contact_content = rx.vstack(
        rx.heading("Contact Us"),
        rx.cond(ContactState.submitted, "Graciavóh, {email}".format(email=ContactState.contact_email), ""),
        rx.desktop_only(
            rx.box(
                contact_form,
                width="50vw",
            ),
        ),
        rx.mobile_and_tablet(
            rx.box(
                contact_form,
                width="55vw"
            ),
        ),
        rx.link(
            rx.button("Check out our ducks!"),
            href=navigation.routes.HOME_ROUTE,
            is_extgsernal=True,
        ),
        spacing="5",
        justify="center",
        align="center",
        min_height="85vh",
    ),
    
    return base_page(contact_content)