from typing import Optional
from pydantic import BaseModel


class DBColumnBase(BaseModel):
    name: str
    type: Optional[str]
    is_partition_column: Optional[bool]

    class Config:
        orm_mode = True


class DBColumnCreate(DBColumnBase):
    table_id: int
    is_partition_column: bool


class DBColumnUpdate(DBColumnBase):
    pass


class DBColumnInDBBase(DBColumnBase):
    pass


class DBColumn(DBColumnInDBBase):
    pass


class DBColumnInDB(DBColumnInDBBase):
    id: int
