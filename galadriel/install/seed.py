"""Database seeding logic for first-run initialization."""

import reflex as rx
import reflex_local_auth

from .. import cycle, iteration, suite, user

from ..config import ConfigModel

cycle_child_types: cycle.CycleChildTypeModel = []
cycle_status: cycle.CycleStatusModel = []
iteration_snapshot_status: iteration.IterationSnapshotStatusModel = []
iteration_status: iteration.IterationStatusModel = []
suite_types: suite.SuiteChildTypeModel = []

galadriel_user_roles: user.GaladrielUserRole = []
local_users: reflex_local_auth.LocalUser = []
galadriel_users: user.GaladrielUser = []

cycle_child_types = [
    {"id":0, "type_name":"suite",},
    {"id":1, "type_name":"scenario",},
    {"id":2, "type_name":"case",},
    {"id":3, "type_name":"step",},
]

cycle_statuses = [
    {"id":0, "status_name":"passed",},
    {"id":1, "status_name":"failed",},
]

iteration_snapshot_statuses = [
    {"id":0, "status_name":"to do",},
    {"id":1, "status_name":"failed",},
    {"id":2, "status_name":"pass",},
    {"id":3, "status_name":"skipped",},
    {"id":4, "status_name":"blocked",},
]

iteration_statuses = [
    {"id":0, "name":"not started",},
    {"id":1, "name":"in progress",},
    {"id":2, "name":"on hold",},
    {"id":3, "name":"closed",},
    {"id":4, "name":"completed",},
]

suite_types = [
    {"id":0, "type_name":"scenario",},
    {"id":1, "type_name":"case",},
]

galadriel_user_roles = [
    {"id":0, "name":"admin", "description":"Manages user access"},
    {"id":1, "name":"viewer", "description":"Can navigate through the galadriel instance"},
    {"id":2, "name":"editor", "description":"Can perform any task in the galadriel instance, but manage users"},
    {"id":3, "name":"user manager", "description":"Can manage users but cannot assign or modify the admin role"},
]

local_users = [
    {"id":0, "username":"admin", "password_hash":"admin", "enabled":1},
]

galadriel_users = [
    {"id":0, "email":"no_email", "user_id":0, "user_role":0, "active":True},
]

def is_first_run() -> bool:
    """Return True if the database has not been seeded yet."""
    with rx.session() as session:
        to_return = session.exec(ConfigModel.select().where(ConfigModel.name == "first_run")).one_or_none()
        return (to_return == None)
    
def seed_db():
    """Clear existing seed data and insert fresh seed records."""
    __clear_seed_data()
    __insert_seed_data()

def __clear_seed_data():
    with rx.session() as session:
        for model in [
            cycle.CycleChildTypeModel,
            cycle.CycleStatusModel,
            iteration.IterationSnapshotStatusModel,
            iteration.IterationStatusModel,
            suite.SuiteChildTypeModel,
            user.GaladrielUser,
            user.GaladrielUserRole,
            reflex_local_auth.LocalUser,
        ]:
            results = session.exec(model.select()).all()
            for to_delete in results:
                session.delete(to_delete)
        session.commit()

def __insert_seed_data():
    with rx.session() as session:
        for item in cycle_child_types:
            session.add(cycle.CycleChildTypeModel(**item))

        for item in cycle_statuses:
            session.add(cycle.CycleStatusModel(**item))

        for item in iteration_snapshot_statuses:
            session.add(iteration.IterationSnapshotStatusModel(**item))

        for item in iteration_statuses:
            session.add(iteration.IterationStatusModel(**item))

        for item in suite_types:
            session.add(suite.SuiteChildTypeModel(**item))

        for local_user in local_users:
            local_user["password_hash"] = reflex_local_auth.LocalUser.hash_password(local_user["password_hash"])
            session.add(reflex_local_auth.LocalUser(**local_user))

        for item in galadriel_user_roles:
            session.add(user.GaladrielUserRole(**item))

        for item in galadriel_users:
            session.add(user.GaladrielUser(**item))

        session.commit()

def set_first_run():
    """Mark the database as seeded so seeding does not repeat."""
    first_run:dict = {"name":"first_run", "value": "1"}

    with rx.session() as session:
        to_add = ConfigModel(**first_run)
        session.add(to_add)
        session.commit()