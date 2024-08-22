from typing import List, Optional
import reflex as rx
from .model import Suite

class SuiteState(rx.State):
    suites: List['Suite'] = []
    suite: Optional['Suite'] = None

    @rx.var
    def id(self):
        #print(self.router.page.params)
        return self.router.page.params.get("id", "")    

    def get_suite_detail(self):                
        with rx.session() as session:
            if (self.id == ""):
                self.suite = None
                return            
            result = session.exec(Suite.select().where(Suite.id == self.id)).one_or_none()
            self.suite = result

    def load_suites(self):
        with rx.session() as session:
            results = session.exec(Suite.select()).all()
            self.suites = results

    def add_suite(self, form_data:dict):
        with rx.session() as session:
            post = Suite(**form_data)
            session.add(post)
            session.commit()
            session.refresh(post)
            self.post = post

class AddSuiteState(SuiteState):
    form_data:dict = {}

    def handle_submit(self, form_data):
        self.form_data = form_data
        self.add_suite(form_data)