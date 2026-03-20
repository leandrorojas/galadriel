"""Test case state management and event handlers."""

import reflex as rx
import sqlmodel

from typing import List, Optional
from .model import CaseModel, StepModel, PrerequisiteModel
from ..navigation import routes
from ..utils import consts, timing
from ..utils.mixins import reorder_move_up, reorder_move_down, reorder_delete, has_steps as _has_steps, toggle_sort_field, sort_items, search_by_name

from datetime import datetime


CASE_ROUTE = consts.normalize_route(routes.CASES)

class CaseState(rx.State):
    """Manages test case CRUD, steps, and prerequisites."""

    cases: List['CaseModel'] = []
    case: Optional['CaseModel'] = None

    steps: List['StepModel'] = []
    step_count: int = 0

    prerequisites: List['PrerequisiteModel'] = []
    prerequisite_count: int = 0

    search_value:str = ""
    show_search:bool = False

    sort_by: str = ""
    sort_asc: bool = True

    search_sort_by: str = ""
    search_sort_asc: bool = True

    @rx.var(cache=True)
    def case_id(self) -> int:
        try:
            return int(self.router._page.params.get(consts.FIELD_ID, "0"))
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
        """Load a single case by its route ID."""
        self.show_search = False
        with rx.session() as session:
            if (self.case_id == 0):
                self.case = None
                return
            result = session.exec(CaseModel.select().where(CaseModel.id == self.case_id)).one_or_none()
            self.case = result

    def load_cases(self):
        """Load all cases with step and prerequisite counts."""
        cases = search_by_name(CaseModel, self.search_value)
        if cases:
            case_ids = [case.id for case in cases]
            with rx.session() as session:
                step_counts = dict(session.exec(
                    sqlmodel.select(StepModel.case_id, sqlmodel.func.count(StepModel.id))
                    .where(StepModel.case_id.in_(case_ids))
                    .group_by(StepModel.case_id)
                ).all())
                prereq_counts = dict(session.exec(
                    sqlmodel.select(PrerequisiteModel.case_id, sqlmodel.func.count(PrerequisiteModel.id))
                    .where(PrerequisiteModel.case_id.in_(case_ids))
                    .group_by(PrerequisiteModel.case_id)
                ).all())
                for case in cases:
                    case.step_count = step_counts.get(case.id, 0)
                    case.prerequisite_count = prereq_counts.get(case.id, 0)
        self.cases = cases

    def toggle_sort(self, field: str):
        """Cycle sort: default → asc → desc → default."""
        self.sort_by, self.sort_asc = toggle_sort_field(self.sort_by, self.sort_asc, field)

    @rx.var(cache=True)
    def sorted_cases(self) -> List['CaseModel']:
        """Return cases sorted by the current sort field and direction."""
        return sort_items(self.cases, self.sort_by, self.sort_asc)

    def toggle_search_sort(self, field: str):
        """Cycle search sort: default → asc → desc → default."""
        self.search_sort_by, self.search_sort_asc = toggle_sort_field(self.search_sort_by, self.search_sort_asc, field)

    @rx.var(cache=True)
    def sorted_cases_for_search(self) -> List['CaseModel']:
        """Return prerequisite search cases sorted by the current search sort field."""
        return sort_items(self.cases, self.search_sort_by, self.search_sort_asc)

    def add_case(self, form_data:dict):
        """Create a new test case from form data."""
        if (form_data["name"] == ""): return None

        with rx.session() as session:
            existing = session.exec(CaseModel.select().where(CaseModel.name == form_data["name"])).first()
            if existing:
                return rx.toast.error("A test case with this name already exists")
            case = CaseModel(**form_data)
            session.add(case)
            session.commit()
            session.refresh(case)
            self.case = case

        return consts.RETURN_VALUE
    
    def save_case_edits(self, case_id:int, updated_data:dict):
        """Persist edits to an existing test case."""
        if (updated_data["name"] == ""): return None

        with rx.session() as session:
            existing = session.exec(CaseModel.select().where(CaseModel.name == updated_data["name"], CaseModel.id != case_id)).first()
            if existing:
                return rx.toast.error("A test case with this name already exists")
            case = session.exec(CaseModel.select().where(CaseModel.id == case_id)).one_or_none()

            if (case is None):
                return
            for key, value in updated_data.items():
                setattr(case, key, value)

            session.add(case)
            session.commit()
            session.refresh(case)
            self.case = case

            return consts.RETURN_VALUE

    def to_case(self, edit_page=True):
        """Redirect to the case detail or edit page."""
        if not self.case:
            return rx.redirect(routes.CASES)
        if edit_page:
            return rx.redirect(self.case_edit_url)
        return rx.redirect(self.case_url)
    
    def load_steps(self):
        """Load all steps for the current case, ordered by position."""
        with rx.session() as session:
            results = session.exec(StepModel.select().where(StepModel.case_id == self.case_id).order_by(StepModel.order)).all()
            self.steps = results
            self.step_count = len(results)

    def add_step(self, case_id:int, form_data:dict):
        """Add a new step to the specified case."""
        if (form_data["action"] == ""):
            return rx.toast.error("action cannot be empty")

        with rx.session() as session:
            new_step_order = 1
            if (len(self.steps) > 0):
                steps_order:StepModel = session.exec(StepModel.select().where(StepModel.case_id == self.case_id)).all()
                max_order = 0
                for step_order in steps_order:
                    if step_order.order > max_order:
                        max_order = step_order.order
                new_step_order = max_order + 1

            form_data.update({"case_id":case_id})
            form_data.update({"order":new_step_order})

            step_to_add = StepModel(**form_data)
            session.add(step_to_add)
            session.commit()
            session.refresh(step_to_add)
        self.load_steps()

        return rx.toast.success("step added!")
        
    def delete_step(self, step_id:int):
        """Delete a step and reorder remaining steps."""
        toast = reorder_delete(StepModel, step_id, "case_id", self.case_id, "step", min_count=1)
        self.load_steps()
        return toast
    
    def move_step_up(self, step_id:int):
        """Move a step one position up in the order."""
        toast = reorder_move_up(StepModel, step_id, "case_id", self.case_id, "step")
        if toast is None:
            self.load_steps()
        return toast

    def move_step_down(self, step_id:int):
        """Move a step one position down in the order."""
        toast = reorder_move_down(StepModel, step_id, "case_id", self.case_id, "step")
        if toast is None:
            self.load_steps()
        return toast

    def load_prerequisites(self):
        """Load all prerequisites for the current case."""
        with rx.session() as session:
            results = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == self.case_id).order_by(PrerequisiteModel.order)).all()
            if (len(results) > 0):
                for single_result in results:
                    case_name = session.exec(CaseModel.select().where(CaseModel.id == single_result.prerequisite_id)).first()
                    setattr(single_result, "prerequisite_name", case_name.name if case_name else "unknown")
            self.prerequisites = results
            self.prerequisite_count = len(results)

    def filter_cases(self, search_value):
        """Update the search filter and reload cases."""
        self.search_value = search_value
        self.load_cases()

    def has_steps(self, case_id:int) -> bool:
        """Return True if the case has at least one step."""
        return _has_steps(StepModel, case_id)

    def has_any_prerequisites(self, case_id:int) -> bool:
        """Return True if the case has any prerequisites."""
        with rx.session() as session:
            child_prerequisites = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == case_id)).first()
            return (child_prerequisites != None)

    def is_prerequisite_redundant(self, prerequisite_id: int, target_case_id: int) -> bool:
        """Check if adding the prerequisite would create a circular dependency."""
        with rx.session() as session:
            child_prerequisites = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == prerequisite_id)).all()

            for child_prerequisite in child_prerequisites:
                if int(child_prerequisite.prerequisite_id) == int(target_case_id):
                    return True
                if (self.has_any_prerequisites(child_prerequisite.prerequisite_id) and self.is_prerequisite_redundant(child_prerequisite.prerequisite_id, target_case_id)):
                    return True
        return False

    def add_prerequisite(self, prerequisite_id:int):
        """Link a prerequisite case to the current case."""
        if (int(self.case_id) == prerequisite_id): return rx.toast.error("self cannot be prerequisite")
        
        if self.has_any_prerequisites(prerequisite_id):
            if self.is_prerequisite_redundant(prerequisite_id, self.case_id):
                return rx.toast.error("cannot add redundant prerequisite")
            
        if not self.has_steps(prerequisite_id): return rx.toast.error("prerequisite must have at least one step")
        
        with rx.session() as session:
            new_prerequisite_order = 1
            if (len(self.prerequisites) > 0):
                linked_prerequisites:PrerequisiteModel = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == self.case_id)).all()
                max_order = 0
                for linked_prerequisite in linked_prerequisites:
                    if (linked_prerequisite.prerequisite_id == prerequisite_id): return rx.toast.error(consts.MESSAGE_PREREQUISITE_ALREADY_IN_LIST)

                    if linked_prerequisite.order > max_order:
                        max_order = linked_prerequisite.order
                new_prerequisite_order = max_order + 1

            prerequisite_data = {
                "case_id": self.case_id,
                "prerequisite_id": prerequisite_id,
                "order": new_prerequisite_order,
                "prerequisite_name": "",
            }

            prerequisite_to_add = PrerequisiteModel(**prerequisite_data)
            session.add(prerequisite_to_add)
            session.commit()
            session.refresh(prerequisite_to_add)
        self.search_value = ""
        self.load_prerequisites()

        return rx.toast.success("prerequisite added!")

    def toggle_search(self):
        """Toggle the search panel visibility."""
        self.show_search = not(self.show_search)

    def delete_prerequisite(self, prerequisite_id:int):
        """Delete a prerequisite and reorder remaining ones."""
        toast = reorder_delete(PrerequisiteModel, prerequisite_id, "case_id", self.case_id, "prerequisite")
        self.load_prerequisites()
        return toast

    def move_prerequisite_up(self, prerequisite_id:int):
        """Move a prerequisite one position up in the order."""
        toast = reorder_move_up(PrerequisiteModel, prerequisite_id, "case_id", self.case_id, "prerequisite")
        if toast is None:
            self.load_prerequisites()
        return toast

    def move_prerequisite_down(self, prerequisite_id:int):
        """Move a prerequisite one position down in the order."""
        toast = reorder_move_down(PrerequisiteModel, prerequisite_id, "case_id", self.case_id, "prerequisite")
        if toast is None:
            self.load_prerequisites()
        return toast
            
