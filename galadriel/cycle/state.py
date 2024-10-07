from typing import List, Optional
import reflex as rx
from .model import CycleModel
from ..navigation import routes

# from ..case.model import CaseModel
# from ..scenario.model import ScenarioModel

from datetime import datetime

from sqlmodel import select, asc, or_, func, cast, String

CYCLES_ROUTE = routes.SUITES
if CYCLES_ROUTE.endswith("/"): CYCLES_ROUTE = CYCLES_ROUTE[:-1]

class CycleState(rx.State):
    cycles: List['CycleModel'] = []
    cycle: Optional['CycleModel'] = None

    # children: List['SuiteChildModel'] = []
    # child: Optional['SuiteChildModel'] = None

    # cases_for_search: List['CaseModel'] = []
    # show_case_search:bool = False
    # search_case_value:str = ""

    # scenarios_for_search: List['ScenarioModel'] = []
    # show_scenario_search:bool = False
    # search_scenario_value:str = ""

    @rx.var
    def cycle_id(self):
        #print(self.router.page.params)
        return self.router.page.params.get("id", "")
    
    @rx.var
    def suite_url(self):
        if not self.cycle:
            return f"{CYCLES_ROUTE}"
        return f"{CYCLES_ROUTE}/{self.cycle.id}"
    
    @rx.var
    def suite_edit_url(self):
        if not self.cycle:
            return f"{CYCLES_ROUTE}"
        return f"{CYCLES_ROUTE}/{self.cycle.id}/edit"

    # def get_suite_detail(self):
    #     with rx.session() as session:
    #         if (self.cycle_id == ""):
    #             self.cycle = None
    #             return
    #         result = session.exec(SuiteModel.select().where(SuiteModel.id == self.cycle_id)).one_or_none()
    #         self.cycle = result

    def load_cycles(self):
        with rx.session() as session:
            results = session.exec(CycleModel.select()).all()
            self.cycles = results

    def add_cycle(self, form_data:dict):
        with rx.session() as session:
            cycle = CycleModel(**form_data)
            session.add(cycle)
            session.commit()
            session.refresh(cycle)
            self.cycle = cycle
    
    # def save_suite_edits(self, cycle_id:int, updated_data:dict):
    #     with rx.session() as session:        
    #         suite = session.exec(SuiteModel.select().where(SuiteModel.id == cycle_id)).one_or_none()

    #         if (suite is None):
    #             return
    #         for key, value in updated_data.items():
    #             setattr(suite, key, value)

    #         session.add(suite)
    #         session.commit()
    #         session.refresh(suite)
    #         self.cycle = suite

    # def to_suite(self, edit_page=True):
    #     if not self.cycle:
    #         return rx.redirect(routes.SUITES)
    #     if edit_page:
    #         return rx.redirect(self.suite_edit_url)
    #     return rx.redirect(self.suite_url)
    
    # def collapse_searches(self):
    #     self.show_case_search = False
    #     self.show_scenario_search = False
    
    # def toggle_case_search(self):
    #     self.show_case_search = not(self.show_case_search)

    # def load_children(self):
    #     with rx.session() as session:
    #         results = session.exec(SuiteChildModel.select().where(SuiteChildModel.cycle_id == self.cycle_id).order_by(SuiteChildModel.order)).all()
    #         if (len(results) > 0):
    #             for single_result in results:
    #                 child = None
    #                 if (single_result.child_type_id == 1):
    #                     child = session.exec(ScenarioModel.select().where(ScenarioModel.id == single_result.child_id)).first()
    #                 elif (single_result.child_type_id == 2):
    #                     child = session.exec(CaseModel.select().where(CaseModel.id == single_result.child_id)).first()
    #                 setattr(single_result, "child_name", child.name)
    #         self.children = results

    # def unlink_child(self, suite_child_id:int):
    #     with rx.session() as session:
    #         child_to_delete = session.exec(SuiteChildModel.select().where(SuiteChildModel.id == suite_child_id)).first()
    #         order_to_update = child_to_delete.order
    #         session.delete(child_to_delete)
    #         session.commit()

    #         children_to_update = session.exec(SuiteChildModel.select().where(SuiteChildModel.order > order_to_update)).all()
    #         for suite_child in children_to_update:
    #             suite_child.order = suite_child.order - 1
    #             session.add(suite_child)
    #             session.commit()
    #             session.refresh(suite_child)
    #     self.load_children()
    #     return rx.toast.info("child unlinked.")
    
    # def move_child_up(self, child_id:int):
    #     with rx.session() as session:
    #         child_going_up = session.exec(SuiteChildModel.select().where(SuiteChildModel.id == child_id)).first()
    #         old_order = child_going_up.order
    #         if (old_order != 1):
    #             child_going_down = session.exec(SuiteChildModel.select().where(SuiteChildModel.order == (old_order -1), SuiteChildModel.cycle_id == self.cycle_id)).first()
    #             new_order = child_going_down.order

    #             child_going_up.order = new_order
    #             session.add(child_going_up)
    #             session.commit()
    #             session.refresh(child_going_up)

    #             child_going_down.order = old_order
    #             session.add(child_going_down)
    #             session.commit()
    #             session.refresh(child_going_down)

    #             self.load_children()
    #         else:
    #             return rx.toast.warning("The child has reached min.")
            
    # def move_child_down(self, child_id:int):
    #     with rx.session() as session:
    #         child_going_down = session.exec(SuiteChildModel.select().where(SuiteChildModel.id == child_id)).first()
    #         old_order = child_going_down.order
    #         child_going_up = session.exec(SuiteChildModel.select().where(SuiteChildModel.order == (old_order +1), SuiteChildModel.cycle_id == self.cycle_id)).first()

    #         if (child_going_up is not None):
    #             new_order = child_going_up.order

    #             child_going_down.order = new_order
    #             session.add(child_going_down)
    #             session.commit()
    #             session.refresh(child_going_down)

    #             child_going_up.order = old_order
    #             session.add(child_going_up)
    #             session.commit()
    #             session.refresh(child_going_up)

    #             self.load_children()
    #         else:
    #             return rx.toast.warning("The child has reached max.")
    
    # def get_max_child_order(self, child_id:int, child_type_id:int):
    #     with rx.session() as session:
    #         linked_scenarios:SuiteChildModel = session.exec(SuiteChildModel.select().where(SuiteChildModel.cycle_id == self.cycle_id)).all()
    #         max_order = 0
    #         for linked_scenario in linked_scenarios:
    #             if ((linked_scenario.child_id == child_id) and (linked_scenario.child_type_id == child_type_id)):
    #                 return -1
                
    #             if linked_scenario.order > max_order:
    #                 max_order = linked_scenario.order
    #         return max_order + 1

    # def filter_test_cases(self, search_case_value):
    #     self.search_case_value = search_case_value
    #     self.load_cases_for_search()

    # def load_cases_for_search(self):
    #   with rx.session() as session:
    #         query = select(CaseModel)
    #         if self.search_case_value:
    #             search_case_value = (
    #                 f"%{str(self.search_case_value).lower()}%"
    #             )
    #             #TODO: review this query... galadriel doesn't have payments...
    #             query = query.where(
    #                 or_(
    #                     *[
    #                         getattr(CaseModel, field).ilike(
    #                             search_case_value
    #                         )
    #                         for field in CaseModel.get_fields()
    #                         if field
    #                         not in ["id", "payments"]
    #                     ],
    #                     # ensures that payments is cast to a string before applying the ilike operator
    #                     cast(
    #                         CaseModel.name, String
    #                     ).ilike(search_case_value),
    #                 )
    #             )

    #         results = session.exec(query).all()
    #         self.cases_for_search = results

    # def link_case(self, case_id:int):
    #     suite_case_data:dict = {"cycle_id":""}
    #     new_case_order = 1

    #     if (len(self.scenarios_for_search) > 0):
    #         new_case_order = self.get_max_child_order(case_id, 2)

    #         if new_case_order == -1:
    #             return rx.toast.error("already in list")

    #     suite_case_data.update({"cycle_id":self.cycle_id})
    #     suite_case_data.update({"child_type_id":2})
    #     suite_case_data.update({"child_id":case_id})
    #     suite_case_data.update({"order":new_case_order})

    #     with rx.session() as session:
    #         case_to_add = SuiteChildModel(**suite_case_data)
    #         session.add(case_to_add)
    #         session.commit()
    #         session.refresh(case_to_add)
    #     self.search_value = ""
    #     self.collapse_searches()
    #     self.load_children()
        
    #     return rx.toast.success("case added!")

    # def toggle_scenario_search(self):
    #     self.show_scenario_search = not(self.show_scenario_search)

    # def filter_scenarios(self, search_scenario_value):
    #     self.search_scenario_value = search_scenario_value
    #     self.load_scenarios_for_search()

    # def load_scenarios_for_search(self):
    #   with rx.session() as session:
    #         query = select(ScenarioModel)
    #         if self.search_scenario_value:
    #             search_scenario_value = (
    #                 f"%{str(self.search_scenario_value).lower()}%"
    #             )
    #             #TODO: review this query... galadriel doesn't have payments...
    #             query = query.where(
    #                 or_(
    #                     *[
    #                         getattr(ScenarioModel, field).ilike(
    #                             search_scenario_value
    #                         )
    #                         for field in ScenarioModel.get_fields()
    #                         if field
    #                         not in ["id", "payments"]
    #                     ],
    #                     # ensures that payments is cast to a string before applying the ilike operator
    #                     cast(
    #                         ScenarioModel.name, String
    #                     ).ilike(search_scenario_value),
    #                 )
    #             )

    #         results = session.exec(query).all()
    #         self.scenarios_for_search = results

    # def link_scenario(self, scenario_id:int):
    #     suite_scenario_data:dict = {"cycle_id":""}
    #     new_scenario_order = 1

    #     if (len(self.scenarios_for_search) > 0):
    #         new_scenario_order = self.get_max_child_order(scenario_id, 1)

    #         if new_scenario_order == -1:
    #             return rx.toast.error("already in list")

    #     suite_scenario_data.update({"cycle_id":self.cycle_id})
    #     suite_scenario_data.update({"child_type_id":1})
    #     suite_scenario_data.update({"child_id":scenario_id})
    #     suite_scenario_data.update({"order":new_scenario_order})

    #     with rx.session() as session:
    #         scenario_to_add = SuiteChildModel(**suite_scenario_data)
    #         session.add(scenario_to_add)
    #         session.commit()
    #         session.refresh(scenario_to_add)
    #     self.search_value = ""
    #     self.collapse_searches()
    #     self.load_children()
        
    #     return rx.toast.success("scenario added!")
    
class AddCycleState(CycleState):
    form_data:dict = {}

    def handle_submit(self, form_data):
        self.form_data = form_data
        self.add_cycle(form_data)
        return rx.redirect(routes.CYCLES)

# class EditSuiteState(CycleState):
#     form_data:dict = {}
#     # suite_name:str = ""
    
#     def handle_submit(self, form_data):
#         self.form_data = form_data
#         cycle_id = form_data.pop("cycle_id")
#         updated_data = {**form_data}
#         self.save_suite_edits(cycle_id, updated_data)
#         return rx.redirect(routes.SUITES)
#         #return self.to_suite() #<-- review this code, why it was changed?