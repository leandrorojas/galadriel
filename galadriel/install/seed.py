import reflex as rx
from .. import cycle, iteration, suite

from ..config import ConfigModel

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
    {"id":0,"status_name": "passed",},
    {"id":1,"status_name": "failed",},
]

iteration_snapshot_statuses = [
    {"id":1,"status_name": "to do",},
    {"id":2,"status_name": "failed",},
    {"id":3,"status_name": "pass",},
    {"id":4,"status_name": "skipped",},
    {"id":5,"status_name": "blocked",},
]

iteration_statuses = [
    {"id":0,"name": "not started",},
    {"id":1,"name": "in progress",},
    {"id":2,"name": "on hold",},
    {"id":3,"name": "closed",},
    {"id":4,"name": "completed",},
]

suite_tyoes = [
    {"id":0,"type_name": "not started",},
    {"id":1,"type_name": "in progress",},
    {"id":2,"type_name": "on hold",},
    {"id":3,"type_name": "closed",},
    {"id":4,"type_name": "completed",},
]

def is_first_run() -> bool:
    with rx.session() as session:
        to_return = session.exec(ConfigModel.select().where(ConfigModel.name == "first_run")).one_or_none()
        return (to_return == None)
    
def seed_db():
    __clear_seed_data()
    __insert_seed_data()

def __clear_seed_data():
    with rx.session() as session:
        #delete CycleChildTypeModel
        results = session.exec(cycle.CycleChildTypeModel.select()).all()
        for to_delete in results:
            session.delete(to_delete)
            session.commit()
        results = None

        #delete CycleStatusModel
        results = session.exec(cycle.CycleStatusModel.select()).all()
        for to_delete in results:
            session.delete(to_delete)
            session.commit()
        results = None

        #delete IterationSnapshotStatusModel
        results = session.exec(iteration.IterationSnapshotStatusModel.select()).all()
        for to_delete in results:
            session.delete(to_delete)
            session.commit()
        results = None

        #delete IterationStatusModel
        results = session.exec(iteration.IterationStatusModel.select()).all()
        for to_delete in results:
            session.delete(to_delete)
            session.commit()
        results = None

        #delete SuiteChildTypeModel
        results = session.exec(suite.SuiteChildTypeModel.select()).all()
        for to_delete in results:
            session.delete(to_delete)
            session.commit()
        results = None

def __insert_seed_data():
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

def set_first_run():
    first_run:dict = {"name":"first_run", "value": "1"}

    with rx.session() as session:
        to_add = ConfigModel(**first_run)
        session.add(to_add)
        session.commit()