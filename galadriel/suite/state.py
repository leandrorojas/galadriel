from typing import List, Optional
import reflex as rx
from .model import Suite
from ..navigation import routes

class SuiteState(rx.State):
    suites: List['Suite'] = []
    suite: Optional['Suite'] = None
    suite_name:str = ""

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
    
    def save_suite_edits(self, suite_id:int, updated_data:dict):
        with rx.session() as session:        
            suite = session.exec(Suite.select().where(Suite.id == suite_id)).one_or_none()

            if (suite is None):
                return
            for key, value in updated_data.items():
                setattr(suite, key, value)

            session.add(suite)
            session.commit()
            session.refresh(suite)
            self.suite = suite

    def to_suite(self):
        if not self.suite:
            return rx.redirect(routes.SUITES_ROUTE)
        return rx.redirect(routes.SUITES_ROUTE + f"/{self.suite.id}/")

class AddSuiteState(SuiteState):
    form_data:dict = {}

    def handle_submit(self, form_data):
        self.form_data = form_data
        self.add_suite(form_data)

class EditSuiteState(SuiteState):
    form_data:dict = {}
    # suite_name:str = ""
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        suite_id = form_data.pop("suite_id")
        updated_data = {**form_data}
        self.save_suite_edits(suite_id, updated_data)
        return self.to_suite()