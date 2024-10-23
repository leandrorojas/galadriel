from typing import List, Optional
import reflex as rx
from .model import CycleModel, CycleChildModel
from ..navigation import routes

from ..case.model import CaseModel
from ..scenario.model import ScenarioModel
from ..suite.model import SuiteModel
from ..iteration.model import IterationModel, IterationStatusModel

from datetime import datetime

from sqlmodel import select, asc, or_, func, cast, String

CYCLES_ROUTE = routes.CYCLES
if CYCLES_ROUTE.endswith("/"): CYCLES_ROUTE = CYCLES_ROUTE[:-1]

RETURN_VALUE = 0
class CycleState(rx.State):
    cycles: List['CycleModel'] = []
    cycle: Optional['CycleModel'] = None

    children: List['CycleChildModel'] = []
    child: Optional['CycleChildModel'] = None

    show_case_search:bool = False
    search_case_value:str = ""
    cases_for_search: List['CaseModel'] = []

    show_scenario_search:bool = False
    search_scenario_value:str = ""
    scenarios_for_search: List['ScenarioModel'] = []

    show_suite_search:bool = False
    search_suite_value:str = ""
    suites_for_search: List['SuiteModel'] = []

    @rx.var
    def cycle_id(self):
        #print(self.router.page.params)
        return self.router.page.params.get("id", "")
    
    @rx.var
    def cycle_url(self) -> str:
        if not self.cycle:
            return f"{CYCLES_ROUTE}"
        return f"{CYCLES_ROUTE}/{self.cycle.id}"
    
    @rx.var
    def cycle_edit_url(self) -> str:
        if not self.cycle:
            return f"{CYCLES_ROUTE}"
        return f"{CYCLES_ROUTE}/{self.cycle.id}/edit"
    
    @rx.var
    def cycle_threshold(self) -> str:
        if not self.cycle:
            return 0
        return f"{self.cycle.threshold}"
    
    @rx.var
    def has_iteration(self) -> bool:
        if not self.cycle:
            return False
        
        with rx.session() as session:
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == self.cycle_id)).one_or_none()
            return (iteration != None)

    def get_cycle_detail(self):
        with rx.session() as session:
            if (self.cycle_id == ""):
                self.cycle = None
                return
            result = session.exec(CycleModel.select().where(CycleModel.id == self.cycle_id)).one_or_none()
            self.cycle = result

    def load_cycles(self):
        with rx.session() as session:
            results = session.exec(CycleModel.select()).all()

            for single_result in results:
                iteration_status = None
                iteration_status_name = ""
                cycle_iteration = session.exec(IterationModel.select().where(IterationModel.cycle_id == single_result.id)).one_or_none()
                if (cycle_iteration != None):
                    iteration_status = session.exec(IterationStatusModel.select().where(IterationStatusModel.id == cycle_iteration.iteration_status_id)).first()
                    if (iteration_status == None):
                        iteration_status_name = ""
                    else:
                        iteration_status_name = iteration_status.name

                setattr(single_result, "iteration_status_name", iteration_status_name)

            self.cycles = results

    def add_cycle(self, form_data:dict):
        if form_data["name"] == "": return "name"
        if form_data["threshold"] == "": return "threshold"
        with rx.session() as session:
            cycle = CycleModel(**form_data)
            session.add(cycle)
            session.commit()
            session.refresh(cycle)
            self.cycle = cycle

            return RETURN_VALUE
    
    def save_cycle_edits(self, cycle_id:int, updated_data:dict):
        if updated_data["name"] == "": return "name"
        if updated_data["threshold"] == "": return "threshold"
        with rx.session() as session:
            cycle = session.exec(CycleModel.select().where(CycleModel.id == cycle_id)).one_or_none()

            if (cycle is None):
                return
            for key, value in updated_data.items():
                setattr(cycle, key, value)

            session.add(cycle)
            session.commit()
            session.refresh(cycle)
            self.cycle = cycle

            return RETURN_VALUE

    # def to_suite(self, edit_page=True):
    #     if not self.cycle:
    #         return rx.redirect(routes.SUITES)
    #     if edit_page:
    #         return rx.redirect(self.suite_edit_url)
    #     return rx.redirect(self.suite_url)
    
    def collapse_searches(self):
        self.show_case_search = False
        self.show_scenario_search = False
        self.show_suite_search = False
    
    def toggle_case_search(self):
        self.show_case_search = not(self.show_case_search)

    def load_children(self):
        with rx.session() as session:
            results = session.exec(CycleChildModel.select().where(CycleChildModel.cycle_id == self.cycle_id).order_by(CycleChildModel.order)).all()
            if (len(results) > 0):
                for single_result in results:
                    child = None
                    if (single_result.child_type_id == 1):
                        child = session.exec(SuiteModel.select().where(SuiteModel.id == single_result.child_id)).first()
                    if (single_result.child_type_id == 2):
                        child = session.exec(ScenarioModel.select().where(ScenarioModel.id == single_result.child_id)).first()
                    elif (single_result.child_type_id == 3):
                        child = session.exec(CaseModel.select().where(CaseModel.id == single_result.child_id)).first()
                    setattr(single_result, "child_name", child.name)
            self.children = results

    def unlink_child(self, child_id:int):
        with rx.session() as session:
            child_to_delete = session.exec(CycleChildModel.select().where(CycleChildModel.id == child_id)).first()
            order_to_update = child_to_delete.order
            session.delete(child_to_delete)
            session.commit()

            children_to_update = session.exec(CycleChildModel.select().where(CycleChildModel.order > order_to_update)).all()
            for cycle_child in children_to_update:
                cycle_child.order = cycle_child.order - 1
                session.add(cycle_child)
                session.commit()
                session.refresh(cycle_child)
        self.load_children()
        return rx.toast.info("child unlinked")
    
    def move_child_up(self, child_id:int):
        with rx.session() as session:
            child_going_up = session.exec(CycleChildModel.select().where(CycleChildModel.id == child_id)).first()
            old_order = child_going_up.order
            if (old_order != 1):
                child_going_down = session.exec(CycleChildModel.select().where(CycleChildModel.order == (old_order -1), CycleChildModel.cycle_id == self.cycle_id)).first()
                new_order = child_going_down.order

                child_going_up.order = new_order
                session.add(child_going_up)
                session.commit()
                session.refresh(child_going_up)

                child_going_down.order = old_order
                session.add(child_going_down)
                session.commit()
                session.refresh(child_going_down)

                self.load_children()
            else:
                return rx.toast.warning("The child has reached min")
            
    def move_child_down(self, child_id:int):
        with rx.session() as session:
            child_going_down = session.exec(CycleChildModel.select().where(CycleChildModel.id == child_id)).first()
            old_order = child_going_down.order
            child_going_up = session.exec(CycleChildModel.select().where(CycleChildModel.order == (old_order +1), CycleChildModel.cycle_id == self.cycle_id)).first()

            if (child_going_up is not None):
                new_order = child_going_up.order

                child_going_down.order = new_order
                session.add(child_going_down)
                session.commit()
                session.refresh(child_going_down)

                child_going_up.order = old_order
                session.add(child_going_up)
                session.commit()
                session.refresh(child_going_up)

                self.load_children()
            else:
                return rx.toast.warning("The child has reached max")
    
    def get_max_child_order(self, child_id:int, child_type_id:int): #TODO: split this into two: get max order and already exists
        with rx.session() as session:
            linked_children:CycleChildModel = session.exec(CycleChildModel.select().where(CycleChildModel.cycle_id == self.cycle_id)).all()
            max_order = 0
            for linked_child in linked_children:
                if ((linked_child.child_id == child_id) and (linked_child.child_type_id == child_type_id)):
                    return -1
                
                if linked_child.order > max_order:
                    max_order = linked_child.order
            return max_order + 1

    def filter_test_cases(self, search_case_value):
        self.search_case_value = search_case_value
        self.load_cases_for_search()

    def load_cases_for_search(self):
      with rx.session() as session:
            query = select(CaseModel)
            if self.search_case_value:
                search_case_value = (f"%{str(self.search_case_value).lower()}%")
                query = query.where(cast(CaseModel.name, String).ilike(search_case_value))

            results = session.exec(query).all()
            self.cases_for_search = results

    def link_case(self, case_id:int):
        cycle_case_data:dict = {"cycle_id":""}
        new_case_order = 1

        if (len(self.cases_for_search) > 0):
            new_case_order = self.get_max_child_order(case_id, 3)

            if new_case_order == -1:
                return rx.toast.error("already in list")

        cycle_case_data.update({"cycle_id":self.cycle_id})
        cycle_case_data.update({"child_type_id":3})
        cycle_case_data.update({"child_id":case_id})
        cycle_case_data.update({"order":new_case_order})

        with rx.session() as session:
            case_to_add = CycleChildModel(**cycle_case_data)
            session.add(case_to_add)
            session.commit()
            session.refresh(case_to_add)
        self.search_case_value = ""
        self.collapse_searches()
        self.load_children()
        
        return rx.toast.success("case added!")

    def toggle_scenario_search(self):
        self.show_scenario_search = not(self.show_scenario_search)

    def filter_scenarios(self, search_scenario_value):
        self.search_scenario_value = search_scenario_value
        self.load_scenarios_for_search()

    def load_scenarios_for_search(self):
      with rx.session() as session:
            query = select(ScenarioModel)
            if self.search_scenario_value:
                search_scenario_value = (f"%{str(self.search_scenario_value).lower()}%")
                query = query.where(cast(ScenarioModel.name, String).ilike(search_scenario_value))

            results = session.exec(query).all()
            self.scenarios_for_search = results

    def link_scenario(self, scenario_id:int):
        cycle_scenario_data:dict = {"cycle_id":""}
        new_scenario_order = 1

        if (len(self.scenarios_for_search) > 0):
            new_scenario_order = self.get_max_child_order(scenario_id, 2)

            if new_scenario_order == -1:
                return rx.toast.error("already in list")

        cycle_scenario_data.update({"cycle_id":self.cycle_id})
        cycle_scenario_data.update({"child_type_id":2})
        cycle_scenario_data.update({"child_id":scenario_id})
        cycle_scenario_data.update({"order":new_scenario_order})

        with rx.session() as session:
            scenario_to_add = CycleChildModel(**cycle_scenario_data)
            session.add(scenario_to_add)
            session.commit()
            session.refresh(scenario_to_add)
        self.search_scenario_value = ""
        self.collapse_searches()
        self.load_children()
        
        return rx.toast.success("scenario added!")

    def toggle_suite_search(self):
        self.show_suite_search = not(self.show_suite_search)

    def filter_suites(self, search_suite_value):
        self.search_suite_value = search_suite_value
        self.load_suites_for_search()

    def load_suites_for_search(self):
      with rx.session() as session:
            query = select(SuiteModel)
            if self.search_suite_value:
                search_suite_value = (f"%{str(self.search_suite_value).lower()}%")
                query = query.where(cast(SuiteModel.name, String).ilike(search_suite_value))

            results = session.exec(query).all()
            self.suites_for_search = results

    def link_suite(self, suite_id:int):
        cycle_suite_data:dict = {"cycle_id":""}
        new_scenario_order = 1

        if (len(self.scenarios_for_search) > 0):
            new_scenario_order = self.get_max_child_order(suite_id, 1)

            if new_scenario_order == -1:
                return rx.toast.error("already in list")

        cycle_suite_data.update({"cycle_id":self.cycle_id})
        cycle_suite_data.update({"child_type_id":1})
        cycle_suite_data.update({"child_id":suite_id})
        cycle_suite_data.update({"order":new_scenario_order})

        with rx.session() as session:
            suite_to_add = CycleChildModel(**cycle_suite_data)
            session.add(suite_to_add)
            session.commit()
            session.refresh(suite_to_add)
        self.search_suite_value = ""
        self.collapse_searches()
        self.load_children()
        
        return rx.toast.success("scenario added!")

    def continue_or_add_iteration(self, cycle_id:int):
        iteration = None

        with rx.session() as session:
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == cycle_id)).one_or_none()

            if (iteration == None):
                cycle_iteration_data:dict = {"cycle_id":cycle_id}

                cycle_iteration_data.update({"iteration_status_id":0})
                cycle_iteration_data.update({"iteration_number":1})

                iteration_to_add = IterationModel(**cycle_iteration_data)
                session.add(iteration_to_add)
                session.commit()
                session.refresh(iteration_to_add)

                self.load_cycles()
            else:
                return rx.toast.info(f"opening cycle id {cycle_id}")

class AddCycleState(CycleState):
    form_data:dict = {}

    def handle_submit(self, form_data):
        self.form_data = form_data
        result = self.add_cycle(form_data)
        if result != 0:
            return rx.toast.error(f"{result} cannot be empty")
        return rx.redirect(routes.CYCLES)

class EditCycleState(CycleState):
    form_data:dict = {}
    # suite_name:str = ""
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        cycle_id = form_data.pop("cycle_id")
        updated_data = {**form_data}
        result = self.save_cycle_edits(cycle_id, updated_data)
        if result != 0:
            return rx.toast.error(f"{result} cannot be empty")        
        return rx.redirect(routes.CYCLES)
        #return self.to_suite() #<-- review this code, why it was changed?