import reflex as rx
from ..iteration.model import IterationModel

class DashboardState(rx.State):

    @rx.var(cache=True)
    def cycke_count(self) -> int:
        with rx.session() as session:
            return len(session.exec(IterationModel.select().where(IterationModel.iteration_status_id == 1)).all())