import json
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

import crud
import schemas
from api import deps
from models.check import CheckType
from scheduler import scheduler
from utils import logger, get_random_daily_cron

router = APIRouter()


@router.get('/', response_model=List[schemas.CheckWithLastExecution])
def read_checks(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = None,
    filter: Optional[str] = '{}',
    sort: Optional[str] = None,
) -> Any:
    """
    Retrieve checks, including the id of the last check execution.
    """
    sort_list = None
    if sort:
        sort_list = json.loads(sort)
    filter_dict = json.loads(filter)
    checks = crud.check.get_all_with_last_execution(db=db, skip=skip, limit=limit, sort=sort_list, **filter_dict)
    response.headers['X-Content-Range'] = '{}-{}/{}'.format(skip, skip + (limit or 0), crud.check.count(db=db))
    return checks


@router.get('/{id}', response_model=schemas.CheckWithLastExecution)
def read_check_detail(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Retrieve single check with all its executions.
    """
    return crud.check.get_with_last_execution(db=db, id=id)


@router.delete('/delete_all_checks', response_model=schemas.Check)
def delete_all_checks(
    *,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Delete all checks.
    """
    checks = crud.check.get_all(db=db)
    for check in checks:
        crud.check.remove(db=db, id=check.id)

    scheduler.remove_all_jobs()
    return 'All deleted'


@router.delete('/', response_model=List[schemas.Check])
def delete_check_filter(
    db: Session = Depends(deps.get_db),
    filter: Optional[str] = '{}',
) -> Any:
    """
    Delete all checks based on filter params (needed for admin multi-select delete)
    """
    deleted_checks = []
    filter_dict = json.loads(filter)
    filtered_checks = crud.check.get_filtered(db=db, **filter_dict)
    for check in filtered_checks:
        check = crud.check.remove(db=db, id=check.id)
        scheduler.remove_job(check.name)
        deleted_checks.append(check)
    return deleted_checks


@router.delete('/{id}', response_model=schemas.Check)
def delete_check(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Delete a single check.
    """
    check = get_or_404(db=db, id=id)
    scheduler.remove_job(check.name)
    check = crud.check.remove(db=db, id=id)
    return check


@router.put('/', response_model=List[schemas.CheckInDB])
def edit_multiple_check(
    *,
    db: Session = Depends(deps.get_db),
    filter: Optional[str] = '{}',
    check_in: schemas.CheckUpdateMultiple,
    skip: int = 0,
    limit: int = None,
) -> Any:
    """
    Update all checks that pass the filter (needed for admin multi-select enable/disable button)
    """
    filter_dict = json.loads(filter)
    filtered_checks = crud.check.get_filtered(db=db, skip=skip, limit=limit, **filter_dict)
    for check in filtered_checks:
        check_data = check.json()
        c_schema = schemas.CheckUpdate(**check_data)
        c_schema.active = check_in.active

        crud.check.update(db=db, db_obj=check, obj_in=c_schema)
        job_exists = scheduler.get_job(check.name)
        if c_schema.active:
            if not job_exists:
                scheduler.add_job(func=check.get_func(), id=check.name, cron=check.schedule, args=[check.id])
            scheduler.resume_job(check.name)
        elif job_exists:
            scheduler.pause_job(check.name)

    return filtered_checks


@router.put('/{id}', response_model=schemas.CheckWithLastExecution)
def edit_check(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    check_in: schemas.CheckUpdate,
) -> Any:
    """
    Edit single check properties
    """
    check = get_or_404(db=db, id=id)
    needs_reeschedule = check_in.schedule != check.schedule
    check = crud.check.update(db=db, db_obj=check, obj_in=check_in)

    if not scheduler.get_job(check.name):
        scheduler.add_job(func=check.get_func(), id=check.name, cron=check.schedule, args=[check.id])
    if needs_reeschedule:
        scheduler.reschedule_job(id=check.name, cron=check.schedule)
    if check.active:
        scheduler.resume_job(check.name)
    else:
        scheduler.pause_job(check.name)

    return crud.check.get_with_last_execution(db=db, id=id)


@router.put('/stop/{id}', response_model=schemas.Check)
def stop_check(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Stops a check (it won't be launched by the scheduler anymore).
    """
    check = get_or_404(db=db, id=id)
    check_data = jsonable_encoder(check)
    check_in = schemas.CheckUpdate(**check_data)
    check_in.active = False

    check = crud.check.update(db=db, db_obj=check, obj_in=check_in)
    scheduler.pause_job(check.name)
    return check


@router.put('/activate/{id}', response_model=schemas.Check)
def activate_check(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Activates a check.
    """
    check = get_or_404(db=db, id=id)
    check_data = jsonable_encoder(check)
    check_in = schemas.CheckUpdate(**check_data)
    check_in.active = True

    check = crud.check.update(db=db, db_obj=check, obj_in=check_in)
    scheduler.resume_job(check.name)
    return check


@router.post('/trigger/{id}', response_model=schemas.Check)
def trigger_check_by_id(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Trigger a check (skips the scheduler and simply launches the check right now).
    """
    check = get_or_404(db=db, id=id)
    check.get_func()(check.id)
    return check


@router.post('/', response_model=schemas.Check)
def create_check(
    *,
    db: Session = Depends(deps.get_db),
    check_in: schemas.CheckCreate,
) -> Any:
    """
    Creates a new check (used by the admin create check form)
    """
    exists = crud.check.get_filtered(db=db, name=check_in.name)
    if exists:
        logger.debug(f'Check already exists: {exists}')
        return exists[0]

    check = crud.check.create(db=db, obj_in=check_in)
    scheduler.add_job(func=check.get_func(), id=check.name, cron=check.schedule, args=[check.id])
    if check.active:
        scheduler.resume_job(check.name)
    return check


def auto_create_check(db, params, check_type):
    params_json = json.loads(params)
    logger.debug(params_json)
    check = None

    if 'column_id' in params_json:
        column = crud.db_column.get(db=db, id=params_json['column_id'])
        table = column.table

        new_check_name = f'{table.schema.database.name}_{table.schema.name}_{table.name}_{column.name}_{check_type}_auto'
        exists = crud.check.get_filtered(db=db, table_id=table.id, name=new_check_name)
        if exists:
            logger.debug(f'Check already exists: {exists}')
            return exists[0]
        else:
            check_in = schemas.CheckCreate(
                name=new_check_name,
                schedule=get_random_daily_cron(),
                type=check_type,
                active=True,
                database_id=table.schema.database_id,
                schema_id=table.schema.id,
                table_id=table.id,
                column_id=column.id
            )
            logger.debug(check_in)
            check = crud.check.create(db=db, obj_in=check_in)
            scheduler.add_job(func=check.get_func(), id=check.name, cron=check.schedule, args=[check.id])
            scheduler.resume_job(check.name)

    return check


@router.post('/uniqueness/auto', response_model=schemas.Check)
def create_uniqueness_check_auto(
    *,
    db: Session = Depends(deps.get_db),
    params: str,
) -> Any:
    """
    Create new Uniqueness check for a given column ID.
    """
    return auto_create_check(db, params, CheckType.UNIQUENESS)


@router.post('/non_null/auto', response_model=schemas.Check)
def create_non_null_check_auto(
    *,
    db: Session = Depends(deps.get_db),
    params: str,
) -> Any:
    """
    Create new Non-null check for a given column ID.
    """
    return auto_create_check(db, params, CheckType.NON_NULL)


@router.post('/ordered/auto', response_model=schemas.Check)
def create_ordered_check(
    *,
    db: Session = Depends(deps.get_db),
    params: str,
) -> Any:
    """
    Create new Ordered check for a given column.
    """
    return auto_create_check(db, params, CheckType.ORDERED)


@router.post('/outliers/auto', response_model=schemas.Check)
def create_outliers_check_auto(
        *,
        db: Session = Depends(deps.get_db),
        params: str,
) -> Any:
    """
    Create new Outliers check for a given column.
    """
    return auto_create_check(db, params, CheckType.OUTLIERS)


def get_or_404(db, id):
    check = crud.check.get(db=db, id=id)
    if not check:
        raise HTTPException(status_code=404, detail='Check not found')
    return check