class AddCaseState(CaseState):
    """Handles the add-case form submission."""

    form_data:dict = {}

    def handle_submit(self, form_data):
        """Validate and create a new case from the form."""
        self.form_data = form_data
        result = self.add_case(form_data)
        if result is None: return rx.toast.error("name cannot be empty")
        if result != consts.RETURN_VALUE: return result
        return rx.redirect(routes.CASES)

class EditCaseState(CaseState):
    """Handles the edit-case form submission."""

    form_data:dict = {}

    def handle_submit(self, form_data):
        """Validate and save case edits from the form."""
        try:
            case_id = int(form_data.pop("case_id"))
        except (ValueError, KeyError):
            return rx.toast.error("Invalid case ID")
        self.form_data = form_data
        updated_data = {**form_data}
        result = self.save_case_edits(case_id, updated_data)
        if result is None: return rx.toast.error("name cannot be empty")
        if result != consts.RETURN_VALUE: return result
        return rx.redirect(self.case_url)
    
    def get_detail_url(self, id:int):
        """Return the detail URL for a given case ID."""
        return f"{CASE_ROUTE}/{id}"
    
class AddStepState(CaseState):
    """Handles the add-step form submission."""

    form_data:dict = {}

    def handle_submit(self, form_data):
        """Validate and add a new step from the form."""
        try:
            case_id = int(form_data.pop("case_id"))
        except (ValueError, KeyError):
            return rx.toast.error("Invalid case ID")
        self.form_data = form_data
        updated_data = {**form_data}
        result = self.add_step(case_id, updated_data)
        return result