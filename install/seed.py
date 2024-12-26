from alembic import op
from sqlalchemy import Table, MetaData

#cyclechildtypemodel
cyclechildtype_metadata = MetaData(bind=op.get_bind())
cyclechildtype_metadata.reflect(only=('cyclechildtypemodel',))

# define table representation
cyclechildtypemodel_table = Table('cyclechildtypemodel', cyclechildtype_metadata)

# insert records
op.bulk_insert(
    cyclechildtypemodel_table,
    [
        {
            "id":1,
            "type_name": "Suite",
        },
        {
            "id":2,
            "type_name": "Scenario",
        },
        {
            "id":3,
            "type_name": "Case",
        },
        {
            "id":4,
            "type_name": "Step",
        },
    ],
)

cyclechildtypemodel_table = None
cyclechildtype_metadata = None

#cyclestatusmodel
cyclestatus_metadata = MetaData(bind=op.get_bind())
cyclestatus_metadata.reflect(only=('cyclestatusmodel',))

# define table representation
cyclestatusmodel_table = Table('cyclestatusmodel', cyclestatus_metadata)

# insert records
op.bulk_insert(
    cyclestatusmodel_table,
    [
        {
            "id":0,
            "type_name": "passed",
        },
        {
            "id":1,
            "type_name": "failed",
        },
    ],
)

cyclestatusmodel_table = None
cyclestatus_metadata = None

#iterationsnapshotstatusmodel
iterationsnapshotstatus_metadata = MetaData(bind=op.get_bind())
iterationsnapshotstatus_metadata.reflect(only=('iterationsnapshotstatusmodel',))

# define table representation
iterationsnapshotstatusmodel_table = Table('iterationsnapshotstatusmodel', iterationsnapshotstatus_metadata)

# insert records
op.bulk_insert(
    iterationsnapshotstatusmodel_table,
    [
        {
            "id":1,
            "type_name": "to do",
        },
        {
            "id":2,
            "type_name": "failed",
        },
        {
            "id":3,
            "type_name": "pass",
        },
        {
            "id":4,
            "type_name": "skipped",
        },
        {
            "id":5,
            "type_name": "blocked",
        },
    ],
)

iterationsnapshotstatusmodel_table = None
iterationsnapshotstatus_metadata = None

#iterationstatusmodel
iterationstatus_metadata = MetaData(bind=op.get_bind())
iterationstatus_metadata.reflect(only=('iterationstatusmodel',))

# define table representation
iterationstatusmodel_table = Table('iterationstatusmodel', iterationstatus_metadata)

# insert records
op.bulk_insert(
    iterationstatusmodel_table,
    [
        {
            "id":0,
            "type_name": "not started",
        },
        {
            "id":1,
            "type_name": "in progress",
        },
        {
            "id":2,
            "type_name": "on hold",
        },
        {
            "id":3,
            "type_name": "closed",
        },
        {
            "id":4,
            "type_name": "completed",
        },
    ],
)

iterationstatusmodel_table = None
iterationstatus_metadata = None

#suitechildtypemodel
suitechildtype_metadata = MetaData(bind=op.get_bind())
suitechildtype_metadata.reflect(only=('suitechildtypemodel',))

# define table representation
suitechildtypemodel_table = Table('suitechildtypemodel', suitechildtype_metadata)

# insert records
op.bulk_insert(
    suitechildtypemodel_table,
    [
        {
            "id":0,
            "type_name": "not started",
        },
        {
            "id":1,
            "type_name": "in progress",
        },
        {
            "id":2,
            "type_name": "on hold",
        },
        {
            "id":3,
            "type_name": "closed",
        },
        {
            "id":4,
            "type_name": "completed",
        },
    ],
)

suitechildtypemodel_table = None
suitechildtype_metadata = None