import reflex as rx
from typing import List
from datetime import datetime, timedelta, timezone

from ..iteration.model import IterationModel
from ..iteration.model import IterationSnapshotModel, IterationSnapshotLinkedIssues

from sqlmodel import desc
from ..utils import jira, timing, consts
from rxconfig import config

class DashboardState(rx.State):

    linked_bugs: List[str] = []

    def __get_in_progress_iterations(self):
        with rx.session() as session:
            return session.exec(IterationModel.select().where(IterationModel.iteration_status_id == consts.ITERATION_STATUS_IN_PROGRESS)).all()
        
    def __get_case_count_by_status(self, status_id: int) -> int:
        in_progress_iter = self.__get_in_progress_iterations()
        case_count = 0

        with rx.session() as session:
            for iteration in in_progress_iter:
                case_count = case_count + len(session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP, IterationSnapshotModel.iteration_id == iteration.id, IterationSnapshotModel.child_status_id == status_id)).all())

        return case_count

    @rx.var(cache=False)
    def cycle_count(self) -> int:
        return len(self.__get_in_progress_iterations())
        
    @rx.var(cache=False)
    def skipped_cases(self) -> int:
        return self.__get_case_count_by_status(consts.SNAPSHOT_STATUS_SKIPPED)
    
    @rx.var(cache=False)
    def cases_without_bug(self) -> int:
        in_progress_iter = self.__get_in_progress_iterations()
        cases_without_bug_count = 0
        failed_cases_count = 0

        for iteration in in_progress_iter:
            with rx.session() as session:
                failed_cases = session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP, IterationSnapshotModel.iteration_id == iteration.id, IterationSnapshotModel.child_status_id == consts.SNAPSHOT_STATUS_FAILED)).all()
                if (failed_cases != None):
                    failed_cases_count += len(failed_cases)

                for failed_case in failed_cases:
                    linked_issues = session.exec(IterationSnapshotLinkedIssues.select().where(IterationSnapshotLinkedIssues.iteration_snapshot_id == failed_case.id, IterationSnapshotLinkedIssues.unlinked == None)).all()
                    cases_without_bug_count += len(linked_issues)

        return failed_cases_count - cases_without_bug_count
    
    @rx.var(cache=False)
    def blocked_cases(self) -> int:
        return self.__get_case_count_by_status(consts.SNAPSHOT_STATUS_BLOCKED)
    
    def __get_passed_cases(self) -> int:
        return self.__get_case_count_by_status(consts.SNAPSHOT_STATUS_PASS)
    
    def __get_failed_cases(self) -> int:
        return self.__get_case_count_by_status(consts.SNAPSHOT_STATUS_FAILED)
    
    @rx.var(cache=False)
    def get_pie_chart_data(self) -> list:
        passed_cases = self.__get_passed_cases()
        failed_cases = self.__get_failed_cases()
        blocked_cases = self.blocked_cases

        total_cases = passed_cases + failed_cases + blocked_cases

        passed_percentage = round((passed_cases / total_cases) * 100, 2) if total_cases > 0 else 0
        failed_percentage = round((failed_cases / total_cases) * 100, 2) if total_cases > 0 else 0
        blocked_percentage = round((blocked_cases / total_cases) * 100, 2) if total_cases > 0 else 0

        return [
            {"name": "Passed", "value": passed_percentage, "fill": "#71d083"},
            {"name": "Failed", "value": failed_percentage, "fill": "#b0a9ff"},
            {"name": "Blocked", "value": blocked_percentage, "fill": "#ff8a88"},
        ]
    
    async def load_linked_bugs(self):
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
                raw_issue = jira.get_issue(linked_bug.issue_key)

                if raw_issue is None:
                    return rx.toast.error("there was an error while loading the linked bugs")
                if raw_issue["fields"]["status"]["name"] != config.jira_done_status:
                    self.linked_bugs.append([raw_issue["key"], jira.get_issue_url(raw_issue["key"]), raw_issue["fields"]["summary"], raw_issue["fields"]["status"]["name"], raw_issue["fields"]["updated"]])
                    appended_bugs += 1
            else:
                break

    def __build_trend_data(self):
        trend_data = []
        current_utc_date = datetime.now(timezone.utc)
        for _ in range(11):
            trend_data.append({"date": current_utc_date.strftime("%Y-%m-%d %H:%M:%S"), "exec": 0, "passed": 0, "failed": 0, "blocked": 0})
            current_utc_date = current_utc_date - timedelta(days=1)
        return trend_data, current_utc_date

    def __apply_case_to_trend(self, trend_data, updated_case):
        STATUS_MAP = {consts.SNAPSHOT_STATUS_PASS: "passed", consts.SNAPSHOT_STATUS_FAILED: "failed", consts.SNAPSHOT_STATUS_BLOCKED: "blocked"}
        case_date = updated_case.updated.strftime("%Y-%m-%d")

        for trend_entry in trend_data:
            trend_entry_date = datetime.strptime(trend_entry["date"], "%Y-%m-%d %H:%M:%S")
            if trend_entry_date.strftime("%Y-%m-%d") == case_date:
                trend_entry["exec"] += 1
                status_key = STATUS_MAP.get(updated_case.child_status_id)
                if status_key:
                    trend_entry[status_key] += 1
                break

    @rx.var(cache=False)
    def cases_trends(self) -> List:
        trend_data, cutoff_date = self.__build_trend_data()

        with rx.session() as session:
            updated_cases = session.exec(IterationSnapshotModel.select().where(
                IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP,
                IterationSnapshotModel.updated >= cutoff_date)
            .order_by(desc(IterationSnapshotModel.updated))).all()

            if updated_cases is not None:
                for updated_case in updated_cases:
                    self.__apply_case_to_trend(trend_data, updated_case)

                for trend_entry in trend_data:
                    trend_entry["date"] = timing.convert_utc_to_local(datetime.strptime(trend_entry["date"], "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d")

        list.reverse(trend_data)
        return trend_data
    
