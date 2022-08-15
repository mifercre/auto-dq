from typing import Optional, List
from pydantic import BaseModel
from schemas.db_column import DBColumnInDB


class DBTableBase(BaseModel):
    name: str
    schema_id: int


class DBTableCreate(DBTableBase):
    schema_id: int


class DBTableUpdate(DBTableBase):
    pass


class DBTableInDBBase(DBTableBase):

    class Config:
        orm_mode = True


class DBTable(DBTableInDBBase):
    pass


class DBTableInDB(DBTableInDBBase):
    id: int
    has_partition_column: Optional[bool]


class DBTableWithColumns(DBTableBase):
    id: int
    columns: List[DBColumnInDB]
