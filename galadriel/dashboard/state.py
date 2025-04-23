import reflex as rx
from typing import List

from ..iteration.model import IterationModel
from ..iteration.model import IterationSnapshotModel, IterationSnapshotLinkedIssues

class DashboardState(rx.State):

    linked_bugs: List['IterationSnapshotLinkedIssues'] = []

    def __get_in_progress_iterations(self):
        with rx.session() as session:
            return session.exec(IterationModel.select().where(IterationModel.iteration_status_id == 1)).all()
        
    def __get_case_count_by_status(self, status_id: int) -> int:
        in_progress_iter = self.__get_in_progress_iterations()
        case_count = 0

        for iteration in in_progress_iter:
            with rx.session() as session:
                case_count = case_count + len(session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.child_type == 4, IterationSnapshotModel.iteration_id == iteration.id, IterationSnapshotModel.child_status_id == status_id)).all())

        return case_count

    @rx.var(cache=False)
    def cycle_count(self) -> int:
        return len(self.__get_in_progress_iterations())
        
    @rx.var(cache=False)
    def skipped_cases(self) -> int:
        return self.__get_case_count_by_status(4)
    
    @rx.var(cache=False)
    def cases_without_bug(self) -> int:
        in_progress_iter = self.__get_in_progress_iterations()
        cases_without_bug_count = 0
        failed_cases_count = 0

        for iteration in in_progress_iter:
            with rx.session() as session:
                failed_cases = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.child_type == 4, IterationSnapshotModel.iteration_id == iteration.id, IterationSnapshotModel.child_status_id == 2)).all()
                if (failed_cases != None):
                    failed_cases_count += len(failed_cases)

                for failed_case in failed_cases:
                    linked_issues = session.exec(IterationSnapshotLinkedIssues.select().where(IterationSnapshotLinkedIssues.iteration_snapshot_id == failed_case.id, IterationSnapshotLinkedIssues.unlinked == None)).all()
                    cases_without_bug_count += len(linked_issues)

        return failed_cases_count - cases_without_bug_count
    
    @rx.var(cache=False)
    def blocked_cases(self) -> int:
        return self.__get_case_count_by_status(5)
    
    def __get_passed_cases(self) -> int:
        return self.__get_case_count_by_status(3)
    
    def __get_failed_cases(self) -> int:
        return self.__get_case_count_by_status(2)
    
    @rx.var(cache=False)
    def get_pie_chart_data(self) -> list:
        passed_cases = self.__get_passed_cases()
        failed_cases = self.__get_failed_cases()
        blocked_cases = self.blocked_cases

        total_cases = passed_cases + failed_cases + blocked_cases

        passed_percentage = round((passed_cases / total_cases), 2) * 100 if total_cases > 0 else 0
        failed_percentage = round((failed_cases / total_cases), 2) * 100 if total_cases > 0 else 0
        blocked_percentage = round((blocked_cases / total_cases), 2) * 100 if total_cases > 0 else 0

        return [
            {"name": "Passed", "value": passed_percentage, "fill": "#71d083"},
            {"name": "Failed", "value": failed_percentage, "fill": "#b0a9ff"},
            {"name": "Blocked", "value": blocked_percentage, "fill": "#ff8a88"},
        ]
    
    #@rx.var(cache=False)
    def load_linked_bugs(self) -> rx.Component:
        in_progress_iter = self.__get_in_progress_iterations()

        for iteration in in_progress_iter:
            with rx.session() as session:
                pass

        #id, description, status, updated
        #rx.table.cell("TEST-7"), rx.table.cell("new bug"), rx.table.cell("In Progress"), rx.table.cell("2025-03-31")
        return rx.table.body(
            rx.table.row(rx.table.cell("TEST-1"), rx.table.cell("some bug"), rx.table.cell("To Do"), rx.table.cell("2025-03-31"), ),
            rx.table.row(rx.table.cell(rx.link("TEST-2", href="https://smallfix.atlassian.net/browse/TEST-2")), rx.table.cell("another bug"), rx.table.cell("In Progress"), rx.table.cell("2025-03-18"), ),
            rx.table.row(rx.table.cell("TEST-3"), rx.table.cell("this bug this bug this bug this bug this bug this bug"), rx.table.cell("Open"), rx.table.cell("2025-03-10"), ),
            rx.table.row(rx.table.cell("TEST-4"),rx.table.cell("that bug"), rx.table.cell("Closed"), rx.table.cell("2025-03-01"), ),
            rx.table.row(rx.table.cell("TEST-5"), rx.table.cell("some bug"), rx.table.cell("To Do"), rx.table.cell("2025-03-31"), ),
            rx.table.row(rx.table.cell("TEST-6"), rx.table.cell("another bug"), rx.table.cell("To Do"), rx.table.cell("2025-03-31"), ),
            rx.table.row(rx.table.cell("TEST-7"), rx.table.cell("new bug"), rx.table.cell("In Progress"), rx.table.cell("2025-03-31"), ),
        ),