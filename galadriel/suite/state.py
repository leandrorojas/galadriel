"""Suite state management and event handlers."""

from typing import List, Optional
import reflex as rx
from .model import SuiteModel, SuiteChildModel
from ..navigation import routes

from ..case.model import CaseModel, StepModel
from ..scenario.model import ScenarioModel

from ..utils import consts
from ..utils.mixins import reorder_move_up, reorder_move_down, reorder_delete, has_steps as _has_steps, get_max_child_order as _get_max_child_order, toggle_sort_field, sort_items, search_by_name

SUITES_ROUTE = consts.normalize_route(routes.SUITES)

class SuiteState(rx.State):
    """Manages suite CRUD and child linking operations."""

    suites: List['SuiteModel'] = []
    suite: Optional['SuiteModel'] = None

    children: List['SuiteChildModel'] = []
    child: Optional['SuiteChildModel'] = None
    child_count: int = 0

    cases_for_search: List['CaseModel'] = []
    show_case_search:bool = False
    search_case_value:str = ""

    scenarios_for_search: List['ScenarioModel'] = []
    show_scenario_search:bool = False
    search_scenario_value:str = ""

    sort_by: str = ""
    sort_asc: bool = True

    search_sort_by: str = ""
    search_sort_asc: bool = True

    @rx.var(cache=True)
    def suite_id(self) -> str:
        return self.router._page.params.get(consts.FIELD_ID, "")
    
    @rx.var(cache=True)
    def suite_url(self) -> str:
        if not self.suite:
            return f"{SUITES_ROUTE}"
        return f"{SUITES_ROUTE}/{self.suite.id}"
    
    @rx.var(cache=True)
    def suite_edit_url(self) -> str:
        if not self.suite:
            return f"{SUITES_ROUTE}"
        return f"{SUITES_ROUTE}/{self.suite.id}/edit"

    def get_suite_detail(self):
        """Load a single suite by its route ID."""
        with rx.session() as session:
            if (self.suite_id == ""):
                self.suite = None
                return
            result = session.exec(SuiteModel.select().where(SuiteModel.id == self.suite_id)).one_or_none()
            self.suite = result

    def load_suites(self):
        """Load all suites from the database."""
        with rx.session() as session:
            results = session.exec(SuiteModel.select()).all()
            self.suites = results

    def toggle_sort(self, field: str):
        """Cycle sort: default → asc → desc → default."""
        self.sort_by, self.sort_asc = toggle_sort_field(self.sort_by, self.sort_asc, field)

    @rx.var(cache=True)
    def sorted_suites(self) -> List['SuiteModel']:
        """Return suites sorted by the current sort field and direction."""
        return sort_items(self.suites, self.sort_by, self.sort_asc)

    def toggle_search_sort(self, field: str):
        """Cycle search sort: default → asc → desc → default."""
        self.search_sort_by, self.search_sort_asc = toggle_sort_field(self.search_sort_by, self.search_sort_asc, field)

    @rx.var(cache=True)
    def sorted_cases_for_search(self) -> List['CaseModel']:
        """Return search cases sorted by the current search sort field."""
        return sort_items(self.cases_for_search, self.search_sort_by, self.search_sort_asc)

    @rx.var(cache=True)
    def sorted_scenarios_for_search(self) -> List['ScenarioModel']:
        """Return search scenarios sorted by the current search sort field."""
        return sort_items(self.scenarios_for_search, self.search_sort_by, self.search_sort_asc)

    def add_suite(self, form_data:dict):
        """Create a new suite from form data."""
        if form_data["name"] == "": return None
        with rx.session() as session:
            suite = SuiteModel(**form_data)
            session.add(suite)
            session.commit()
            session.refresh(suite)
            self.suite = suite

            return consts.RETURN_VALUE
    
    def save_suite_edits(self, suite_id:int, updated_data:dict):
        """Persist edits to an existing suite."""
        if updated_data["name"] == "": return None
        with rx.session() as session:        
            suite = session.exec(SuiteModel.select().where(SuiteModel.id == suite_id)).one_or_none()

            if (suite is None):
                return
            for key, value in updated_data.items():
                setattr(suite, key, value)

            session.add(suite)
            session.commit()
            session.refresh(suite)
            self.suite = suite

            return consts.RETURN_VALUE

    def to_suite(self, edit_page=True):
        """Redirect to the suite detail or edit page."""
        if not self.suite:
            return rx.redirect(routes.SUITES)
        if edit_page:
            return rx.redirect(self.suite_edit_url)
        return rx.redirect(self.suite_url)
    
    def collapse_searches(self):
        """Hide all child search panels."""
        self.show_case_search = False
        self.show_scenario_search = False

    def toggle_case_search(self):
        """Toggle the case search panel visibility."""
        self.show_case_search = not(self.show_case_search)
        self.search_sort_by = ""
        self.search_sort_asc = True

    def load_children(self):
        """Load all children (scenarios, cases) for the current suite."""
        with rx.session() as session:
            results = session.exec(SuiteChildModel.select().where(SuiteChildModel.suite_id == self.suite_id).order_by(SuiteChildModel.order)).all()
            if (len(results) > 0):
                for single_result in results:
                    child = None
                    if (single_result.child_type_id == consts.SUITE_CHILD_TYPE_SCENARIO):
                        child = session.exec(ScenarioModel.select().where(ScenarioModel.id == single_result.child_id)).first()
                    elif (single_result.child_type_id == consts.SUITE_CHILD_TYPE_CASE):
                        child = session.exec(CaseModel.select().where(CaseModel.id == single_result.child_id)).first()
                    setattr(single_result, "child_name", child.name if child else "unknown")
            self.children = results
            self.child_count = len(results)

    def unlink_child(self, suite_child_id:int):
        """Remove a child from this suite and reorder siblings."""
        toast = reorder_delete(SuiteChildModel, suite_child_id, "suite_id", self.suite_id, "child")
        self.load_children()
        return toast

    def move_child_up(self, child_id:int):
        """Move a suite child one position up."""
        toast = reorder_move_up(SuiteChildModel, child_id, "suite_id", self.suite_id, "child")
        if toast is None:
            self.load_children()
        return toast

    def move_child_down(self, child_id:int):
        """Move a suite child one position down."""
        toast = reorder_move_down(SuiteChildModel, child_id, "suite_id", self.suite_id, "child")
        if toast is None:
            self.load_children()
        return toast
    
    def get_max_child_order(self, child_id:int, child_type_id:int):
        """Return the next order value for a new suite child."""
        return _get_max_child_order(SuiteChildModel, "suite_id", self.suite_id, child_id, child_type_id)

    def filter_test_cases(self, search_case_value):
        """Update the case search filter and reload results."""
        self.search_case_value = search_case_value
        self.load_cases_for_search()

    def load_cases_for_search(self):
        """Load cases matching the current search filter."""
        self.cases_for_search = search_by_name(CaseModel, self.search_case_value)

    def link_case(self, case_id:int):
        """Link a test case to the current suite."""
        if not self.has_steps(case_id): return rx.toast.error("test case must have at least one step")

        suite_case_data:dict = {"suite_id":""}
        new_case_order = 1

        if (len(self.cases_for_search) > 0):
            new_case_order = self.get_max_child_order(case_id, 2)

            if new_case_order == -1:
                return rx.toast.error(consts.MESSAGE_ALREADY_IN_LIST)

        suite_case_data.update({"suite_id":self.suite_id})
        suite_case_data.update({"child_type_id":consts.SUITE_CHILD_TYPE_CASE})
        suite_case_data.update({"child_id":case_id})
        suite_case_data.update({"order":new_case_order})

        with rx.session() as session:
            case_to_add = SuiteChildModel(**suite_case_data)
            session.add(case_to_add)
            session.commit()
            session.refresh(case_to_add)
        self.search_case_value = ""
        self.collapse_searches()
        self.load_children()
        
        return rx.toast.success("case added!")
    
    def has_steps(self, case_id:int) -> bool:
        """Check whether the given case contains any steps."""
        return _has_steps(StepModel, case_id)

    def toggle_scenario_search(self):
        """Toggle the scenario search panel visibility."""
        self.show_scenario_search = not(self.show_scenario_search)
        self.search_sort_by = ""
        self.search_sort_asc = True

    def filter_scenarios(self, search_scenario_value):
        """Update the scenario search filter and reload results."""
        self.search_scenario_value = search_scenario_value
        self.load_scenarios_for_search()

    def load_scenarios_for_search(self):
        """Load scenarios matching the current search filter."""
        self.scenarios_for_search = search_by_name(ScenarioModel, self.search_scenario_value)

    def link_scenario(self, scenario_id:int):
        """Link a scenario to the current suite."""
        suite_scenario_data:dict = {"suite_id":""}
        new_scenario_order = 1

        if (len(self.scenarios_for_search) > 0):
            new_scenario_order = self.get_max_child_order(scenario_id, 1)

            if new_scenario_order == -1:
                return rx.toast.error(consts.MESSAGE_ALREADY_IN_LIST)

        suite_scenario_data.update({"suite_id":self.suite_id})
        suite_scenario_data.update({"child_type_id":consts.SUITE_CHILD_TYPE_SCENARIO})
        suite_scenario_data.update({"child_id":scenario_id})
        suite_scenario_data.update({"order":new_scenario_order})

        with rx.session() as session:
            scenario_to_add = SuiteChildModel(**suite_scenario_data)
            session.add(scenario_to_add)
            session.commit()
            session.refresh(scenario_to_add)
        self.search_scenario_value = ""
        self.collapse_searches()
        self.load_children()
        
        return rx.toast.success("scenario added!")
    
class AddSuiteState(SuiteState):
    """Handles the add-suite form submission."""

    form_data:dict = {}

    def handle_submit(self, form_data):
        """Validate and create a new suite from the form."""
        self.form_data = form_data
        result = self.add_suite(form_data)
        
        if result is None: return rx.toast.error("name cannot be empty")
        return rx.redirect(routes.SUITES)

class EditSuiteState(SuiteState):
    """Handles the edit-suite form submission."""

    form_data:dict = {}

    def handle_submit(self, form_data):
        """Validate and save suite edits from the form."""
        self.form_data = form_data
        try:
            suite_id = form_data.pop("suite_id")
        except KeyError:
            return rx.toast.error("Invalid suite ID")
        updated_data = {**form_data}
        result = self.save_suite_edits(suite_id, updated_data)

        if result is None: return rx.toast.error("name cannot be empty")
        return rx.redirect(routes.SUITES)