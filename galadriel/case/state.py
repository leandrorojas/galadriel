from typing import List, Optional
import reflex as rx
from .model import CaseModel, StepModel
from ..navigation import routes

from sqlalchemy import func

CASE_ROUTE = routes.CASES
if CASE_ROUTE.endswith("/"): CASE_ROUTE = CASE_ROUTE[:-1]

class CaseState(rx.State):
    cases: List['CaseModel'] = []
    case: Optional['CaseModel'] = None

    steps: List['StepModel'] = []
    step: Optional['StepModel'] = None

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
        with rx.session() as session:
            results = session.exec(StepModel.select().where(StepModel.case_id == self.case_id).order_by(StepModel.order)).all()
            self.steps = results

    def add_step(self, case_id:int, form_data:dict):

        if (form_data["action"] != ""):
            if (form_data["expected"] != ""):
                step_order = 1
                if (len(self.steps) > 0):
                    with rx.session() as session:
                        steps_order:StepModel = session.exec(StepModel.select().where(StepModel.case_id == self.case_id)).all()
                        max_order = 0

                        for step_order in steps_order:
                            if step_order.order > max_order:
                                max_order = step_order.order

                        step_order = max_order + 1
                else:
                    form_data["order"] = 1
                    
                form_data.update({"case_id":case_id})
                form_data.update({"order":step_order})

                with rx.session() as session:
                    step_to_add = StepModel(**form_data)
                    session.add(step_to_add)
                    session.commit()
                    session.refresh(step_to_add)
                    self.step = step_to_add
                self.load_steps()

                return rx.toast.success("step added!")
            else:
                return rx.toast.error("expected cannot be empty")
        else:
            return rx.toast.error("action cannot be empty")
        
    def delete_step(self, step_id:int):
        with rx.session() as session:
            step_to_delete = session.exec(StepModel.select().where(StepModel.id == step_id)).first()
            order_to_update = step_to_delete.order
            session.delete(step_to_delete)
            session.commit()

            steps_to_update = session.exec(StepModel.select().where(StepModel.order > order_to_update)).all()
            for step in steps_to_update:
                step.order = step.order - 1
                session.add(step)
                session.commit()
                session.refresh(step)

            #select all with order > order_to_update
            #go through the list, and update order = order - 1
            #commit
        self.load_steps() 
        return rx.toast.info("The step has been deleted.")

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
        return rx.redirect(self.case_url)
    
    def get_detail_url(self, id:int):
        return f"{CASE_ROUTE}/{id}"
    
class AddStepState(CaseState):
    form_data:dict = {}
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        case_id = form_data.pop("case_id")
        updated_data = {**form_data}
        result = self.add_step(case_id, updated_data)
        return result