import reflex as rx

from typing import List, Optional
from .model import CaseModel, StepModel, PrerequisiteModel
from ..navigation import routes
from ..utils import consts, timing
from ..utils.mixins import reorder_move_up, reorder_move_down, reorder_delete

from datetime import datetime

from sqlmodel import select, cast, String

CASE_ROUTE = routes.CASES
if CASE_ROUTE.endswith("/"): CASE_ROUTE = CASE_ROUTE[:-1]

RETURN_VALUE = 0

class CaseState(rx.State):
    cases: List['CaseModel'] = []
    case: Optional['CaseModel'] = None

    steps: List['StepModel'] = []

    prerequisites: List['PrerequisiteModel'] = []

    search_value:str = ""
    show_search:bool = False

    @rx.var(cache=True)
    def case_id(self) -> int:
        try:
            return int(self.router.page.params.get(consts.FIELD_ID, "0"))
        except ValueError:
            return 0
    
    @rx.var(cache=True)
    def case_url(self) -> str:
        if not self.case:
            return f"{CASE_ROUTE}"
        return f"{CASE_ROUTE}/{self.case.id}"
    
    @rx.var(cache=True)
    def case_edit_url(self) -> str:
        if not self.case:
            return f"{CASE_ROUTE}"
        return f"{CASE_ROUTE}/{self.case.id}/edit"

    def get_case_detail(self):
        self.show_search = False
        with rx.session() as session:
            if (self.case_id == 0):
                self.case = None
                return
            result = session.exec(CaseModel.select().where(CaseModel.id == self.case_id)).one_or_none()
            self.case = result

    def load_cases(self):
      with rx.session() as session:
            query = select(CaseModel)
            if self.search_value:
                search_value = (f"%{str(self.search_value).lower()}%")
                query = query.where(cast(CaseModel.name, String).ilike(search_value))

            results = session.exec(query).all()
            self.cases = results

    def add_case(self, form_data:dict):
        if (form_data["name"] == ""): return None

        with rx.session() as session:
            case = CaseModel(**form_data)
            session.add(case)
            session.commit()
            session.refresh(case)
            self.case = case

        return RETURN_VALUE
    
    def save_case_edits(self, case_id:int, updated_data:dict):
        if (updated_data["name"] == ""): return None

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

            return RETURN_VALUE

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
        if (form_data["action"] == ""): 
            return rx.toast.error("action cannot be empty")
        
        new_step_order = 1

        if (len(self.steps) > 0):
            with rx.session() as session:
                steps_order:StepModel = session.exec(StepModel.select().where(StepModel.case_id == self.case_id)).all()
                max_order = 0
                for step_order in steps_order:
                    if step_order.order > max_order:
                        max_order = step_order.order
                new_step_order = max_order + 1
            
        form_data.update({"case_id":case_id})
        form_data.update({"order":new_step_order})

        with rx.session() as session:
            step_to_add = StepModel(**form_data)
            session.add(step_to_add)
            session.commit()
            session.refresh(step_to_add)
        self.load_steps()
        
        return rx.toast.success("step added!")
        
    def delete_step(self, step_id:int):
        toast = reorder_delete(StepModel, step_id, "case_id", self.case_id, "step", min_count=1)
        self.load_steps()
        return toast
    
    def move_step_up(self, step_id:int):
        toast = reorder_move_up(StepModel, step_id, "case_id", self.case_id, "step")
        if toast is None:
            self.load_steps()
        return toast

    def move_step_down(self, step_id:int):
        toast = reorder_move_down(StepModel, step_id, "case_id", self.case_id, "step")
        if toast is None:
            self.load_steps()
        return toast

    def load_prerequisites(self):
        with rx.session() as session:
            results = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == self.case_id).order_by(PrerequisiteModel.order)).all()
            if (len(results) > 0):
                for single_result in results:
                    case_name = session.exec(CaseModel.select().where(CaseModel.id == single_result.prerequisite_id)).first()
                    setattr(single_result, "prerequisite_name", case_name.name if case_name else "unknown")
            self.prerequisites = results 

    def filter_cases(self, search_value):
        self.search_value = search_value
        self.load_cases()

    def has_steps(self, case_id:int) -> bool:
        with rx.session() as session:
            case_steps = session.exec(StepModel.select().where(StepModel.case_id == case_id)).all()

            return len(case_steps) > 0

    def has_any_prerequisites(self, case_id:int) -> bool:
        with rx.session() as session:
            child_prerequisites = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == case_id)).first()
            return (child_prerequisites != None)

    def is_prerequisite_redundant(self, prerequisite_id: int, target_case_id: int) -> bool:
        with rx.session() as session:
            child_prerequisites = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == prerequisite_id)).all()

            for child_prerequisite in child_prerequisites:
                if int(child_prerequisite.prerequisite_id) == int(target_case_id):
                    return True
                if (self.has_any_prerequisites(child_prerequisite.prerequisite_id) and self.is_prerequisite_redundant(child_prerequisite.prerequisite_id, target_case_id)):
                    return True
        return False

    def add_prerequisite(self, prerequisite_id:int):
        if (int(self.case_id) == prerequisite_id): return rx.toast.error("self cannot be prerequisite")
        
        if self.has_any_prerequisites(prerequisite_id):
            if self.is_prerequisite_redundant(prerequisite_id, self.case_id):
                return rx.toast.error("cannot add redundant prerequisite")
            
        if not self.has_steps(prerequisite_id): return rx.toast.error("prerequisite must have at least one step")
        
        prerequisite_data:dict = {"case_id": 0}
        new_prerequisite_order = 1

        if (len(self.prerequisites) > 0):
            with rx.session() as session:
                linked_prerequisites:PrerequisiteModel = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == self.case_id)).all()
                max_order = 0
                for linked_prerequisite in linked_prerequisites:
                    if (linked_prerequisite.prerequisite_id == prerequisite_id): return rx.toast.error(consts.MESSAGE_PREREQUISITE_ALREADY_IN_LIST)
                    
                    if linked_prerequisite.order > max_order:
                        max_order = linked_prerequisite.order
                new_prerequisite_order = max_order + 1

        prerequisite_data.update({"case_id":self.case_id})
        prerequisite_data.update({"prerequisite_id":prerequisite_id})
        prerequisite_data.update({"order":new_prerequisite_order})
        prerequisite_data.update({"prerequisite_name":""})

        with rx.session() as session:
            prerequisite_to_add = PrerequisiteModel(**prerequisite_data)
            session.add(prerequisite_to_add)
            session.commit()
            session.refresh(prerequisite_to_add)
        self.search_value = ""
        self.load_prerequisites()
        
        return rx.toast.success("prerequisite added!")

    def toggle_search(self):
        self.show_search = not(self.show_search)

    def delete_prerequisite(self, prerequisite_id:int):
        toast = reorder_delete(PrerequisiteModel, prerequisite_id, "case_id", self.case_id, "prerequisite")
        self.load_prerequisites()
        return toast

    def move_prerequisite_up(self, prerequisite_id:int):
        toast = reorder_move_up(PrerequisiteModel, prerequisite_id, "case_id", self.case_id, "prerequisite")
        if toast is None:
            self.load_prerequisites()
        return toast

    def move_prerequisite_down(self, prerequisite_id:int):
        toast = reorder_move_down(PrerequisiteModel, prerequisite_id, "case_id", self.case_id, "prerequisite")
        if toast is None:
            self.load_prerequisites()
        return toast
            
    def ensure_utc(self, dt) -> datetime:
        return timing.ensure_utc(dt)

class AddCaseState(CaseState):
    form_data:dict = {}

    def handle_submit(self, form_data):
        self.form_data = form_data
        result = self.add_case(form_data)
        if result is None: return rx.toast.error("name cannot be empty")
        return rx.redirect(routes.CASES)

class EditCaseState(CaseState):
    form_data:dict = {}
    
    def handle_submit(self, form_data):
        try:
            case_id = int(form_data.pop("case_id"))
        except (ValueError, KeyError):
            return rx.toast.error("Invalid case ID")
        self.form_data = form_data
        updated_data = {**form_data}
        result = self.save_case_edits(case_id, updated_data)
        if result is None: return rx.toast.error("name cannot be empty")
        return rx.redirect(self.case_url)
    
    def get_detail_url(self, id:int):
        return f"{CASE_ROUTE}/{id}"
    
class AddStepState(CaseState):
    form_data:dict = {}
    
    def handle_submit(self, form_data):
        try:
            case_id = int(form_data.pop("case_id"))
        except (ValueError, KeyError):
            return rx.toast.error("Invalid case ID")
        self.form_data = form_data
        updated_data = {**form_data}
        result = self.add_step(case_id, updated_data)
        return result