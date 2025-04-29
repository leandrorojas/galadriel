import reflex as rx
from typing import List

from ..iteration.model import IterationModel
from ..iteration.model import IterationSnapshotModel, IterationSnapshotLinkedIssues

from sqlmodel import desc
from ..utils import jira
from rxconfig import config

class DashboardState(rx.State):

    linked_bugs: List[str] = []

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
    
    def load_linked_bugs(self):
        self.linked_bugs = []
        appended_bugs = 0
        with rx.session() as session:
            all_linked_bugs = session.exec(
                IterationSnapshotLinkedIssues.select()
                    .where(IterationSnapshotLinkedIssues.unlinked == None)
                    .order_by(desc(IterationSnapshotLinkedIssues.created))
                ).all()

        for linked_bug in all_linked_bugs:
            if (appended_bugs < 5):
                with rx.session() as session:
                    raw_issue = jira.get_issue(linked_bug.issue_key)

                    if raw_issue["fields"]["status"]["name"] != config.jira_done_status:
                        if (raw_issue != None):
                            self.linked_bugs.append([raw_issue["key"], jira.get_issue_url(raw_issue["key"]), raw_issue["fields"]["summary"], raw_issue["fields"]["status"]["name"], raw_issue["fields"]["updated"]])
                            appended_bugs += 1
                        else:
                            return rx.toast.error("there was an error while loading the linked bugs")
            else:
                break

    @rx.var(cache=False)
    def cases_trends(self) -> List:
        #to return days of the week, executed, passed, failed, blocked
        #find the latest ocurrence of updated cases

        with rx.session() as session:
            updated_cases = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.child_type == 4, IterationSnapshotModel.updated != None)).all()

        return  [
            {"name": "Page A", "exec": 4000, "passed": 2400, "failed": 2400},
            {"name": "Page B", "exec": 3000, "passed": 1398, "failed": 2210},
            {"name": "Page C", "exec": 2000, "passed": 9800, "failed": 2290},
            {"name": "Page D", "exec": 2780, "passed": 3908, "failed": 2000},
            {"name": "Page E", "exec": 1890, "passed": 4800, "failed": 2181},
            {"name": "Page F", "exec": 2390, "passed": 3800, "failed": 2500},
            {"name": "Page G", "exec": 3490, "passed": 4300, "failed": 2100}, 
        ]