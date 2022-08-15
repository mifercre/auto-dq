import json
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

import crud
import schemas
from api import deps
from scheduler import scheduler

router = APIRouter()


@router.get('/', response_model=List[schemas.CustomCheckWithLastExecution])
def read_checks(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = None,
    filter: Optional[str] = '{}',
    sort: Optional[str] = None,
) -> Any:
    """
    Retrieve custom checks, including the id of the last check execution.
    """
    sort_list = None
    if sort:
        sort_list = json.loads(sort)
    filter_dict = json.loads(filter)

    checks = crud.custom_check.get_all_with_last_execution(db=db, skip=skip, limit=limit, sort=sort_list, **filter_dict)
    response.headers['X-Content-Range'] = '{}-{}/{}'.format(skip, skip + (limit or 0), crud.custom_check.count(db=db))
    return checks


@router.get('/{id}', response_model=schemas.CustomCheckWithLastExecution)
def read_check_detail(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Retrieve single custom check with its executions.
    """
    return crud.custom_check.get_with_last_execution(db=db, id=id)


@router.post('/', response_model=schemas.CustomCheck)
def create_custom_check(
    *,
    db: Session = Depends(deps.get_db),
    check_in: schemas.CustomCheckCreate,
) -> Any:
    check = crud.custom_check.create(db=db, obj_in=check_in)
    scheduler.add_job(func=check.get_func(), id=check.name, cron=check.schedule, args=[check.id])
    if check.active:
        scheduler.resume_job(check.name)
    return check


@router.delete('/', response_model=List[schemas.CustomCheck])
def delete_check_filter(
    db: Session = Depends(deps.get_db),
    filter: Optional[str] = '{}',
) -> Any:
    """
    Delete all custom checks based on filter params (needed for admin multi-select delete)
    """
    deleted_checks = []
    filter_dict = json.loads(filter)
    filtered_checks = crud.custom_check.get_filtered(db=db, **filter_dict)
    for check in filtered_checks:
        check = crud.custom_check.remove(db=db, id=check.id)
        scheduler.remove_job(check.name)
        deleted_checks.append(check)
    return deleted_checks


@router.delete('/{id}', response_model=schemas.CustomCheck)
def delete_check(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Delete a custom check.
    """
    check = get_or_404(db=db, id=id)
    scheduler.remove_job(check.name)
    check = crud.custom_check.remove(db=db, id=id)
    return check


@router.put('/', response_model=List[schemas.CustomCheckInDB])
def edit_multiple_check(
    *,
    db: Session = Depends(deps.get_db),
    filter: Optional[str] = '{}',
    check_in: schemas.CustomCheckUpdateMultiple,
    skip: int = 0,
    limit: int = None,
) -> Any:
    """
    Update all custom checks that pass the filter (needed for admin multi-select enable/disable button)
    """
    filter_dict = json.loads(filter)
    filtered_checks = crud.custom_check.get_filtered(db=db, skip=skip, limit=limit, **filter_dict)
    for check in filtered_checks:
        check_data = check.json()
        c_schema = schemas.CustomCheckUpdate(**check_data)
        c_schema.active = check_in.active

        crud.custom_check.update(db=db, db_obj=check, obj_in=c_schema)
        job_exists = scheduler.get_job(check.name)
        if c_schema.active:
            if not job_exists:
                scheduler.add_job(func=check.get_func(), id=check.name, cron=check.schedule, args=[check.id])
            scheduler.resume_job(check.name)
        elif job_exists:
            scheduler.pause_job(check.name)

    return filtered_checks


@router.put('/{id}', response_model=schemas.CustomCheckWithLastExecution)
def edit_check(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    check_in: schemas.CustomCheckUpdate,
) -> Any:
    """
    Edit single custom check properties
    """
    check = get_or_404(db=db, id=id)
    needs_reeschedule = check_in.schedule != check.schedule
    check = crud.custom_check.update(db=db, db_obj=check, obj_in=check_in)

    if not scheduler.get_job(check.name):
        scheduler.add_job(func=check.get_func(), id=check.name, cron=check.schedule, args=[check.id])
    if needs_reeschedule:
        scheduler.reschedule_job(id=check.name, cron=check.schedule)
    if check.active:
        scheduler.resume_job(check.name)
    else:
        scheduler.pause_job(check.name)

    return crud.custom_check.get_with_last_execution(db=db, id=id)


@router.put('/stop/{id}', response_model=schemas.CustomCheck)
def stop_check(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Stops a custom check.
    """
    check = get_or_404(db=db, id=id)
    check_data = jsonable_encoder(check)
    check_in = schemas.CustomCheckUpdate(**check_data)
    check_in.active = False

    check = crud.custom_check.update(db=db, db_obj=check, obj_in=check_in)
    scheduler.pause_job(check.name)
    return check


@router.put('/activate/{id}', response_model=schemas.CustomCheck)
def activate_check(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Activates a custom check.
    """
    check = get_or_404(db=db, id=id)
    check_data = jsonable_encoder(check)
    check_in = schemas.CustomCheckUpdate(**check_data)
    check_in.active = True

    check = crud.custom_check.update(db=db, db_obj=check, obj_in=check_in)
    if not scheduler.get_job(check.name):
        scheduler.add_job(func=check.get_func(), id=check.name, cron=check.schedule, args=[check.id])
    scheduler.resume_job(check.name)
    return check


@router.post('/trigger/{id}', response_model=schemas.CustomCheck)
def trigger_check_by_id(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Trigger a custom check.
    """
    check = get_or_404(db=db, id=id)
    check.get_func()(check.id)
    return check


def get_or_404(db, id):
    check = crud.custom_check.get(db=db, id=id)
    if not check:
        raise HTTPException(status_code=404, detail='Check not found')
    return check
