from typing import List, Optional
import reflex as rx
from .model import ScenarioModel, ScenarioCaseModel
from ..navigation import routes

from ..case.model import CaseModel, StepModel

from sqlmodel import select, asc, or_, func, cast, String

SCENARIO_ROUTE = routes.SCENARIOS
if SCENARIO_ROUTE.endswith("/"): SCENARIO_ROUTE = SCENARIO_ROUTE[:-1]

RETURN_VALUE = 0

class ScenarioState(rx.State):
    scenarios: List['ScenarioModel'] = []
    scenario: Optional['ScenarioModel'] = None

    test_cases: List['ScenarioCaseModel'] = []
    test_cases_for_search: List['CaseModel'] = []

    show_search:bool = False
    search_value:str = ""

    @rx.var
    def scenario_id(self) -> str:
        return self.router.page.params.get("id", "")
    
    @rx.var
    def scenario_url(self) -> str:
        if not self.scenario:
            return str(f"{SCENARIO_ROUTE}")
        return str(f"{SCENARIO_ROUTE}/{self.scenario.id}")
    
    @rx.var
    def scenario_edit_url(self) -> str:
        if not self.scenario:
            return f"{SCENARIO_ROUTE}"
        return f"{SCENARIO_ROUTE}/{self.scenario.id}/edit"

    def get_scenario_detail(self):
        self.show_search = False
        with rx.session() as session:
            if (self.scenario_id == ""):
                self.scenario = None
                return            
            result = session.exec(ScenarioModel.select().where(ScenarioModel.id == self.scenario_id)).one_or_none()
            self.scenario = result

    def load_scenarios(self):
        with rx.session() as session:
            results = session.exec(ScenarioModel.select()).all()
            self.scenarios = results

    def add_scenario(self, form_data:dict):
        if (form_data["name"] == ""): return None
        with rx.session() as session:
            scenario = ScenarioModel(**form_data)
            session.add(scenario)
            session.commit()
            session.refresh(scenario)
            self.scenario = scenario

            return RETURN_VALUE
    
    def save_scenario_edits(self, scenario_id:int, updated_data:dict):
        if updated_data["name"] == "": return None
        with rx.session() as session:        
            scenario = session.exec(ScenarioModel.select().where(ScenarioModel.id == scenario_id)).one_or_none()

            if (scenario is None):
                return
            for key, value in updated_data.items():
                setattr(scenario, key, value)

            session.add(scenario)
            session.commit()
            session.refresh(scenario)
            self.scenario = scenario

            return RETURN_VALUE

    def to_scenario(self, edit_page=True):
        if not self.scenario:
            return rx.redirect(routes.SCENARIOS)
        if edit_page:
            return rx.redirect(self.scenario_edit_url)
        return rx.redirect(self.scenario_url)
    
    def toggle_search(self):
        self.show_search = not(self.show_search)

    def load_cases(self):
        with rx.session() as session:
            results = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.scenario_id == self.scenario_id).order_by(ScenarioCaseModel.order)).all()
            if (len(results) > 0):
                for single_result in results:
                    case_name = session.exec(CaseModel.select().where(CaseModel.id == single_result.case_id)).first()
                    setattr(single_result, "case_name", case_name.name)
            self.test_cases = results
    
    def filter_test_cases(self, search_value):
        self.search_value = search_value
        self.load_cases_for_search()

    def load_cases_for_search(self):
      with rx.session() as session:
            query = select(CaseModel)
            if self.search_value:
                search_value = (f"%{str(self.search_value).lower()}%")
                query = query.where(cast(CaseModel.name, String).ilike(search_value))

            results = session.exec(query).all()
            self.test_cases_for_search = results

    def link_case(self, case_id:int):
        if not self.has_steps(case_id): return rx.toast.error("test case must have at least one step")

        scenario_case_data:dict = {"scenario_id":""}
        new_case_order = 1

        if (len(self.test_cases) > 0):
            with rx.session() as session:
                linked_cases:ScenarioCaseModel = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.scenario_id == self.scenario_id)).all()
                max_order = 0
                for linked_case in linked_cases:
                    if (linked_case.case_id == case_id):
                        return rx.toast.error("prerequisite already in list")
                    
                    if linked_case.order > max_order:
                        max_order = linked_case.order
                new_case_order = max_order + 1

                #TODO: if failes in othe add name of the Test Case here?

        scenario_case_data.update({"scenario_id":self.scenario_id})
        scenario_case_data.update({"case_id":case_id})
        scenario_case_data.update({"order":new_case_order})
        scenario_case_data.update({"case_name":""})

        with rx.session() as session:
            case_to_add = ScenarioCaseModel(**scenario_case_data)
            session.add(case_to_add)
            session.commit()
            session.refresh(case_to_add)
        self.search_value = ""
        self.load_cases()
        
        return rx.toast.success("case added!")
    
    def unlink_case(self, scenario_case_id:int):
        with rx.session() as session:
            case_to_delete = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.id == scenario_case_id)).first()
            order_to_update = case_to_delete.order
            session.delete(case_to_delete)
            session.commit()

            cases_to_update = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.order > order_to_update)).all()
            for test_case in cases_to_update:
                test_case.order = test_case.order - 1
                session.add(test_case)
                session.commit()
                session.refresh(test_case)
        self.load_cases()
        return rx.toast.info("case unlinked")
    
    def move_case_up(self, scenario_case_id:int):
        with rx.session() as session:
            case_going_up = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.id == scenario_case_id)).first()
            old_order = case_going_up.order
            if (old_order != 1):
                case_going_down = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.order == (old_order -1), ScenarioCaseModel.scenario_id == self.scenario_id)).first()
                new_order = case_going_down.order

                case_going_up.order = new_order
                session.add(case_going_up)
                session.commit()
                session.refresh(case_going_up)

                case_going_down.order = old_order
                session.add(case_going_down)
                session.commit()
                session.refresh(case_going_down)

                self.load_cases()
            else:
                return rx.toast.warning("The case has reached min")
            
    def move_case_down(self, scenario_case_id:int):
        with rx.session() as session:
            case_going_down = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.id == scenario_case_id)).first()
            old_order = case_going_down.order
            case_going_up = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.order == (old_order +1), ScenarioCaseModel.scenario_id == self.scenario_id)).first()

            if (case_going_up is not None):
                new_order = case_going_up.order

                case_going_down.order = new_order
                session.add(case_going_down)
                session.commit()
                session.refresh(case_going_down)

                case_going_up.order = old_order
                session.add(case_going_up)
                session.commit()
                session.refresh(case_going_up)

                self.load_cases()
            else:
                return rx.toast.warning("The case has reached max")

    def has_steps(self, case_id:int) -> bool:
        with rx.session() as session:
            case_steps = session.exec(StepModel.select().where(StepModel.case_id == case_id)).all()

            return len(case_steps) > 0

class AddScenarioState(ScenarioState):
    form_data:dict = {}

    def handle_submit(self, form_data):
        self.form_data = form_data
        result = self.add_scenario(form_data)

        if result is None: return rx.toast.error("name cannot be empty")
        return rx.redirect(routes.SCENARIOS)

class EditScenarioState(ScenarioState):
    form_data:dict = {}
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        scenario_id = form_data.pop("scenario_id")
        updated_data = {**form_data}
        result = self.save_scenario_edits(scenario_id, updated_data)

        if result is None: return rx.toast.error("name cannot be empty")
        return rx.redirect(routes.SCENARIOS)