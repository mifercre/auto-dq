import re
import pyhive
import sqlalchemy
from sqlalchemy import inspect, create_engine
from sqlalchemy.orm import sessionmaker, Session

import crud
import schemas
from core.config import settings
from core.db_engines import engine_specs
from celery_app import celery_app
from models import DB
from models.deps import df_from_query


def get_sessionmaker_instance(uri: str) -> sessionmaker:
    engine = create_engine(uri, pool_pre_ping=True)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return Session


def delete_blacklisted_schema(db_session: Session, schema_name: str, database: DB):
    if database.blacklist:
        for bl in database.blacklist.split(','):

            # Check if schema is one of the blacklisted schemas on this DB
            if bool(re.search(bl.strip(), schema_name)):

                # If it's blacklisted, then check if it existed before on this DB and delete the metadata
                for s in database.schemas:
                    if schema_name == s.name:
                        crud.db_schema.remove(db=db_session, id=s.id)

                return True


@celery_app.task(acks_late=True)
def fetch_db_tree(db_id: int):
    db_session = get_sessionmaker_instance(settings.SQLALCHEMY_DATABASE_URI)()
    database = crud.db.get(db=db_session, id=db_id)

    engine_spec = engine_specs.get(database.type)
    engine = engine_spec.get_sqla_engine(
        hostname=database.hostname, port=database.port, database=database.database,
        username=database.username, password=database.password
    )
    insp = inspect(engine)
    schema_names = insp.get_schema_names()

    existing_schemas_names = [s.name for s in database.schemas]

    # Fetch schemas and save then into DQ db
    for schema_name in schema_names:

        # If schema is one of the blacklisted schemas on this DB, do not add it (and delete it)
        blacklisted = delete_blacklisted_schema(db_session, schema_name, database)
        if not blacklisted and schema_name not in existing_schemas_names:
            schema = crud.db_schema.create(db=db_session, obj_in=schemas.DBSchemaCreate(name=schema_name, database_id=database.id))
            celery_app.send_task('tasks.celery_worker.fetch_db_schema_tree', args=[schema.id])

    db_session.flush()


@celery_app.task(acks_late=True)
def fetch_db_schema_tree(db_schema_id: int, force: bool = False):
    db_session = get_sessionmaker_instance(settings.SQLALCHEMY_DATABASE_URI)()
    db_schema = crud.db_schema.get(db=db_session, id=db_schema_id)
    database = db_schema.database
    engine_spec = engine_specs.get(database.type)

    engine = engine_spec.get_sqla_engine(
        hostname=db_schema.database.hostname, port=database.port, database=database.database,
        username=database.username, password=database.password
    )
    insp = inspect(engine)

    table_names = insp.get_table_names(schema=db_schema.name)

    # Fetch tables and save then into DQ db
    existing_tables = {t.name: t.id for t in db_schema.tables}
    for table_name in table_names:
        if table_name not in existing_tables.keys():
            table = crud.db_table.create(db=db_session, obj_in=schemas.DBTableCreate(name=table_name, schema_id=db_schema.id))
            celery_app.send_task('tasks.celery_worker.fetch_db_table_tree', args=[table.id])
        elif force:
            # If force, we will fetch columns for existing tables too
            celery_app.send_task('tasks.celery_worker.fetch_db_table_tree', args=[existing_tables[table_name]])

    db_session.flush()


@celery_app.task(acks_late=True)
def fetch_db_table_tree(db_table_id: int):
    db_session = get_sessionmaker_instance(settings.SQLALCHEMY_DATABASE_URI)()
    db_table = crud.db_table.get(db=db_session, id=db_table_id)
    database = db_table.schema.database
    engine_spec = engine_specs.get(database.type)

    engine = engine_spec.get_sqla_engine(
        hostname=db_table.schema.database.hostname, port=database.port, database=database.database,
        username=database.username, password=database.password
    )
    insp = engine_spec.get_inspector(engine)
    try:
        indexes = engine_spec.get_indexes(inspector=insp, table_name=db_table.name, schema_name=db_table.schema.name)
        print(indexes)
        # [{'name': 'partition', 'column_names': ['database', 'table', 'kf_date'], 'unique': False}]
        partition_columns = []
        for index in indexes:
            if index['name'] == 'partition':
                partition_columns = index['column_names']

        # If it's a partitioned table, launch task to fetch partition metadata
        if partition_columns:
            celery_app.send_task('tasks.celery_worker.fetch_db_table_partitions', args=[db_table_id])

        columns = engine_spec.get_columns(inspector=insp, table_name=db_table.name, schema_name=db_table.schema.name)
        existing_columns = [c.name for c in db_table.columns]
        for column in columns:

            # If the column doesn't exist already, then create it
            if column.get('name') not in existing_columns:
                crud.db_column.create(
                    db=db_session,
                    obj_in=schemas.DBColumnCreate(
                        name=column.get('name'),
                        type=str(column.get('type')),
                        table_id=db_table.id,
                        is_partition_column=column.get('name') in partition_columns
                    )
                )

            # If the column exists, update it
            else:
                db_column = crud.db_column.get(db=db_session, id=db_table.get_column(column.get('name')).id)
                db_column_in = schemas.DBColumnUpdate(**db_column.json())
                db_column_in.type = str(column.get('type'))
                db_column_in.is_partition_column = column.get('name') in partition_columns
                crud.db_column.update(
                    db=db_session,
                    db_obj=db_column,
                    obj_in=db_column_in
                )

        db_session.flush()
    except (sqlalchemy.exc.DatabaseError, pyhive.exc.DatabaseError, Exception) as e:
        print(e.__class__)
        print(e)


@celery_app.task(acks_late=True)
def fetch_db_table_partitions(db_table_id: int):
    db_session = get_sessionmaker_instance(settings.SQLALCHEMY_DATABASE_URI)()
    db_table = crud.db_table.get(db=db_session, id=db_table_id)
    database = db_table.schema.database
    engine_spec = engine_specs.get(database.type)

    engine = engine_spec.get_sqla_engine(
        hostname=db_table.schema.database.hostname, port=database.port, database=database.database,
        username=database.username, password=database.password
    )
    partitions_q = engine_spec.get_partitions_q_template().format(schema=db_table.schema.name, table=db_table.name)
    df = df_from_query(partitions_q, conn=engine)
    df['part'] = df.apply(lambda x: '/'.join([f'{c}={x[c]}' for c in df.columns]), axis=1)

    existing_partitions = [p.name for p in db_table.partitions]
    for part in df['part'].tolist():
        if part not in existing_partitions:
            crud.db_table_partition.create(
                db=db_session,
                obj_in=schemas.DBTablePartitionCreate(
                    name=part,
                    table_id=db_table_id
                )
            )
    db_session.flush()


@celery_app.task(acks_late=True)
def exec_check(check_id: int, partition_id: int = None):
    db_session = get_sessionmaker_instance(settings.SQLALCHEMY_DATABASE_URI)()
    check = crud.check.get(db=db_session, id=check_id)

    check.get_func()(check.id, partition_id)
