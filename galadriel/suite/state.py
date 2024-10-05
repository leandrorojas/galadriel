from typing import List, Optional
import reflex as rx
from .model import SuiteModel, SuiteChildModel
from ..navigation import routes

from datetime import datetime

SUITES_ROUTE = routes.SUITES
if SUITES_ROUTE.endswith("/"): SUITES_ROUTE = SUITES_ROUTE[:-1]

class SuiteState(rx.State):
    suites: List['SuiteModel'] = []
    suite: Optional['SuiteModel'] = None

    children: List['SuiteChildModel'] = []
    child: Optional['SuiteChildModel'] = None

    show_case_search:bool = False

    @rx.var
    def suite_id(self):
        #print(self.router.page.params)
        return self.router.page.params.get("id", "")
    
    @rx.var
    def suite_url(self):
        if not self.suite:
            return f"{SUITES_ROUTE}"
        return f"{SUITES_ROUTE}/{self.suite.id}"
    
    @rx.var
    def suite_edit_url(self):
        if not self.suite:
            return f"{SUITES_ROUTE}"
        return f"{SUITES_ROUTE}/{self.suite.id}/edit"

    def get_suite_detail(self):                
        with rx.session() as session:
            if (self.suite_id == ""):
                self.suite = None
                return
            result = session.exec(SuiteModel.select().where(SuiteModel.id == self.suite_id)).one_or_none()
            self.suite = result

    def load_suites(self):
        with rx.session() as session:
            results = session.exec(SuiteModel.select()).all()
            self.suites = results

    def add_suite(self, form_data:dict):
        with rx.session() as session:
            suite = SuiteModel(**form_data)
            session.add(suite)
            session.commit()
            session.refresh(suite)
            self.suite = suite
    
    def save_suite_edits(self, suite_id:int, updated_data:dict):
        with rx.session() as session:        
            suite = session.exec(SuiteModel.select().where(SuiteModel.id == suite_id)).one_or_none()

            if (suite is None):
                return
            for key, value in updated_data.items():
                setattr(suite, key, value)

            session.add(suite)
            session.commit()
            session.refresh(suite)
            self.suite = suite

    def to_suite(self, edit_page=True):
        if not self.suite:
            return rx.redirect(routes.SUITES)
        if edit_page:
            return rx.redirect(self.suite_edit_url)
        return rx.redirect(self.suite_url)
    
    def toggle_case_search(self):
        self.show_case_search = not(self.show_case_search)

    def load_children(self):
        with rx.session() as session:
            results = session.exec(SuiteChildModel.select().where(SuiteChildModel.suite_id == self.suite_id).order_by(SuiteChildModel.order)).all()
            # if (len(results) > 0):
            #     for single_result in results:
            #         case_name = session.exec(CaseModel.select().where(CaseModel.id == single_result.case_id)).first()
            #         setattr(single_result, "case_name", case_name.name)
            self.children = results

class AddSuiteState(SuiteState):
    form_data:dict = {}

    def handle_submit(self, form_data):
        self.form_data = form_data
        self.add_suite(form_data)
        return rx.redirect(routes.SUITES)

class EditSuiteState(SuiteState):
    form_data:dict = {}
    # suite_name:str = ""
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        suite_id = form_data.pop("suite_id")
        updated_data = {**form_data}
        self.save_suite_edits(suite_id, updated_data)
        return rx.redirect(routes.SUITES)
        #return self.to_suite() #<-- review this code, why it was changed?