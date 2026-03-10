"""Test cycle state management, iteration snapshots, and event handlers."""

from typing import List, Optional
from datetime import datetime, timezone
import reflex as rx
from rxconfig import config
from .model import CycleModel, CycleChildModel
from ..navigation import routes

from ..case.model import CaseModel, StepModel, PrerequisiteModel
from ..scenario.model import ScenarioModel, ScenarioCaseModel
from ..suite.model import SuiteModel, SuiteChildModel
from ..iteration.model import IterationModel, IterationStatusModel, IterationSnapshotModel, IterationSnapshotLinkedIssues

from sqlmodel import select, asc, desc

from ..utils import jira, consts
from ..utils.mixins import reorder_move_up, reorder_move_down, reorder_delete, has_steps as _has_steps, get_max_child_order as _get_max_child_order, toggle_sort_field, sort_items, search_by_name, toggle_search_panel

CYCLES_ROUTE = consts.normalize_route(routes.CYCLES)

def format_iteration_status(status: 'IterationStatusModel', can_edit: bool) -> str:
    """Return the display name for an iteration status, prefixed with [F] when completed with failures."""
    if status is None:
        return ""
    if (status.id == consts.ITERATION_STATUS_COMPLETED) and can_edit:
        return "[F] " + status.name
    return status.name

