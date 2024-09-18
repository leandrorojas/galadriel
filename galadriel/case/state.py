from typing import List, Optional
import reflex as rx
from .model import CaseModel, StepCaseModel
from ..navigation import routes

CASE_ROUTE = routes.CASES
if CASE_ROUTE.endswith("/"): CASE_ROUTE = CASE_ROUTE[:-1]

class CaseState(rx.State):
    cases: List['CaseModel'] = []
    case: Optional['CaseModel'] = None

    @rx.var
    def case_id(self):
        #print(self.router.page.params)
        return self.router.page.params.get("id", "") 
    
    @rx.var
    def case_url(self):
        if not self.case:
            return f"{CASE_ROUTE}"
        return f"{CASE_ROUTE}/{self.case.id}"
    
    @rx.var
    def case_edit_url(self):
        if not self.case:
            return f"{CASE_ROUTE}"
        return f"{CASE_ROUTE}/{self.case.id}/edit"

    def get_case_detail(self):                
        with rx.session() as session:
            if (self.case_id == ""):
                self.case = None
                return            
            result = session.exec(CaseModel.select().where(CaseModel.id == self.case_id)).one_or_none()
            self.case = result

    def load_cases(self):
        with rx.session() as session:
            results = session.exec(CaseModel.select()).all()
            self.cases = results

    def add_case(self, form_data:dict):
        with rx.session() as session:
            case = CaseModel(**form_data)
            session.add(case)
            session.commit()
            session.refresh(case)
            self.case = case
    
    def save_case_edits(self, case_id:int, updated_data:dict):
        with rx.session() as session:        
            case = session.exec(CaseModel.select().where(CaseModel.id == case_id)).one_or_none()

            if (case is None):
                return
            for key, value in updated_data.items():
                setattr(case, key, value)

            session.add(case)
            session.commit()
            session.refresh(case)
            self.case = case

    def to_case(self, edit_page=True):
        if not self.case:
            return rx.redirect(routes.CASES)
        if edit_page:
            return rx.redirect(self.case_edit_url)
        return rx.redirect(self.case_url)
    
    def load_steps(self):
        pass

    def load_prerequisites(self):
        pass

class AddCaseState(CaseState):
    form_data:dict = {}

    def handle_submit(self, form_data):
        self.form_data = form_data
        self.add_case(form_data)
        return rx.redirect(routes.CASES)

class EditCaseState(CaseState):
    form_data:dict = {}
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        case_id = form_data.pop("case_id")
        updated_data = {**form_data}
        self.save_case_edits(case_id, updated_data)
        #return rx.redirect(routes.CASES) # self.to_scenario()
        return rx.redirect(self.case_url)
    
    def get_detail_url(self, id:int):
        return f"{CASE_ROUTE}/{id}"