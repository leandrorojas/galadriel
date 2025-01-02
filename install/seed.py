import reflex as rx
from ..galadriel import cycle, iteration, suite

from ..galadriel.config import ConfigModel

cycle_child_types: cycle.CycleChildTypeModel = []
cycle_status: cycle.CycleStatusModel = []
iteration_snapshot_status: iteration.IterationSnapshotStatusModel = []
iteration_status: iteration.IterationStatusModel = []
suite_tyoe: suite.SuiteChildTypeModel = []

cycle_child_types = [
    {"id":1, "type_name": "Suite",},
    {"id":2,"type_name": "Scenario",},
    {"id":3,"type_name": "Case",},
    {"id":4,"type_name": "Step",},
]

cycle_statuses = [
    {"id":0,"type_name": "passed",},
    {"id":1,"type_name": "failed",},
]

iteration_snapshot_statuses = [
    {"id":1,"type_name": "to do",},
    {"id":2,"type_name": "failed",},
    {"id":3,"type_name": "pass",},
    {"id":4,"type_name": "skipped",},
    {"id":5,"type_name": "blocked",},
]

iteration_statuses = [
    {"id":0,"type_name": "not started",},
    {"id":1,"type_name": "in progress",},
    {"id":2,"type_name": "on hold",},
    {"id":3,"type_name": "closed",},
    {"id":4,"type_name": "completed",},
]

suite_tyoes = [
    {"id":0,"type_name": "not started",},
    {"id":1,"type_name": "in progress",},
    {"id":2,"type_name": "on hold",},
    {"id":3,"type_name": "closed",},
    {"id":4,"type_name": "completed",},
]

def first_run() -> bool:
    with rx.session() as session:
        to_return = session.exec(ConfigModel.select().where(ConfigModel.name == "")).one_or_none()

        return (to_return == None)
        

def insert_seed_data():
    for cycle_child_type in cycle_child_types:
        with rx.session() as session:
            cycle_child_type = cycle.CycleChildTypeModel(**cycle_child_type)
            session.add(cycle_child_type)
            session.commit()

    for cycle_status in cycle_statuses:
        with rx.session() as session:
            cycle_status = cycle.CycleStatusModel(**cycle_status)
            session.add(cycle_status)
            session.commit()

    for iteration_snapshot_status in iteration_snapshot_statuses:
        with rx.session() as session:
            iteration_snapshot_status = iteration.IterationSnapshotStatusModel(**iteration_snapshot_status)
            session.add(iteration_snapshot_status)
            session.commit()

    for iteration_status in iteration_statuses:
        with rx.session() as session:
            iteration_status = iteration.IterationStatusModel(**iteration_status)
            session.add(iteration_status)
            session.commit()

    for suite_type in suite_tyoes:
        with rx.session() as session:
            suite_type = suite.SuiteChildTypeModel(**suite_type)
            session.add(suite_type)
            session.commit()