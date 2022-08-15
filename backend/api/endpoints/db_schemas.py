import crud
import json
from typing import List, Any, Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

import schemas
from api import deps
from celery_app import celery_app

router = APIRouter()


@router.get('/', response_model=List[schemas.DBSchemaInDB])
def read_all_schemas(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    filter: Optional[str] = '{}',
    sort: Optional[str] = None,
) -> Any:
    """
    Retrieve all schemas
    """
    sort_list = None
    if sort:
        sort_list = json.loads(sort)
    filter_dict = json.loads(filter)

    db_schemas = crud.db_schema.get_filtered(db=db, skip=skip, limit=limit, sort=sort_list, **filter_dict)
    response.headers['X-Content-Range'] = '{}-{}/{}'.format(skip, skip + (limit or 0), crud.db_schema.count(db=db))
    return db_schemas


@router.get('/{id}', response_model=schemas.DBSchemaInDB)
def read_db_schema_detail(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Retrieve a single schema, the count of tables in the schema and the count of tables with checks.
    (used for the 'checks coverage' pie chart in the admin)
    """
    db_schema = crud.db_schema.get(db=db, id=id)

    unique_tables_with_checks = set()
    schema_checks = crud.check.get_filtered(db=db, schema_id=id)
    for x in schema_checks:
        unique_tables_with_checks.add(x.table.name)

    return schemas.DBSchemaInDB(
        id=db_schema.id, name=db_schema.name, database_id=db_schema.database_id, table_count=len(db_schema.tables),
        tables_with_checks=len(list(unique_tables_with_checks))
    )


@router.post('/refresh/{id}', response_model=schemas.DBSchema)
def refresh_db_schema(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    force: bool = False
) -> Any:
    """
    Launches an async task to refresh the schema metadata tree (tables and columns inside this schema)
    """
    db_schema = crud.db_schema.get(db=db, id=id)
    celery_app.send_task('tasks.celery_worker.fetch_db_schema_tree', args=[db_schema.id, force])
    return db_schema
