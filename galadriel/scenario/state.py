from typing import List, Optional
import reflex as rx
from .model import ScenarioModel, ScenarioCaseModel
from ..navigation import routes

from ..case.model import CaseModel

SCENARIO_ROUTE = routes.SCENARIOS
if SCENARIO_ROUTE.endswith("/"): SCENARIO_ROUTE = SCENARIO_ROUTE[:-1]

class ScenarioState(rx.State):
    scenarios: List['ScenarioModel'] = []
    scenario: Optional['ScenarioModel'] = None

    test_cases: List['ScenarioCaseModel'] = []

    show_search:bool = False

    @rx.var
    def scenario_id(self):
        #print(self.router.page.params)
        return self.router.page.params.get("id", "")
    
    @rx.var
    def scenario_url(self):
        if not self.scenario:
            return f"{SCENARIO_ROUTE}"
        return f"{SCENARIO_ROUTE}/{self.scenario.id}"
    
    @rx.var
    def scenario_edit_url(self):
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
        with rx.session() as session:
            scenario = ScenarioModel(**form_data)
            session.add(scenario)
            session.commit()
            session.refresh(scenario)
            self.scenario = scenario
    
    def save_scenario_edits(self, scenario_id:int, updated_data:dict):
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

    def to_scenario(self, edit_page=True):
        if not self.scenario:
            return rx.redirect(routes.SCENARIOS)
        if edit_page:
            return rx.redirect(self.scenario_edit_url)
        return rx.redirect(self.scenario_url)
    
    def toggle_search(self):
        self.show_search = not(self.show_search)

    def load_test_cases(self):
        with rx.session() as session:
            results = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.scenario_id == self.scenario_id).order_by(ScenarioCaseModel.order)).all()
            if (len(results) > 0):
                for single_result in results:
                    case_name = session.exec(CaseModel.select().where(CaseModel.id == single_result.case_id)).first()
                    setattr(single_result, "case_name", case_name.name)
            self.test_cases = results

class AddScenarioState(ScenarioState):
    form_data:dict = {}

    def handle_submit(self, form_data):
        self.form_data = form_data
        self.add_scenario(form_data)
        return rx.redirect(routes.SCENARIOS)

class EditScenarioState(ScenarioState):
    form_data:dict = {}
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        scenario_id = form_data.pop("scenario_id")
        updated_data = {**form_data}
        self.save_scenario_edits(scenario_id, updated_data)
        return rx.redirect(routes.SCENARIOS) # self.to_scenario()