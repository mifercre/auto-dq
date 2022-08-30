from typing import Optional, List
from pydantic import BaseModel
from schemas.db_schema import DBSchemaInDB


class DBBase(BaseModel):
    name: Optional[str]
    type: Optional[str]
    hostname: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    blacklist: Optional[str] = None

    class Config:
        orm_mode = True


class DBCreate(DBBase):
    username: Optional[str] = None
    password: Optional[str] = None


class DBCreateInternal(DBBase):
    name: Optional[str]
    type: Optional[str]
    hostname: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    blacklist: Optional[str] = None


class DBUpdate(DBCreateInternal):
    pass


class DBInDBBase(DBBase):
    pass


class DB(DBInDBBase):
    id: int


class DBInDB(DBInDBBase):
    id: int


class DBWithSchemas(DBInDBBase):
    id: int
    schemas: List[DBSchemaInDB]


class TestDBConn(BaseModel):
    success: bool


class SupportedDBs(BaseModel):
    id: str
    type: str
