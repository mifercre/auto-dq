import json
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

import crud
import schemas
from api import deps
from models import CheckExecutionStatus

router = APIRouter()


@router.get('/', response_model=List[schemas.CheckExecutionWithCheckName])
def read_check_executions(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = None,
    filter: Optional[str] = '{}',
    sort: Optional[str] = None,
) -> Any:
    """
    Retrieve all check executions by default or use filters if needed
    """
    sort_list = None
    if sort:
        sort_list = json.loads(sort)
    filter_dict = json.loads(filter)
    executions = crud.check_execution.get_all(db=db, skip=skip, limit=limit, sort=sort_list, **filter_dict)
    response.headers['X-Content-Range'] = '{}-{}/{}'.format(skip, skip + (limit or 0), crud.check_execution.count(db=db, **filter_dict))
    return executions


@router.get('/count', response_model=schemas.Stats)
def count(
    db: Session = Depends(deps.get_db),
    filter: Optional[str] = '{}',
) -> Any:
    """
    Get filtered count of check executions
    """
    return schemas.Stats(meta={'fields': ['count']}, data=[crud.check_execution.count(db=db, **json.loads(filter))])


@router.get('/stats', response_model=schemas.Stats)
def count(
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Get stats for all check executions. Total count of executions and count of successful executions.
    """
    q = crud.check_execution.stats(db=db)
    return schemas.Stats(meta={'fields': [d['name'] for d in q.column_descriptions]}, data=q.all())


@router.get('/{id}', response_model=schemas.CheckExecutionWithLogs)
def read_check_detail(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Retrieve single check execution with logs
    """
    return crud.check_execution.get_with_logs(db=db, id=id)


@router.put('/success/{id}', response_model=schemas.CheckExecution)
def success_check_execution(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Set a given check execution status as success.
    """
    check_exec = crud.check_execution.get(db=db, id=id)
    if not check_exec:
        raise HTTPException(status_code=404, detail='Check not found')

    check_exec_data = check_exec.json()
    check_exec_in = schemas.CheckExecutionUpdate(**check_exec_data)
    check_exec_in.status = CheckExecutionStatus.SUCCESS.value
    check_exec = crud.check_execution.update(db=db, db_obj=check_exec, obj_in=check_exec_in)
    return check_exec
