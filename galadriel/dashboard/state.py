import reflex as rx
from ..iteration.model import IterationModel
from ..iteration.model import IterationSnapshotModel

class DashboardState(rx.State):

    def __get_in_progress_iterations(self):
        with rx.session() as session:
            return session.exec(IterationModel.select().where(IterationModel.iteration_status_id == 1)).all()

    @rx.var(cache=False)
    def cycke_count(self) -> int:
        return len(self.__get_in_progress_iterations())
        
    @rx.var(cache=False)
    def skipped_cases(self) -> int:
        in_progress_iter = self.__get_in_progress_iterations()
        skipped_case_count = 0

        for iteration in in_progress_iter:
            with rx.session() as session:
                skipped_case_count = skipped_case_count + len(session.exec(IterationSnapshotModel.select().where(IterationSnapshotModel.child_type == 4, IterationSnapshotModel.iteration_id == iteration.id, IterationSnapshotModel.child_status_id == 4)).all())

        return skipped_case_count