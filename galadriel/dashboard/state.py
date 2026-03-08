import reflex as rx
import logging
from typing import List
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

from ..iteration.model import IterationModel
from ..iteration.model import IterationSnapshotModel, IterationSnapshotLinkedIssues

from sqlmodel import select, col, desc
from ..utils import jira, timing, consts
from rxconfig import config

MAX_LINKED_BUGS = 5


def _fetch_issue(issue_key: str) -> dict | None:
    """Fetch a single Jira issue. Designed to run in a thread pool."""
    return jira.get_issue(issue_key)


class DashboardState(rx.State):

    linked_bugs: List[List[str]] = []

    cycle_count: int = 0
    skipped_cases: int = 0
    blocked_cases: int = 0
    cases_without_bug: int = 0
    pie_chart_data: list = []
    trend_data: list = []
    _loading_bugs: bool = False

    def load_dashboard(self):
        with rx.session() as session:
            in_progress = session.exec(
                select(IterationModel).where(IterationModel.iteration_status_id == consts.ITERATION_STATUS_IN_PROGRESS)
            ).all()

            self.cycle_count = len(in_progress)

            if not in_progress:
                self.skipped_cases = 0
                self.blocked_cases = 0
                self.cases_without_bug = 0
                self.pie_chart_data = []
                self.linked_bugs = []
                self.trend_data = self.__build_empty_trend_data()
                return

            iteration_ids = [it.id for it in in_progress]

            all_steps = session.exec(
                select(IterationSnapshotModel).where(
                    IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP,
                    col(IterationSnapshotModel.iteration_id).in_(iteration_ids),
                )
            ).all()

            passed = 0
            failed = 0
            blocked = 0
            skipped = 0
            failed_step_ids = []

            for step in all_steps:
                if step.child_status_id == consts.SNAPSHOT_STATUS_PASS:
                    passed += 1
                elif step.child_status_id == consts.SNAPSHOT_STATUS_FAILED:
                    failed += 1
                    failed_step_ids.append(step.id)
                elif step.child_status_id == consts.SNAPSHOT_STATUS_BLOCKED:
                    blocked += 1
                elif step.child_status_id == consts.SNAPSHOT_STATUS_SKIPPED:
                    skipped += 1

            self.skipped_cases = skipped
            self.blocked_cases = blocked

            steps_with_bugs = 0
            if failed_step_ids:
                linked_issues = session.exec(
                    select(IterationSnapshotLinkedIssues.iteration_snapshot_id).where(
                        col(IterationSnapshotLinkedIssues.iteration_snapshot_id).in_(failed_step_ids),
                        IterationSnapshotLinkedIssues.unlinked == None,
                    )
                ).all()
                steps_with_bugs = len(set(linked_issues))
            self.cases_without_bug = failed - steps_with_bugs

            total = passed + failed + blocked
            if total > 0:
                self.pie_chart_data = [
                    {"name": "Passed", "value": round((passed / total) * 100, 2), "fill": "#71d083"},
                    {"name": "Failed", "value": round((failed / total) * 100, 2), "fill": "#b0a9ff"},
                    {"name": "Blocked", "value": round((blocked / total) * 100, 2), "fill": "#ff8a88"},
                ]
            else:
                self.pie_chart_data = []

            self.trend_data = self.__compute_trend_data(session)

        return DashboardState.load_linked_bugs

    def __build_empty_trend_data(self) -> list:
        trend_data = []
        current_utc_date = datetime.now(timezone.utc)
        for _ in range(11):
            trend_data.append({"date": timing.convert_utc_to_local(current_utc_date).strftime("%Y-%m-%d"), "exec": 0, "passed": 0, "failed": 0, "blocked": 0})
            current_utc_date = current_utc_date - timedelta(days=1)
        trend_data.reverse()
        return trend_data

    def __compute_trend_data(self, session) -> list:
        trend_data = []
        current_utc_date = datetime.now(timezone.utc)
        cutoff_date = current_utc_date - timedelta(days=11)

        for _ in range(11):
            trend_data.append({"date": current_utc_date.strftime("%Y-%m-%d %H:%M:%S"), "exec": 0, "passed": 0, "failed": 0, "blocked": 0})
            current_utc_date = current_utc_date - timedelta(days=1)

        status_map = {
            consts.SNAPSHOT_STATUS_PASS: "passed",
            consts.SNAPSHOT_STATUS_FAILED: "failed",
            consts.SNAPSHOT_STATUS_BLOCKED: "blocked",
        }

        updated_cases = session.exec(
            select(IterationSnapshotModel).where(
                IterationSnapshotModel.child_type == consts.CHILD_TYPE_STEP,
                IterationSnapshotModel.updated >= cutoff_date,
            ).order_by(desc(IterationSnapshotModel.updated))
        ).all()

        for updated_case in updated_cases:
            if updated_case.updated is None:
                continue
            case_date = updated_case.updated.strftime("%Y-%m-%d")
            for trend_entry in trend_data:
                trend_entry_date = datetime.strptime(trend_entry["date"], "%Y-%m-%d %H:%M:%S")
                if trend_entry_date.strftime("%Y-%m-%d") == case_date:
                    trend_entry["exec"] += 1
                    status_key = status_map.get(updated_case.child_status_id)
                    if status_key:
                        trend_entry[status_key] += 1
                    break

        for trend_entry in trend_data:
            trend_entry["date"] = timing.convert_utc_to_local(datetime.strptime(trend_entry["date"], "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d")

        trend_data.reverse()
        return trend_data

    @rx.event(background=True)
    async def load_linked_bugs(self):
        async with self:
            if self._loading_bugs:
                return
            self._loading_bugs = True

        try:
            with rx.session() as session:
                all_linked_bugs = session.exec(
                    select(IterationSnapshotLinkedIssues)
                        .where(IterationSnapshotLinkedIssues.unlinked == None)
                        .order_by(desc(IterationSnapshotLinkedIssues.created))
                        .limit(MAX_LINKED_BUGS * 2)
                ).all()

            unique_keys = list(dict.fromkeys(bug.issue_key for bug in all_linked_bugs))

            results = {}
            with ThreadPoolExecutor(max_workers=MAX_LINKED_BUGS) as executor:
                futures = {executor.submit(_fetch_issue, key): key for key in unique_keys}
                for future in as_completed(futures):
                    key = futures[future]
                    try:
                        results[key] = future.result()
                    except Exception:
                        logger.exception("Failed to fetch Jira issue %s", key)
                        results[key] = None

            bugs = []
            for linked_bug in all_linked_bugs:
                if len(bugs) >= MAX_LINKED_BUGS:
                    break
                raw_issue = results.get(linked_bug.issue_key)
                if raw_issue is None:
                    continue
                if raw_issue["fields"]["status"]["name"] != config.jira_done_status:
                    bugs.append([raw_issue["key"], jira.get_issue_url(raw_issue["key"]), raw_issue["fields"]["summary"], raw_issue["fields"]["status"]["name"], raw_issue["fields"]["updated"]])

            async with self:
                self._loading_bugs = False
                self.linked_bugs = bugs
        except Exception:
            logger.exception("Unexpected error loading linked bugs")
            async with self:
                self._loading_bugs = False
                self.linked_bugs = []
            return rx.toast.error("there was an error while loading the linked bugs")
