from typing import Optional, List
from pydantic import BaseModel
from schemas import CheckExecutionBase


class DBTablePartitionBase(BaseModel):
    name: str


class DBTablePartitionCreate(DBTablePartitionBase):
    table_id: int


class DBTablePartitionUpdate(DBTablePartitionBase):
    pass


class DBTablePartitionInDB(DBTablePartitionBase):
    id: int
    check_executions: Optional[List[CheckExecutionBase]]

    class Config:
        orm_mode = True
