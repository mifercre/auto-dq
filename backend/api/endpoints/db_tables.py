from typing import List, Any, Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

import crud
import schemas
from api import deps
from services import DBTableService

router = APIRouter()


@router.get('/', response_model=List[schemas.DBTableInDB])
def read_db_tables(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    filter: Optional[str] = '{}',
    sort: Optional[str] = None,
) -> Any:
    """
    Retrieve all tables
    """
    response.headers['X-Content-Range'] = '{}-{}/{}'.format(skip, skip + (limit or 0), crud.db_table.count(db=db))
    return DBTableService(db).get_tables(skip=skip, limit=limit, sort=sort, filter=filter)


@router.get('/{id}', response_model=schemas.DBTableInDB)
def read_db_table_detail(
    id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Retrieve single table
    """
    return crud.db_table.get(db, id=id)


@router.post('/refresh/{id}', response_model=schemas.DBTable)
def refresh_db_table(
    *,
    db: Session = Depends(deps.get_db),
    id: int
) -> Any:
    """
    Launches an async task to refresh the table metadata
    """
    return DBTableService(db).trigger_fetch_table_tree(id)


@router.post('/trigger_checks/{id}', response_model=List[schemas.Check])
def trigger_checks(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    partitions: Optional[List[int]] = [],
) -> Any:
    """
    Trigger all checks for the given table
    """
    return DBTableService(db).trigger_checks(id=id)
