import json
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

import crud
import schemas
from api import deps

router = APIRouter()


@router.get('/', response_model=List[schemas.CheckBaseWithLastExecution])
def read_check_base(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = None,
    filter: Optional[str] = '{}',
    sort: Optional[str] = None,
) -> Any:
    """
    Retrieve checks base (either `checks` or `custom checks`), including the id of the last check execution.
    """
    sort_list = None
    if sort:
        sort_list = json.loads(sort)
    filter_dict = json.loads(filter)
    checks = crud.check_base.get_all_with_last_execution(db=db, skip=skip, limit=limit, sort=sort_list, **filter_dict)
    response.headers['X-Content-Range'] = '{}-{}/{}'.format(skip, skip + (limit or 0), crud.check.count(db=db))
    return checks
