import json
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
import crud
import schemas
from api import deps
from celery_app import celery_app
from services.db import DBService
from utils import logger

router = APIRouter()


@router.get('/', response_model=List[schemas.DB])
def read_dbs(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve all DBs
    """
    dbs = crud.db.get_multi(db, skip=skip, limit=limit)
    response.headers['X-Content-Range'] = '{}-{}/{}'.format(skip, skip + (limit or 0), crud.db.count(db=db))
    return dbs


@router.get('/{id}', response_model=schemas.DB)
def read_db_detail(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Retrieve single DB
    """
    return crud.db.get(db=db, id=id)


@router.post('/', response_model=schemas.DB)
def create_db(
    *,
    db: Session = Depends(deps.get_db),
    db_in: schemas.DBCreate,
) -> Any:
    """
    Create new DB and start the DB tree metadata extraction
    """
    try:
        db_res = DBService(db).create_db(db_in)
        DBService.trigger_fetch_db_tree(db_res.id)
        return db_res
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=404, detail='Failed to connect to the given DB')


@router.delete('/', response_model=List[schemas.DB])
def delete_db_filter(
    db: Session = Depends(deps.get_db),
    filter: Optional[str] = '{}',
) -> Any:
    """
    Delete all checks based on filter params
    """
    deleted_dbs = []
    filter_dict = json.loads(filter)
    filtered_db = crud.db.get_filtered(db=db, **filter_dict)
    for db_ in filtered_db:
        db_del = crud.db.remove(db=db, id=db_.id)
        deleted_dbs.append(db_del)
    return deleted_dbs


@router.post('/refresh/{id}', response_model=schemas.DB)
def refresh_db(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    force: bool = False
) -> Any:
    """
    Launches an async task to refresh the DB tree metadata
    """
    db_ = get_or_404(db=db, id=id)
    celery_app.send_task('tasks.celery_worker.fetch_db_tree', args=[db_.id])
    return db_


@router.put('/{id}', response_model=schemas.DB)
def edit_db(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    db_in: schemas.DBUpdate,
) -> Any:
    db_ = get_or_404(db=db, id=id)
    return crud.db.update(db=db, db_obj=db_, obj_in=db_in)


@router.get('/{id}/test_conn', response_model=schemas.TestDBConn)
def test_conn(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Test connection to DB
    """
    db_ = get_or_404(db=db, id=id)
    try:
        db_.fetchone('SELECT 1')
        return schemas.TestDBConn(success=True)
    except OperationalError:
        return schemas.TestDBConn(success=False)


def get_or_404(db, id):
    db_ = crud.db.get(db=db, id=id)
    if not db_:
        raise HTTPException(status_code=404, detail='DB not found')
    return db_

