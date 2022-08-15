from typing import List, Any, Optional

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

import json
import crud
import schemas
from api import deps

router = APIRouter()


@router.get('/', response_model=List[schemas.DBTablePartitionInDB])
def read_db_table_partitions(
    response: Response,
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    filter: Optional[str] = '{}',
    sort: Optional[str] = None,
) -> Any:
    """
    Retrieve table partition metadata
    """
    sort_list = None
    if sort:
        sort_list = json.loads(sort)
    filter_dict = json.loads(filter)

    partitions = crud.db_table_partition.get_filtered(db=db, skip=skip, limit=limit, sort=sort_list, **filter_dict)
    res = [
        schemas.DBTablePartitionInDB(
            id=p.id,
            name=p.name,
            check_executions=[c.json() for c in p.check_executions] if p.check_executions else None)
        for p in partitions
    ]
    response.headers['X-Content-Range'] = '{}-{}/{}'.format(skip, skip + (limit or 0), crud.db_table_partition.count(db=db))
    return res