SITE_URL = f"http://localhost:{config.frontend_port}/"
class CycleState(rx.State):
    """Manages cycle CRUD, child linking, iteration snapshots, and execution."""

    cycles: List['CycleModel'] = []
    cycle: Optional['CycleModel'] = None

    sort_by: str = ""
    sort_asc: bool = True

    search_sort_by: str = ""
    search_sort_asc: bool = True

    @rx.var(cache=True)
    def cycle_id(self) -> str:
        return self.router._page.params.get(consts.FIELD_ID, "")

    @rx.var(cache=True)
    def cycle_url(self) -> str:
        if not self.cycle:
            return f"{CYCLES_ROUTE}"
        return f"{CYCLES_ROUTE}/{self.cycle.id}"
    
    @rx.var(cache=True)
    def cycle_edit_url(self) -> str:
        if not self.cycle:
            return f"{CYCLES_ROUTE}"
        return f"{CYCLES_ROUTE}/{self.cycle.id}/edit"
    
    @rx.var(cache=True)
    def cycle_threshold(self) -> str:
        if not self.cycle:
            return "0"
        return f"{self.cycle.threshold}"
    
    @rx.var(cache=True)
    def cycle_name(self) -> str:
        if not self.cycle:
            return ""
        return f"{self.cycle.name}"

    def get_cycle_detail(self):
        """Load a single cycle by its route ID."""
        with rx.session() as session:
            if (self.cycle_id == ""):
                self.cycle = None
                return
            result = session.exec(CycleModel.select().where(CycleModel.id == self.cycle_id)).one_or_none()
            self.cycle = result

    #region CYCLES
    def load_cycles(self):
        """Load all cycles with their iteration status and pass/fail metrics."""
        with rx.session() as session:
            results = session.exec(CycleModel.select().order_by(desc(CycleModel.created))).all()

            for single_result in results:
                iteration_status_name = ""
                iteration_finished = False
                iteration_in_progress = False

                cycle_iteration = session.exec(IterationModel.select().where(IterationModel.cycle_id == single_result.id)).one_or_none()
                if (cycle_iteration != None):
                    iteration_execution_status = session.exec(IterationStatusModel.select().where(IterationStatusModel.id == cycle_iteration.iteration_status_id)).first()
                    iteration_status_name = format_iteration_status(iteration_execution_status, self.can_edit_iteration(single_result.id))

                    if (iteration_execution_status != None):
                        iteration_finished = ((iteration_execution_status.id == consts.ITERATION_STATUS_CLOSED) or (iteration_execution_status.id == consts.ITERATION_STATUS_COMPLETED))

                        if (iteration_finished == False):
                            iteration_in_progress = ((iteration_execution_status.id == consts.ITERATION_STATUS_IN_PROGRESS) or (iteration_execution_status.id == consts.ITERATION_STATUS_ON_HOLD))

                    if ((iteration_finished == True) or (iteration_in_progress == True)):
                        all_steps_count = 0
                        failed_steps_count = 0
                        passed_steps_count = 0
                        snapshot_all_steps = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.iteration_id == cycle_iteration.id, IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP)).all()

                        if snapshot_all_steps != None:
                            all_steps_count = len(snapshot_all_steps)
                            snapshot_failed_steps = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.iteration_id == cycle_iteration.id, IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP, IterationSnapshotModel.child_status_id == consts.SNAPSHOT_STATUS_FAILED)).all()

                            if snapshot_failed_steps != None and all_steps_count > 0:
                                failed_steps_count = len(snapshot_failed_steps)

                                iteration_failed_percentage = int((failed_steps_count*100)/all_steps_count)

                            else:
                                iteration_failed_percentage = 0

                            snapshot_passed_steps = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.iteration_id == cycle_iteration.id, IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP, IterationSnapshotModel.child_status_id == consts.SNAPSHOT_STATUS_PASS)).all()
                            if snapshot_passed_steps != None and all_steps_count > 0:
                                passed_steps_count = len(snapshot_passed_steps)

                                iteration_passed_percentage = int((passed_steps_count*100)/all_steps_count)
                            else:
                                iteration_passed_percentage = 0
                        else:
                            iteration_failed_percentage = 0
                            iteration_passed_percentage = 0

                        snapshot_threshold = f"{single_result.threshold}/{iteration_passed_percentage}/{iteration_failed_percentage}"

                        if (iteration_finished == True):
                            cycle_status = ""
                            try:
                                threshold_value = int(single_result.threshold)
                            except (TypeError, ValueError):
                                threshold_value = 0
                            if (iteration_passed_percentage >= threshold_value):
                                cycle_status = consts.STATUS_CYCLE_PASSED
                            else:
                                cycle_status = consts.STATUS_CYCLE_FAILED
                            setattr(single_result, "cycle_status_name", cycle_status)
                        else: #iteration is in progress
                            setattr(single_result, "cycle_status_name", "testing")

                        setattr(single_result, "threshold", snapshot_threshold)

                setattr(single_result, "iteration_status_name", iteration_status_name)

            self.cycles = results

    def toggle_sort(self, field: str):
        """Cycle sort: default → asc → desc → default."""
        self.sort_by, self.sort_asc = toggle_sort_field(self.sort_by, self.sort_asc, field)

    @rx.var(cache=True)
    def sorted_cycles(self) -> List['CycleModel']:
        """Return cycles sorted by the current sort field and direction."""
        return sort_items(self.cycles, self.sort_by, self.sort_asc)

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

    @rx.var(cache=True)
    def sorted_suites_for_search(self) -> List['SuiteModel']:
        """Return search suites sorted by the current search sort field."""
        return sort_items(self.suites_for_search, self.search_sort_by, self.search_sort_asc)

    def add_cycle(self, form_data:dict):
        """Create a new cycle from form data."""
        if form_data["name"] == "": return None
        if form_data["threshold"] == "": return None
        with rx.session() as session:
            cycle = CycleModel(**form_data)
            session.add(cycle)
            session.commit()
            session.refresh(cycle)
            self.cycle = cycle

            return consts.RETURN_VALUE
    
    def save_cycle_edits(self, cycle_id:int, updated_data:dict):
        """Persist edits to an existing cycle."""
        if updated_data["name"] == "": return None
        if updated_data["threshold"] == "": return None
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

            return consts.RETURN_VALUE
    
    def collapse_searches(self):
        """Hide all child search panels."""
        self.show_case_search = False
        self.show_scenario_search = False
        self.show_suite_search = False

    def can_edit_iteration(self, cycle_id:int) -> bool:
        """Return True if the cycle's iteration is still editable."""
        with rx.session() as session:
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == cycle_id)).one_or_none()

            if (iteration != None):
                if (iteration.iteration_status_id == consts.ITERATION_STATUS_CLOSED): return False

                if (iteration.iteration_status_id == consts.ITERATION_STATUS_COMPLETED):
                    all_steps = session.exec(select(IterationSnapshotModel).where(IterationSnapshotModel.iteration_id == iteration.id, IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP)).all()
                    passed_steps = session.exec(select(IterationSnapshotModel).where(IterationSnapshotModel.iteration_id == iteration.id, IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP, IterationSnapshotModel.child_status_id == consts.SNAPSHOT_STATUS_PASS)).all()

                    if (all_steps != None) and (passed_steps != None):
                        if (len(all_steps) == len(passed_steps)): return False

                return True
            else:
                return False

    def duplicate_cycle(self, origin_cycle_id:int):
        """Create a copy of a cycle including all its children."""
        with rx.session() as session:
            origin_cycle = session.exec(CycleModel.select().where(CycleModel.id == origin_cycle_id)).one_or_none()
            if origin_cycle is None: return

            new_cycle:dict = {"name": "copy of " + origin_cycle.name, "threshold": origin_cycle.threshold}
            cycle_to_add = CycleModel(**new_cycle)
            session.add(cycle_to_add)
            session.commit()
            session.refresh(cycle_to_add)

            self.cycle = cycle_to_add

            self.duplicate_cycle_children(origin_cycle_id, self.cycle.id)
            self.load_cycles()
    #endregion

    #region CYCLE CHILDREN
    children: List['CycleChildModel'] = []
    child: Optional['CycleChildModel'] = None
    child_count: int = 0

    def load_children(self):
        """Load all children (suites, scenarios, cases) for the current cycle."""
        with rx.session() as session:
            results = session.exec(CycleChildModel.select().where(CycleChildModel.cycle_id == self.cycle_id).order_by(CycleChildModel.order)).all()
            if (len(results) > 0):
                for single_result in results:
                    child = None
                    if (single_result.child_type_id == consts.CHILD_TYPE_SUITE):
                        child = session.exec(SuiteModel.select().where(SuiteModel.id == single_result.child_id)).first()
                    elif (single_result.child_type_id == consts.CHILD_TYPE_SCENARIO):
                        child = session.exec(ScenarioModel.select().where(ScenarioModel.id == single_result.child_id)).first()
                    elif (single_result.child_type_id == consts.CHILD_TYPE_CASE):
                        child = session.exec(CaseModel.select().where(CaseModel.id == single_result.child_id)).first()
                    setattr(single_result, "child_name", child.name if child else "unknown")
            self.children = results
            self.child_count = len(results)

    def unlink_child(self, child_id:int):
        """Remove a child from this cycle and reorder siblings."""
        toast = reorder_delete(CycleChildModel, child_id, "cycle_id", self.cycle_id, "child")
        self.load_children()
        return toast

    def move_child_up(self, child_id:int):
        """Move a cycle child one position up."""
        toast = reorder_move_up(CycleChildModel, child_id, "cycle_id", self.cycle_id, "child")
        if toast is None:
            self.load_children()
        return toast

    def move_child_down(self, child_id:int):
        """Move a cycle child one position down."""
        toast = reorder_move_down(CycleChildModel, child_id, "cycle_id", self.cycle_id, "child")
        if toast is None:
            self.load_children()
        return toast
    
    def get_max_child_order(self, child_id:int, child_type_id:int):
        """Return the next order value for a new cycle child."""
        return _get_max_child_order(CycleChildModel, "cycle_id", self.cycle_id, child_id, child_type_id)

    def duplicate_cycle_children(self, origin_cycle_id:int, target_cycle_id:int):
        """Copy all children from one cycle to another."""
        with rx.session() as session:
            linked_children = session.exec(CycleChildModel.select().where(CycleChildModel.cycle_id == origin_cycle_id)).all()

            for linked_child in linked_children:
                new_child:dict = {"cycle_id": target_cycle_id, "child_type_id": linked_child.child_type_id, "child_id": linked_child.child_id, "order": linked_child.order}

                child_to_add = CycleChildModel(**new_child)
                session.add(child_to_add)
                session.commit()
                session.refresh(child_to_add)
    #endregion

    #region CASES
    show_case_search:bool = False
    search_case_value:str = ""
    cases_for_search: List['CaseModel'] = []

    def toggle_case_search(self):
        """Toggle the case search panel visibility."""
        self.show_case_search, self.search_sort_by, self.search_sort_asc = toggle_search_panel(self.show_case_search)

    def filter_test_cases(self, search_case_value):
        """Update the case search filter and reload results."""
        self.search_case_value = search_case_value
        self.load_cases_for_search()

    def load_cases_for_search(self):
        """Load cases matching the current search filter."""
        self.cases_for_search = search_by_name(CaseModel, self.search_case_value)

    def link_case(self, case_id:int):
        """Link a test case to the current cycle."""
        if not self.has_steps(case_id): return rx.toast.error("test case must have at least one step")
        
        cycle_case_data:dict = {"cycle_id":""}
        new_case_order = 1

        if (len(self.cases_for_search) > 0):
            new_case_order = self.get_max_child_order(case_id, consts.CHILD_TYPE_CASE)

            if new_case_order == -1:
                return rx.toast.error(consts.MESSAGE_ALREADY_IN_LIST)

        cycle_case_data.update({"cycle_id":self.cycle_id})
        cycle_case_data.update({"child_type_id":consts.CHILD_TYPE_CASE})
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
    
    def has_steps(self, case_id:int) -> bool:
        """Check whether the case has steps before linking to the cycle."""
        return _has_steps(StepModel, case_id)
    #endregion

    #region SCENARIOS
    show_scenario_search:bool = False
    search_scenario_value:str = ""
    scenarios_for_search: List['ScenarioModel'] = []

    def toggle_scenario_search(self):
        """Toggle the scenario search panel visibility."""
        self.show_scenario_search, self.search_sort_by, self.search_sort_asc = toggle_search_panel(self.show_scenario_search)

    def filter_scenarios(self, search_scenario_value):
        """Update the scenario search filter and reload results."""
        self.search_scenario_value = search_scenario_value
        self.load_scenarios_for_search()

    def load_scenarios_for_search(self):
        """Load scenarios matching the current search filter."""
        self.scenarios_for_search = search_by_name(ScenarioModel, self.search_scenario_value)

    def link_scenario(self, scenario_id:int):
        """Link a scenario to the current cycle."""
        cycle_scenario_data:dict = {"cycle_id":""}
        new_scenario_order = 1

        if (len(self.scenarios_for_search) > 0):
            new_scenario_order = self.get_max_child_order(scenario_id, consts.CHILD_TYPE_SCENARIO)

            if new_scenario_order == -1:
                return rx.toast.error(consts.MESSAGE_ALREADY_IN_LIST)

        cycle_scenario_data.update({"cycle_id":self.cycle_id})
        cycle_scenario_data.update({"child_type_id":consts.CHILD_TYPE_SCENARIO})
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
    #endregion

    #region SUITES
    show_suite_search:bool = False
    search_suite_value:str = ""
    suites_for_search: List['SuiteModel'] = []

    def toggle_suite_search(self):
        """Toggle the suite search panel visibility."""
        self.show_suite_search, self.search_sort_by, self.search_sort_asc = toggle_search_panel(self.show_suite_search)

    def filter_suites(self, search_suite_value):
        """Update the suite search filter and reload results."""
        self.search_suite_value = search_suite_value
        self.load_suites_for_search()

    def load_suites_for_search(self):
        """Load suites matching the current search filter."""
        self.suites_for_search = search_by_name(SuiteModel, self.search_suite_value)

    def link_suite(self, suite_id:int):
        """Link a suite to the current cycle."""
        cycle_suite_data:dict = {"cycle_id":""}
        new_suite_order = 1

        if (len(self.suites_for_search) > 0):
            new_suite_order = self.get_max_child_order(suite_id, consts.CHILD_TYPE_SUITE)

            if new_suite_order == -1:
                return rx.toast.error(consts.MESSAGE_ALREADY_IN_LIST)

        cycle_suite_data.update({"cycle_id":self.cycle_id})
        cycle_suite_data.update({"child_type_id":consts.CHILD_TYPE_SUITE})
        cycle_suite_data.update({"child_id":suite_id})
        cycle_suite_data.update({"order":new_suite_order})

        with rx.session() as session:
            suite_to_add = CycleChildModel(**cycle_suite_data)
            session.add(suite_to_add)
            session.commit()
            session.refresh(suite_to_add)
        self.search_suite_value = ""
        self.collapse_searches()
        self.load_children()
        
        return rx.toast.success("suite added!")
    #endregion

    #region SNAPSHOT
    iteration_snapshot_items: List['IterationSnapshotModel'] = []

    @rx.var(cache=True)
    def iteration_status_name(self) -> str:
        if not self.cycle:
            return ""
        with rx.session() as session:
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == self.cycle_id)).one_or_none()
            if (iteration != None):
                status = session.exec(select(IterationStatusModel).where(IterationStatusModel.id == iteration.iteration_status_id)).first()
                return format_iteration_status(status, self.can_edit_iteration(self.cycle.id))
            else:
                return ""

    @rx.var(cache=True)
    def has_iteration(self) -> bool:
        if not self.cycle:
            return False
        with rx.session() as session:
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == self.cycle_id)).one_or_none()
            return (iteration != None)
        
    @rx.var(cache=True)
    def iteration_url(self) -> str:
        if not self.cycle:
            return f"{CYCLES_ROUTE}"
        return f"{CYCLES_ROUTE}/{self.cycle.id}/iteration"
    
    @rx.var(cache=True)
    def is_iteration_editable(self) -> bool:
        if not self.cycle:
            return False
        return self.can_edit_iteration(self.cycle_id)

    def __update_iteration_snapshot_step(self, snapshot_item_id:int, status_id:int, set_updated = False, clear_updated = False):
        with rx.session() as session:
            iteration_snapshot = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.id == snapshot_item_id)).one_or_none()

            if (iteration_snapshot is None): return

            setattr(iteration_snapshot, "child_status_id", status_id)
            if (set_updated == True): setattr(iteration_snapshot, "updated", datetime.now(timezone.utc))
            if (clear_updated == True): setattr(iteration_snapshot, "updated", None)

            session.add(iteration_snapshot)
            session.commit()
            session.refresh(iteration_snapshot)
            self.__figure_and_update_iteration_execution_status(iteration_snapshot.iteration_id)
            self.get_iteration_snapshot()
    
    def add_iteration_snapshot(self, cycle_id:int):
        """Create a new iteration snapshot from the cycle's children."""
        with rx.session() as session:
            children = session.exec(CycleChildModel.select().where(CycleChildModel.cycle_id == cycle_id).order_by(CycleChildModel.order)).all()
            if (len(children) > 0):
                #add the cycle - iteration relationship
                cycle_iteration_data:dict = {"cycle_id":cycle_id}

                cycle_iteration_data.update({"iteration_status_id":consts.ITERATION_STATUS_NOT_STARTED})
                cycle_iteration_data.update({"iteration_number":1})

                iteration_to_add = IterationModel(**cycle_iteration_data)
                session.add(iteration_to_add)
                session.commit()
                session.refresh(iteration_to_add)

                #add the cycle's snapshot here
                for cycle_child in children:
                    match cycle_child.child_type_id:
                        case consts.CHILD_TYPE_SUITE:
                            self.add_suite_to_snapshot(iteration_to_add.id, cycle_child.child_id)
                        case consts.CHILD_TYPE_SCENARIO:
                            self.add_scenario_to_snapshot(iteration_to_add.id, cycle_child.child_id)
                        case consts.CHILD_TYPE_CASE:
                            self.add_case_to_snapshot(iteration_to_add.id, cycle_child.child_id)

                self.load_cycles()
                return self.view_iteration_snapshot(cycle_id)

    def view_iteration_snapshot(self, cycle_id:int) -> rx.Component:
        """Redirect to the iteration snapshot page for the given cycle."""
        with rx.session() as session:
            result = session.exec(CycleModel.select().where(CycleModel.id == cycle_id)).one_or_none()
            self.cycle = result
        return rx.redirect(self.iteration_url)
    
    def get_iteration_snapshot(self):
        """Load the iteration snapshot items for the current cycle."""
        with rx.session() as session:
            if (self.cycle_id == ""):
                self.cycle = None
                return
            self.cycle = session.exec(CycleModel.select().where(CycleModel.id == self.cycle_id)).one_or_none()
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == self.cycle_id)).one_or_none()
            if iteration is None:
                self.iteration_snapshot_items = []
                return
            self.iteration_snapshot_items = session.exec(select(IterationSnapshotModel).where(IterationSnapshotModel.iteration_id == iteration.id).order_by(asc(IterationSnapshotModel.order))).all()

            #get all snapshot elements that have a linked issue
            for snapshot_item in self.iteration_snapshot_items:
                linked_issues = session.exec(select(IterationSnapshotLinkedIssues).where(IterationSnapshotLinkedIssues.iteration_snapshot_id == snapshot_item.id).where(IterationSnapshotLinkedIssues.unlinked == None)).one_or_none()

                if linked_issues is not None:
                    setattr(snapshot_item, "linked_issue", linked_issues.issue_key)

    def fail_iteration_snapshot_step(self, snapshot_item_id:int):
        """Mark a snapshot step as failed and block subsequent steps."""
        self.__update_iteration_snapshot_step(snapshot_item_id, consts.SNAPSHOT_STATUS_FAILED, True)

        #block the remainning steps on the case
        with rx.session() as session:
            iteration_snapshot = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.id == snapshot_item_id)).one_or_none()

            next_steps:IterationSnapshotModel = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.order > iteration_snapshot.order, IterationSnapshotModel.iteration_id == iteration_snapshot.iteration_id).order_by(asc(IterationSnapshotModel.order))).all() 
            if (next_steps != None):
                for next_step in next_steps:
                    if next_step.child_name == None:
                        self.__update_iteration_snapshot_step(next_step.id, consts.SNAPSHOT_STATUS_BLOCKED, set_updated=True)
                    else:
                        break

    def fail_iteration_snapshot_step_and_create_issue(self, form_data: dict):
        """Fail a snapshot step and create a linked Jira issue."""
        try:
            snapshot_item_id:int = form_data.pop("snapshot_item_id")
        except KeyError:
            return rx.toast.error("Invalid snapshot item ID")

        self.fail_iteration_snapshot_step(snapshot_item_id)

        if (self.__fail_checkbox == False):
            with rx.session() as session:
                iteration_snapshot = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.id == snapshot_item_id)).one_or_none()        

                previous_steps:IterationSnapshotModel = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.order < iteration_snapshot.order, IterationSnapshotModel.iteration_id == iteration_snapshot.iteration_id).order_by(desc(IterationSnapshotModel.order))).all() 
                if (previous_steps != None):
                    #work summary & description to send to the issue creation
                    issue_summary:str = form_data.pop("summary")
                    actual_result:str = form_data.pop("actual")
                    expected_result:str = form_data.pop("expected")
                    step_count = 0
                    
                    issue_description = ""
                    
                    for prev_step in previous_steps:
                        if prev_step.child_name != None: 
                            issue_summary = f"[{str(prev_step.child_name).replace('[P] ', '')}]: {issue_summary}"
                            break

                        step_count = step_count + 1
                        issue_description = f"{issue_description}{step_count}. {prev_step.child_action}"

                        if (prev_step.child_expected != ""):
                            issue_description = f"{issue_description} --> {prev_step.child_expected}"

                        issue_description = f"{issue_description}\n"

                    if actual_result != "":
                        actual_result = f"\nActual Result: {actual_result}"

                    if expected_result != "":
                        expected_result = f"\nExpected Result: {expected_result}"

                    issue_description = f"{issue_description}{expected_result}{actual_result}\n\nsource: {SITE_URL}{self.iteration_url}"

            #create ticket here
            self.turn_on_fail_checkbox()
            try:
                new_issue = jira.create_issue(issue_summary, issue_description)
                self.link_issue_to_snapshot_step(snapshot_item_id, new_issue)
                self.get_iteration_snapshot()
                return rx.toast.success(f"new issue created: {new_issue}")
            except Exception:
                return rx.toast.error("error creating the issue, please contact the administrator")
            
    def unlink_issue_from_snapshot_step(self, snapshot_item_id:int):
        """Unlink a Jira issue from a snapshot step."""
        with rx.session() as session:
            linked_issue = session.exec(IterationSnapshotLinkedIssues.select().where(IterationSnapshotLinkedIssues.iteration_snapshot_id == snapshot_item_id)).one_or_none()
            if (linked_issue != None):
                setattr(linked_issue, "unlinked", True)
                session.add(linked_issue)
                session.commit()
                session.refresh(linked_issue)
                self.get_iteration_snapshot()
                return rx.toast.info("issue unlinked")
        
    def link_issue_to_snapshot_step(self, snapshot_item_id:int, issue_key:str):
        """Link a Jira issue key to a snapshot step."""
        linked_issue:dict = {"iteration_snapshot_id": f"{snapshot_item_id}", "issue_key": issue_key}
        with rx.session() as session:
            issue_to_add = IterationSnapshotLinkedIssues(**linked_issue)
            session.add(issue_to_add)
            session.commit()
    
    def pass_iteration_snapshot_step(self, snapshot_item_id:int):
        """Mark a snapshot step as passed and unblock subsequent steps."""
        self.__update_iteration_snapshot_step(snapshot_item_id, consts.SNAPSHOT_STATUS_PASS, True)

        #if steps where blocked, restore the "To Do" status for the remainning steps on the case
        with rx.session() as session:
            iteration_snapshot = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.id == snapshot_item_id)).one_or_none()
            next_steps:IterationSnapshotModel = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.order > iteration_snapshot.order, IterationSnapshotModel.iteration_id == iteration_snapshot.iteration_id).order_by(asc(IterationSnapshotModel.order))).all() 

            if (next_steps != None):
                for next_step in next_steps:
                    if next_step.child_name == None:
                        self.__update_iteration_snapshot_step(next_step.id, consts.SNAPSHOT_STATUS_TO_DO, clear_updated=True)
                    else:
                        break

    def skip_iteration_snapshot_step(self, snapshot_item_id:int):
        """Mark a snapshot step as skipped and unblock subsequent steps."""
        self.__update_iteration_snapshot_step(snapshot_item_id, consts.SNAPSHOT_STATUS_SKIPPED, True)

        #if steps where blocked, restore the "To Do" status for the remainning steps on the case
        with rx.session() as session:
            iteration_snapshot = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.id == snapshot_item_id)).one_or_none()
            next_steps:IterationSnapshotModel = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.order > iteration_snapshot.order, IterationSnapshotModel.iteration_id == iteration_snapshot.iteration_id).order_by(asc(IterationSnapshotModel.order))).all() 

            if (next_steps != None):
                for next_step in next_steps:
                    if next_step.child_name == None:
                        self.__update_iteration_snapshot_step(next_step.id, consts.SNAPSHOT_STATUS_TO_DO, clear_updated=True)
                    else:
                        break

    def get_max_iteration_snapshot_order(self, iteration_id:int):
        """Return the next available order value for a snapshot item."""
        with rx.session() as session:
            snapshot_item = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.iteration_id == iteration_id).order_by(desc(IterationSnapshotModel.order))).first()

            max_order = 0
            if (snapshot_item != None):
                max_order = snapshot_item.order + 1

            return max_order
        
    #validate that the case is not yet added to the snapshot
    def is_case_in_snapshot(self, iteration_id:int, case_id:int) -> bool:
        """Return True if the case is already present in the snapshot."""
        with rx.session() as session:
            snapshot_case = session.exec(IterationSnapshotModel.select().where(
                IterationSnapshotModel.iteration_id == iteration_id,
                IterationSnapshotModel.child_id == case_id,
                IterationSnapshotModel.child_type == consts.CHILD_TYPE_CASE
            )).first()

            return (snapshot_case != None)

    def add_case_to_snapshot(self, iteration_id:int, case_id:int, is_prerequisite:bool = False):
        """Add a case and its steps to the iteration snapshot."""
        already_added = self.is_case_in_snapshot(iteration_id, case_id)

        if (already_added == False):
            with rx.session() as session:
                child_case = session.exec(CaseModel.select().where(CaseModel.id == case_id)).first()

                if (child_case != None):
                    if (is_prerequisite == False):
                        child_name = child_case.name
                    else:
                        child_name = f"[P] {child_case.name}"

                    #cycle through prerequisites and insert them
                    prerequisites = session.exec(PrerequisiteModel.select().where(PrerequisiteModel.case_id == case_id).order_by(PrerequisiteModel.order)).all()
                    
                    for prerequisite in prerequisites:
                        self.add_case_to_snapshot(iteration_id, prerequisite.prerequisite_id, True)

                    max_order = self.get_max_iteration_snapshot_order(iteration_id)

                    #insert the case
                    snapshot_case_data:dict = {
                        "iteration_id":iteration_id,
                        "order":max_order,
                        "child_type":consts.CHILD_TYPE_CASE,
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
                            "child_type":consts.CHILD_TYPE_STEP,
                            "child_action": step.action,
                            "child_expected": step.expected,
                            "child_status_id":consts.SNAPSHOT_STATUS_TO_DO
                        }

                        step_to_add = IterationSnapshotModel(**snapshot_step_data)
                        session.add(step_to_add)
                        session.commit()

    def add_scenario_to_snapshot(self, iteration_id:int, scenario_id:int):
        """Add a scenario and its cases to the iteration snapshot."""
        with rx.session() as session:
            child_scenario = session.exec(ScenarioModel.select().where(ScenarioModel.id == scenario_id)).first()

            if (child_scenario != None):
                max_order = self.get_max_iteration_snapshot_order(iteration_id)

                #insert the case
                snapshot_scenario_data:dict = {
                    "iteration_id":iteration_id,
                    "order":max_order,
                    "child_type":consts.CHILD_TYPE_SCENARIO,
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
        """Add a suite and its children to the iteration snapshot."""
        with rx.session() as session:
            child_suite = session.exec(SuiteModel.select().where(SuiteModel.id == suite_id)).first()

            if (child_suite != None):
                max_order = self.get_max_iteration_snapshot_order(iteration_id)

                #insert the case
                snapshot_suite_data:dict = {
                    "iteration_id":iteration_id,
                    "order":max_order,
                    "child_type":consts.CHILD_TYPE_SUITE,
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
                        case consts.SUITE_CHILD_TYPE_SCENARIO:
                            self.add_scenario_to_snapshot(iteration_id, suite_child.child_id)
                        case consts.SUITE_CHILD_TYPE_CASE:
                            self.add_case_to_snapshot(iteration_id, suite_child.child_id)
    #endregion

    #region ITERATION
    @rx.var(cache=True)
    def iteration_id(self) -> int:
        if not self.cycle:
            return -1
        
        with rx.session() as session:
            iteration = session.exec(select(IterationModel).where(IterationModel.cycle_id == self.cycle.id)).one_or_none()
            if not iteration:
                return -1
            return iteration.id
        
    __fail_checkbox = False

    @rx.var(cache=True)
    def fail_checkbox(self) -> bool:
        return self.__fail_checkbox
    
    def __set_iteration_execution_status(self, iteration_id:int, iteration_status_id:int):
        with rx.session() as session:
            iteration = session.exec(select(IterationModel).where(IterationModel.id == iteration_id)).one_or_none()
            if iteration is None: return

            setattr(iteration, "iteration_status_id", iteration_status_id)

            session.add(iteration)
            session.commit()
            session.refresh(iteration)

    def __figure_and_update_iteration_execution_status(self, iteration_id:int):
        with rx.session() as session:
            iteration_not_attempted_steps = session.exec(select(IterationSnapshotModel).where(IterationSnapshotModel.iteration_id == iteration_id, IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP, IterationSnapshotModel.child_status_id == consts.SNAPSHOT_STATUS_TO_DO)).all()

            not_attempted_steps_count = len(iteration_not_attempted_steps)

            if (not_attempted_steps_count == 0):
                self.__set_iteration_execution_status(iteration_id, consts.ITERATION_STATUS_COMPLETED)
            else:
                iteration_in_progress_steps = session.exec(select(IterationSnapshotModel).where(IterationSnapshotModel.iteration_id == iteration_id, IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP, IterationSnapshotModel.child_status_id != consts.SNAPSHOT_STATUS_TO_DO)).all()
                if len(iteration_in_progress_steps) == 1:
                    self.__set_iteration_execution_status(iteration_id, consts.ITERATION_STATUS_IN_PROGRESS)
    
    def turn_on_fail_checkbox(self):
        """Enable the fail-with-issue checkbox."""
        self.__fail_checkbox = True

    def turn_off_fail_checkbox(self):
        """Disable the fail-with-issue checkbox."""
        self.__fail_checkbox = False

    def set_iteration_execution_status_on_hold(self, iteration_id:int):
        """Set the iteration status to on-hold."""
        self.__set_iteration_execution_status(iteration_id, consts.ITERATION_STATUS_ON_HOLD)

    def set_iteration_execution_status_closed(self, iteration_id:int):
        """Set the iteration status to closed."""
        self.__set_iteration_execution_status(iteration_id, consts.ITERATION_STATUS_CLOSED)

    #endregion

class AddCycleState(CycleState):
    """Handles the add-cycle form submission."""

    form_data:dict = {}

    def handle_submit(self, form_data):
        """Validate and create a new cycle from the form."""
        self.form_data = form_data
        result = self.add_cycle(form_data)
        if result is None:
            return rx.toast.error("name and threshold cannot be empty")
        return rx.redirect(routes.CYCLES)

class EditCycleState(CycleState):
    """Handles the edit-cycle form submission."""

    form_data:dict = {}

    def handle_submit(self, form_data):
        """Validate and save cycle edits from the form."""
        self.form_data = form_data
        try:
            cycle_id = form_data.pop("cycle_id")
        except KeyError:
            return rx.toast.error("Invalid cycle ID")
        updated_data = {**form_data}
        result = self.save_cycle_edits(cycle_id, updated_data)
        if result is None:
            return rx.toast.error("name and threshold cannot be empty")
        return rx.redirect(routes.CYCLES)