from typing import List, Optional
import reflex as rx
from .model import CycleModel, CycleChildModel
from ..navigation import routes

from ..case.model import CaseModel, StepModel, PrerequisiteModel
from ..scenario.model import ScenarioModel, ScenarioCaseModel
from ..suite.model import SuiteModel, SuiteChildModel
from ..iteration.model import IterationModel, IterationStatusModel, IterationSnapshotModel

from datetime import datetime

from sqlmodel import select, asc, or_, func, cast, String, desc

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

    iteration_snapshot_items: List['IterationSnapshotModel'] = []

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
    def cycle_name(self) -> str:
        if not self.cycle:
            return ""
        return f"{self.cycle.name}"
    
    @rx.var
    def iteration_status_name(self) -> str:
        if not self.cycle:
            return ""
        with rx.session() as session:
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == self.cycle_id)).one_or_none()
            if (iteration != None):
                status_name = session.exec(select(IterationStatusModel).where(IterationStatusModel.id == iteration.iteration_status_id)).first()
                return status_name.name
            else:
                return ""

    @rx.var
    def has_iteration(self) -> bool:
        if not self.cycle:
            return False
        with rx.session() as session:
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == self.cycle_id)).one_or_none()
            return (iteration != None)
        
    @rx.var
    def iteration_url(self) -> str:
        if not self.cycle:
            return f"{CYCLES_ROUTE}"
        return f"{CYCLES_ROUTE}/{self.cycle.id}/iteration"

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

    def add_iteration_snapshot(self, cycle_id:int):
        iteration = None

        with rx.session() as session:
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == cycle_id)).one_or_none()

            if (iteration == None):
                children = session.exec(CycleChildModel.select().where(CycleChildModel.cycle_id == cycle_id).order_by(CycleChildModel.order)).all()
                if (len(children) > 0):
                    #add the cycle - iteration relationship
                    cycle_iteration_data:dict = {"cycle_id":cycle_id}

                    cycle_iteration_data.update({"iteration_status_id":0})
                    cycle_iteration_data.update({"iteration_number":1})

                    iteration_to_add = IterationModel(**cycle_iteration_data)
                    session.add(iteration_to_add)
                    session.commit()
                    session.refresh(iteration_to_add)

                    #add the cycle's snapshot here
                    for cycle_child in children:
                        match cycle_child.child_type_id:
                            case 1:
                                self.add_suite_to_snapshot(iteration_to_add.id, cycle_child.child_id)
                            case 2:
                                self.add_scenario_to_snapshot(iteration_to_add.id, cycle_child.child_id)
                            case 3:
                                self.add_case_to_snapshot(iteration_to_add.id, cycle_child.child_id)

                    self.load_cycles()
                    return self.resume_iteration_snapshot(cycle_id)

                else:
                    return rx.toast.warning("the cycle doesn't have any linked suites, scenarios or cases. Nothing was done")
                
            
    def resume_iteration_snapshot(self, cycle_id:int) -> rx.Component:
        with rx.session() as session:
            result = session.exec(CycleModel.select().where(CycleModel.id == cycle_id)).one_or_none()
            self.cycle = result
        return rx.redirect(self.iteration_url)
    
    def get_iteration_snapshot(self):
        with rx.session() as session:
            if (self.cycle_id == ""):
                self.cycle = None
                return
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == self.cycle_id)).one_or_none()
            self.iteration_snapshot_items = session.exec(select(IterationSnapshotModel).where(IterationSnapshotModel.iteration_id == iteration.id).order_by(asc(IterationSnapshotModel.order))).all()

    def get_max_iteration_snapshot_order(self, iteration_id:int):
        with rx.session() as session:
            snapshot_item = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.iteration_id == iteration_id).order_by(desc(IterationSnapshotModel.order))).first()

            max_order = 0
            if (snapshot_item != None):
                max_order = snapshot_item.order + 1

            return max_order
        
    #validate that the case is not yet added to the snapshot
    def is_case_in_snapshot(self, iteration_id:int, case_id:int) -> bool:
        with rx.session() as session:
            snapshot_case = session.exec(IterationSnapshotModel.select().where(
                IterationSnapshotModel.iteration_id == iteration_id,
                IterationSnapshotModel.child_id == case_id,
                IterationSnapshotModel.child_type == 3
            )).first()

            return (snapshot_case != None)

    def add_case_to_snapshot(self, iteration_id:int, case_id:int, is_prerequisite:bool = False):
        already_added = self.is_case_in_snapshot(iteration_id, case_id)

        if (already_added == False):
            with rx.session() as session:
                child_case = session.exec(CaseModel.select().where(CaseModel.id == case_id)).first()

                if (child_case != None):
                    max_order = self.get_max_iteration_snapshot_order(iteration_id)

                    if (is_prerequisite == False):
                        child_name = child_case.name
                    else:
                        child_name = f"[prerequisiste] {child_case.name}"

                    #cycle through prerequisites and insert them
                    prerequisites = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == case_id).order_by(PrerequisiteModel.order)).all()
                    
                    for prerequisite in prerequisites:
                        self.add_case_to_snapshot(iteration_id, prerequisite.prerequisite_id, True)

                    #insert the case
                    snapshot_case_data:dict = {
                        "iteration_id":iteration_id,
                        "order":max_order,
                        "child_type":3,
                        "child_id":case_id,
                        "child_name": child_name
                    }

                    case_to_add = IterationSnapshotModel(**snapshot_case_data)
                    session.add(case_to_add)
                    session.commit()

                    #cycle through case steps and insert them
                    steps = session.exec(StepModel.select().where(StepModel.case_id == case_id).order_by(StepModel.order)).all()

                    for step in steps:
                        max_order = max_order + 1

                        snapshot_step_data:dict = {
                            "iteration_id":iteration_id,
                            "order":max_order,
                            "child_type":4,
                            "child_action": step.action,
                            "child_expected": step.expected,
                            "child_status_id":1
                        }

                        step_to_add = IterationSnapshotModel(**snapshot_step_data)
                        session.add(step_to_add)
                        session.commit()

    def add_scenario_to_snapshot(self, iteration_id:int, scenario_id:int):
        with rx.session() as session:
            child_scenario = session.exec(ScenarioModel.select().where(ScenarioModel.id == scenario_id)).first()

            if (child_scenario != None):
                max_order = self.get_max_iteration_snapshot_order(iteration_id)

                #insert the case
                snapshot_scenario_data:dict = {
                    "iteration_id":iteration_id,
                    "order":max_order,
                    "child_type":2,
                    "child_id": scenario_id,
                    "child_name": child_scenario.name
                }

                scenario_to_add = IterationSnapshotModel(**snapshot_scenario_data)
                session.add(scenario_to_add)
                session.commit()

                #cycle through scenario cases and insert them
                cases_to_add = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.scenario_id == scenario_id).order_by(ScenarioCaseModel.order)).all()

                for case_to_add in cases_to_add:
                    self.add_case_to_snapshot(iteration_id, case_to_add.case_id)

    def add_suite_to_snapshot(self, iteration_id:int, suite_id:int):
        with rx.session() as session:
            child_suite = session.exec(SuiteModel.select().where(SuiteModel.id == suite_id)).first()

            if (child_suite != None):
                max_order = self.get_max_iteration_snapshot_order(iteration_id)

                #insert the case
                snapshot_suite_data:dict = {
                    "iteration_id":iteration_id,
                    "order":max_order,
                    "child_type":1,
                    "child_id": suite_id,
                    "child_name": child_suite.name
                }

                suite_to_add = IterationSnapshotModel(**snapshot_suite_data)
                session.add(suite_to_add)
                session.commit()

                #cycle through suite children and insert them
                suite_children_to_add = session.exec(SuiteChildModel.select().where(SuiteChildModel.suite_id == suite_id).order_by(SuiteChildModel.order)).all()

                for suite_child in suite_children_to_add:
                    match suite_child.child_type_id:
                        case 1:
                            self.add_scenario_to_snapshot(iteration_id, suite_child.child_id)
                        case 2:
                            self.add_case_to_snapshot(iteration_id, suite_child.child_id)

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