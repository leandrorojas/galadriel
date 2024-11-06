from typing import List, Optional
import reflex as rx
from .model import CaseModel, StepModel, PrerequisiteModel
from ..navigation import routes

from sqlmodel import select, asc, or_, func, cast, String

CASE_ROUTE = routes.CASES
if CASE_ROUTE.endswith("/"): CASE_ROUTE = CASE_ROUTE[:-1]

RETURN_VALUE = 0

#TODO: rename "prerequisite_id" to another meaningful name like: "selected_case_id", selected_id or "selected_prerequisite_case_id". It has to mean that you are selecting a case_id

class CaseState(rx.State):
    cases: List['CaseModel'] = []
    case: Optional['CaseModel'] = None

    steps: List['StepModel'] = []

    prerequisites: List['PrerequisiteModel'] = []

    search_value:str = ""
    show_search:bool = False

    @rx.var
    def case_id(self):
        #print(self.router.page.params)
        return self.router.page.params.get("id", "") 
    
    @rx.var
    def case_url(self) -> str:
        if not self.case:
            return f"{CASE_ROUTE}"
        return f"{CASE_ROUTE}/{self.case.id}"
    
    @rx.var
    def case_edit_url(self) -> str:
        if not self.case:
            return f"{CASE_ROUTE}"
        return f"{CASE_ROUTE}/{self.case.id}/edit"

    def get_case_detail(self):
        self.show_search = False
        with rx.session() as session:
            if (self.case_id == ""):
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

        if (form_data["expected"] == ""):
            return rx.toast.error("expected cannot be empty")
        
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
        self.load_steps()
        return rx.toast.info("The step has been deleted")
    
    def move_step_up(self, step_id:int):
        with rx.session() as session:
            step_going_up = session.exec(StepModel.select().where(StepModel.id == step_id)).first()
            old_order = step_going_up.order
            if (old_order != 1):
                step_going_down = session.exec(StepModel.select().where(StepModel.order == (old_order -1), StepModel.case_id == self.case_id)).first()
                new_order = step_going_down.order

                step_going_up.order = new_order
                session.add(step_going_up)
                session.commit()
                session.refresh(step_going_up)

                step_going_down.order = old_order
                session.add(step_going_down)
                session.commit()
                session.refresh(step_going_down)

                self.load_steps()
            else:
                return rx.toast.warning("The step has reached min")

    def move_step_down(self, step_id:int):
        with rx.session() as session:
            step_going_down = session.exec(StepModel.select().where(StepModel.id == step_id)).first()
            old_order = step_going_down.order
            step_going_up = session.exec(StepModel.select().where(StepModel.order == (old_order +1), StepModel.case_id == self.case_id)).first()

            if (step_going_up is not None):
                new_order = step_going_up.order

                step_going_down.order = new_order
                session.add(step_going_down)
                session.commit()
                session.refresh(step_going_down)

                step_going_up.order = old_order
                session.add(step_going_up)
                session.commit()
                session.refresh(step_going_up)

                self.load_steps()
            else:
                return rx.toast.warning("The step has reached max")

    def load_prerequisites(self):
        with rx.session() as session:
            results = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == self.case_id).order_by(PrerequisiteModel.order)).all()
            if (len(results) > 0):
                for single_result in results:
                    case_name = session.exec(CaseModel.select().where(CaseModel.id == single_result.prerequisite_id)).first()
                    setattr(single_result, "prerequisite_name", case_name.name)
            self.prerequisites = results 

    def filter_cases(self, search_value):
        self.search_value = search_value
        self.load_cases()

    def has_prerequisite(self, prerequisite_id:int) -> bool:
        with rx.session() as session:
            child_prerequisites = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == prerequisite_id)).first()
            return (child_prerequisites != None)

    def is_prerequisite_redundant(self, prerequisite_id:int, target_case_id:int) -> bool:

        with rx.session() as session:
            child_prerequisites:PrerequisiteModel = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == prerequisite_id)).all()

            result = False
            for child_prerequisite in child_prerequisites:
                if (int(child_prerequisite.prerequisite_id) == int(target_case_id)):
                    return True
                else:
                    if self.has_prerequisite(child_prerequisite.prerequisite_id):
                        result = self.is_prerequisite_redundant(child_prerequisite.prerequisite_id, target_case_id)
                        if result:
                            return True

    def add_prerequisite(self, prerequisite_id:int):
        if (int(self.case_id) == prerequisite_id):
            return rx.toast.error("self cannot be prerequisite")
        
        if self.has_prerequisite(prerequisite_id):
            if self.is_prerequisite_redundant(prerequisite_id, self.case_id):
                return rx.toast.error("cannot add redundant prerequisite")
        
        prerequisite_data:dict = {"case_id":""}
        new_prerequisite_order = 1

        if (len(self.prerequisites) > 0):
            with rx.session() as session:
                linked_prerequisites:PrerequisiteModel = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == self.case_id)).all()
                max_order = 0
                for linked_prerequisite in linked_prerequisites:
                    if (linked_prerequisite.id == prerequisite_id):
                        return rx.toast.error("prerequisite already in list")
                    
                    if linked_prerequisite.order > max_order:
                        max_order = linked_prerequisite.order
                new_prerequisite_order = max_order + 1

                #TODO: if failes in othe add name of the Test Case here?

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
        with rx.session() as session:
            prerequisite_to_delete = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.id == prerequisite_id)).first()
            order_to_update = prerequisite_to_delete.order
            session.delete(prerequisite_to_delete)
            session.commit()

            prerequisites_to_update = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.order > order_to_update)).all()
            for prerequisite in prerequisites_to_update:
                prerequisite.order = prerequisite.order - 1
                session.add(prerequisite)
                session.commit()
                session.refresh(prerequisite)
        self.load_prerequisites()
        return rx.toast.info("The prerequisite has been deleted")

    def move_prerequisite_up(self, prerequisite_id:int):
        with rx.session() as session:
            prerequisite_going_up = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.id == prerequisite_id)).first()
            old_order = prerequisite_going_up.order
            if (old_order != 1):
                prerequisite_going_down = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.order == (old_order -1), PrerequisiteModel.case_id == self.case_id)).first()
                new_order = prerequisite_going_down.order

                prerequisite_going_up.order = new_order
                session.add(prerequisite_going_up)
                session.commit()
                session.refresh(prerequisite_going_up)

                prerequisite_going_down.order = old_order
                session.add(prerequisite_going_down)
                session.commit()
                session.refresh(prerequisite_going_down)

                self.load_prerequisites()
            else:
                return rx.toast.warning("The prerequisite has reached min")

    def move_prerequisite_down(self, prerequisite_id:int):
        with rx.session() as session:
            prerequisite_going_down = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.id == prerequisite_id)).first()
            old_order = prerequisite_going_down.order
            prerequisite_going_up = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.order == (old_order +1), PrerequisiteModel.case_id == self.case_id)).first()

            if (prerequisite_going_up is not None):
                new_order = prerequisite_going_up.order

                prerequisite_going_down.order = new_order
                session.add(prerequisite_going_down)
                session.commit()
                session.refresh(prerequisite_going_down)

                prerequisite_going_up.order = old_order
                session.add(prerequisite_going_up)
                session.commit()
                session.refresh(prerequisite_going_up)

                self.load_prerequisites()
            else:
                return rx.toast.warning("The prerequisite has reached max")

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
        self.form_data = form_data
        case_id = form_data.pop("case_id")
        updated_data = {**form_data}
        result = self.save_case_edits(case_id, updated_data)
        if result is None: return rx.toast.error("name cannot be empty")
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