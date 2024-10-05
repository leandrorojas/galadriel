from typing import List, Optional
import reflex as rx
from .model import SuiteModel, SuiteChildModel
from ..navigation import routes

from ..case.model import CaseModel
from ..scenario.model import ScenarioModel

from datetime import datetime

from sqlmodel import select, asc, or_, func, cast, String

SUITES_ROUTE = routes.SUITES
if SUITES_ROUTE.endswith("/"): SUITES_ROUTE = SUITES_ROUTE[:-1]

class SuiteState(rx.State):
    suites: List['SuiteModel'] = []
    suite: Optional['SuiteModel'] = None

    children: List['SuiteChildModel'] = []
    child: Optional['SuiteChildModel'] = None

    test_cases_for_search: List['CaseModel'] = []
    show_case_search:bool = False
    search_case_value:str = ""

    @rx.var
    def suite_id(self):
        #print(self.router.page.params)
        return self.router.page.params.get("id", "")
    
    @rx.var
    def suite_url(self):
        if not self.suite:
            return f"{SUITES_ROUTE}"
        return f"{SUITES_ROUTE}/{self.suite.id}"
    
    @rx.var
    def suite_edit_url(self):
        if not self.suite:
            return f"{SUITES_ROUTE}"
        return f"{SUITES_ROUTE}/{self.suite.id}/edit"

    def get_suite_detail(self):                
        with rx.session() as session:
            if (self.suite_id == ""):
                self.suite = None
                return
            result = session.exec(SuiteModel.select().where(SuiteModel.id == self.suite_id)).one_or_none()
            self.suite = result

    def load_suites(self):
        with rx.session() as session:
            results = session.exec(SuiteModel.select()).all()
            self.suites = results

    def add_suite(self, form_data:dict):
        with rx.session() as session:
            suite = SuiteModel(**form_data)
            session.add(suite)
            session.commit()
            session.refresh(suite)
            self.suite = suite
    
    def save_suite_edits(self, suite_id:int, updated_data:dict):
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

    def to_suite(self, edit_page=True):
        if not self.suite:
            return rx.redirect(routes.SUITES)
        if edit_page:
            return rx.redirect(self.suite_edit_url)
        return rx.redirect(self.suite_url)
    
    def toggle_case_search(self):
        self.show_case_search = not(self.show_case_search)

    def load_children(self):
        with rx.session() as session:
            results = session.exec(SuiteChildModel.select().where(SuiteChildModel.suite_id == self.suite_id).order_by(SuiteChildModel.order)).all()
            if (len(results) > 0):
                for single_result in results:
                    child = None
                    if (single_result.child_type_id == 1):
                        child = session.exec(ScenarioModel.select().where(ScenarioModel.id == single_result.child_id)).first()
                    elif (single_result.child_type_id == 2):
                        child = session.exec(CaseModel.select().where(CaseModel.id == single_result.child_id)).first()
                    setattr(single_result, "child_name", child.name)
            self.children = results

    def unlink_child(self, suite_child_id:int):
        with rx.session() as session:
            child_to_delete = session.exec(SuiteChildModel.select().where(SuiteChildModel.id == suite_child_id)).first()
            order_to_update = child_to_delete.order
            session.delete(child_to_delete)
            session.commit()

            children_to_update = session.exec(SuiteChildModel.select().where(SuiteChildModel.order > order_to_update)).all()
            for suite_child in children_to_update:
                suite_child.order = suite_child.order - 1
                session.add(suite_child)
                session.commit()
                session.refresh(suite_child)
        self.load_children()
        return rx.toast.info("child unlinked.")

    def filter_test_cases(self, search_case_value):
        self.search_case_value = search_case_value
        self.load_cases_for_search()

    def load_cases_for_search(self):
      with rx.session() as session:
            query = select(CaseModel)
            if self.search_case_value:
                search_case_value = (
                    f"%{str(self.search_case_value).lower()}%"
                )
                #TODO: review this query... galadriel doesn't have payments...
                query = query.where(
                    or_(
                        *[
                            getattr(CaseModel, field).ilike(
                                search_case_value
                            )
                            for field in CaseModel.get_fields()
                            if field
                            not in ["id", "payments"]
                        ],
                        # ensures that payments is cast to a string before applying the ilike operator
                        cast(
                            CaseModel.name, String
                        ).ilike(search_case_value),
                    )
                )

            results = session.exec(query).all()
            self.test_cases_for_search = results

    def link_case(self, case_id:int):
        suite_case_data:dict = {"suite_id":""}
        new_case_order = 1

        if (len(self.test_cases_for_search) > 0):
            with rx.session() as session:
                linked_cases:SuiteChildModel = session.exec(SuiteChildModel.select().where(SuiteChildModel.suite_id == self.suite_id and SuiteChildModel.child_type_id == "2")).all()
                print(linked_cases)
                max_order = 0
                for linked_case in linked_cases:
                    if (linked_case.child_id == case_id):
                        self.toggle_case_search()
                        return rx.toast.error("prerequisite already in list")
                    
                    if linked_case.order > max_order:
                        max_order = linked_case.order
                new_case_order = max_order + 1

                #TODO: if failes in othe add name of the Test Case here?

        suite_case_data.update({"suite_id":self.suite_id})
        suite_case_data.update({"child_type_id":2})
        suite_case_data.update({"child_id":case_id})
        suite_case_data.update({"order":new_case_order})

        with rx.session() as session:
            case_to_add = SuiteChildModel(**suite_case_data)
            session.add(case_to_add)
            session.commit()
            session.refresh(case_to_add)
        self.search_value = ""
        self.load_children()
        
        return rx.toast.success("case added!")

class AddSuiteState(SuiteState):
    form_data:dict = {}

    def handle_submit(self, form_data):
        self.form_data = form_data
        self.add_suite(form_data)
        return rx.redirect(routes.SUITES)

class EditSuiteState(SuiteState):
    form_data:dict = {}
    # suite_name:str = ""
    
    def handle_submit(self, form_data):
        self.form_data = form_data
        suite_id = form_data.pop("suite_id")
        updated_data = {**form_data}
        self.save_suite_edits(suite_id, updated_data)
        return rx.redirect(routes.SUITES)
        #return self.to_suite() #<-- review this code, why it was changed?