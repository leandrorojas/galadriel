"""Scenario state management and event handlers."""

from typing import List, Optional
import reflex as rx
from .model import ScenarioModel, ScenarioCaseModel
from ..navigation import routes
from ..utils import consts
from ..utils.mixins import reorder_move_up, reorder_move_down, reorder_delete, has_steps as _has_steps, toggle_sort_field, sort_items

from ..case.model import CaseModel, StepModel

from sqlmodel import select, cast, String

SCENARIO_ROUTE = consts.normalize_route(routes.SCENARIOS)

class ScenarioState(rx.State):
    """Manages scenario CRUD and linked test case operations."""

    scenarios: List['ScenarioModel'] = []
    scenario: Optional['ScenarioModel'] = None

    test_cases: List['ScenarioCaseModel'] = []
    test_case_count: int = 0
    test_cases_for_search: List['CaseModel'] = []

    show_search:bool = False
    search_value:str = ""

    sort_by: str = ""
    sort_asc: bool = True

    search_sort_by: str = ""
    search_sort_asc: bool = True

    @rx.var(cache=True)
    def scenario_id(self) -> str:
        return self.router._page.params.get(consts.FIELD_ID, "")
    
    @rx.var(cache=True)
    def scenario_url(self) -> str:
        if not self.scenario:
            return str(f"{SCENARIO_ROUTE}")
        return str(f"{SCENARIO_ROUTE}/{self.scenario.id}")
    
    @rx.var(cache=True)
    def scenario_edit_url(self) -> str:
        if not self.scenario:
            return f"{SCENARIO_ROUTE}"
        return f"{SCENARIO_ROUTE}/{self.scenario.id}/edit"

    def get_scenario_detail(self):
        """Load a single scenario by its route ID."""
        self.show_search = False
        with rx.session() as session:
            if (self.scenario_id == ""):
                self.scenario = None
                return            
            result = session.exec(ScenarioModel.select().where(ScenarioModel.id == self.scenario_id)).one_or_none()
            self.scenario = result

    def load_scenarios(self):
        """Load all scenarios from the database."""
        with rx.session() as session:
            results = session.exec(ScenarioModel.select()).all()
            self.scenarios = results

    def toggle_sort(self, field: str):
        """Cycle sort: default → asc → desc → default."""
        self.sort_by, self.sort_asc = toggle_sort_field(self.sort_by, self.sort_asc, field)

    @rx.var(cache=True)
    def sorted_scenarios(self) -> List['ScenarioModel']:
        """Return scenarios sorted by the current sort field and direction."""
        return sort_items(self.scenarios, self.sort_by, self.sort_asc)

    def toggle_search_sort(self, field: str):
        """Cycle search sort: default → asc → desc → default."""
        self.search_sort_by, self.search_sort_asc = toggle_sort_field(self.search_sort_by, self.search_sort_asc, field)

    @rx.var(cache=True)
    def sorted_cases_for_search(self) -> List['CaseModel']:
        """Return search cases sorted by the current search sort field."""
        return sort_items(self.test_cases_for_search, self.search_sort_by, self.search_sort_asc)

    def add_scenario(self, form_data:dict):
        """Create a new scenario from form data."""
        if (form_data["name"] == ""): return None
        with rx.session() as session:
            scenario = ScenarioModel(**form_data)
            session.add(scenario)
            session.commit()
            session.refresh(scenario)
            self.scenario = scenario

            return consts.RETURN_VALUE
    
    def save_scenario_edits(self, scenario_id:int, updated_data:dict):
        """Persist edits to an existing scenario."""
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

            return consts.RETURN_VALUE

    def to_scenario(self, edit_page=True):
        """Redirect to the scenario detail or edit page."""
        if not self.scenario:
            return rx.redirect(routes.SCENARIOS)
        if edit_page:
            return rx.redirect(self.scenario_edit_url)
        return rx.redirect(self.scenario_url)
    
    def toggle_search(self):
        """Toggle the search panel visibility."""
        self.show_search = not(self.show_search)

    def load_cases(self):
        """Load all cases linked to the current scenario."""
        with rx.session() as session:
            results = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.scenario_id == self.scenario_id).order_by(ScenarioCaseModel.order)).all()
            if (len(results) > 0):
                for single_result in results:
                    case_name = session.exec(CaseModel.select().where(CaseModel.id == single_result.case_id)).first()
                    setattr(single_result, "case_name", case_name.name if case_name else "unknown")
            self.test_cases = results
            self.test_case_count = len(results)
    
    def filter_test_cases(self, search_value):
        """Update the case search filter and reload results."""
        self.search_value = search_value
        self.load_cases_for_search()

    def load_cases_for_search(self):
        """Load cases matching the current search filter."""
        with rx.session() as session:
            query = select(CaseModel)
            if self.search_value:
                search_value = (f"%{str(self.search_value).lower()}%")
                query = query.where(cast(CaseModel.name, String).ilike(search_value))

            results = session.exec(query).all()
            self.test_cases_for_search = results

    def link_case(self, case_id:int):
        """Link a test case to the current scenario."""
        if not self.has_steps(case_id): return rx.toast.error("test case must have at least one step")

        with rx.session() as session:
            new_case_order = 1
            if (len(self.test_cases) > 0):
                linked_cases:ScenarioCaseModel = session.exec(ScenarioCaseModel.select().where(ScenarioCaseModel.scenario_id == self.scenario_id)).all()
                max_order = 0
                for linked_case in linked_cases:
                    if (linked_case.case_id == case_id):
                        return rx.toast.error(consts.MESSAGE_ALREADY_IN_LIST)

                    if linked_case.order > max_order:
                        max_order = linked_case.order
                new_case_order = max_order + 1

            scenario_case_data = {
                "scenario_id": self.scenario_id,
                "case_id": case_id,
                "order": new_case_order,
                "case_name": "",
            }

            case_to_add = ScenarioCaseModel(**scenario_case_data)
            session.add(case_to_add)
            session.commit()
            session.refresh(case_to_add)
        self.search_value = ""
        self.load_cases()

        return rx.toast.success("case added!")
    
    def unlink_case(self, scenario_case_id:int):
        """Remove a case from the scenario and reorder remaining cases."""
        toast = reorder_delete(ScenarioCaseModel, scenario_case_id, "scenario_id", self.scenario_id, "case")
        self.load_cases()
        return toast

    def move_case_up(self, scenario_case_id:int):
        """Move a case one position up in the order."""
        toast = reorder_move_up(ScenarioCaseModel, scenario_case_id, "scenario_id", self.scenario_id, "case")
        if toast is None:
            self.load_cases()
        return toast

    def move_case_down(self, scenario_case_id:int):
        """Move a case one position down in the order."""
        toast = reorder_move_down(ScenarioCaseModel, scenario_case_id, "scenario_id", self.scenario_id, "case")
        if toast is None:
            self.load_cases()
        return toast

    def has_steps(self, case_id:int) -> bool:
        """Return True if the case has at least one step."""
        return _has_steps(StepModel, case_id)

class AddScenarioState(ScenarioState):
    """Handles the add-scenario form submission."""

    form_data:dict = {}

    def handle_submit(self, form_data):
        """Validate and create a new scenario from the form."""
        self.form_data = form_data
        result = self.add_scenario(form_data)

        if result is None: return rx.toast.error("name cannot be empty")
        return rx.redirect(routes.SCENARIOS)

class EditScenarioState(ScenarioState):
    """Handles the edit-scenario form submission."""

    form_data:dict = {}

    def handle_submit(self, form_data):
        """Validate and save scenario edits from the form."""
        self.form_data = form_data
        try:
            scenario_id = form_data.pop("scenario_id")
        except KeyError:
            return rx.toast.error("Invalid scenario ID")
        updated_data = {**form_data}
        result = self.save_scenario_edits(scenario_id, updated_data)

        if result is None: return rx.toast.error("name cannot be empty")
        return rx.redirect(routes.SCENARIOS)