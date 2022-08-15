from typing import List, Any, Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

import crud
import schemas
from api import deps
from services import DBColumnService

router = APIRouter()


@router.get('/', response_model=List[schemas.DBColumnInDB])
def read_db_columns(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    filter: Optional[str] = '{}',
    sort: Optional[str] = None,
) -> Any:
    """
    Retrieves all columns that pass the filter (normally admin will filter by schema id and table id)
    """
    response.headers['X-Content-Range'] = '{}-{}/{}'.format(skip, skip + (limit or 0), crud.db_column.count(db=db))
    return DBColumnService(db).get_columns(skip=skip, limit=limit, sort=sort, filter=filter)


@router.get('/{id}', response_model=schemas.DBColumnInDB)
def read_db_column_detail(
    id: int,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Retrieve single column data
    """
    return DBColumnService(db).get(id=id)
