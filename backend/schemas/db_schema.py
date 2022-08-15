from typing import Optional, List
from pydantic import BaseModel
from schemas.db_table import DBTableInDB


class DBSchemaBase(BaseModel):
    name: str
    database_id: int

    class Config:
        orm_mode = True


class DBSchemaCreate(DBSchemaBase):
    database_id: int


class DBSchemaUpdate(DBSchemaBase):
    pass


class DBSchemaInDBBase(DBSchemaBase):
    pass


class DBSchema(DBSchemaInDBBase):
    pass


class DBSchemaInDB(DBSchemaInDBBase):
    id: int
    table_count: Optional[int]
    tables_with_checks: Optional[int]


class DBSchemaWithTables(DBSchemaBase):
    id: int
    tables: List[DBTableInDB]
