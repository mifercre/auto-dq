from crud.base import CRUDBase
from models.db_column import DBColumn
from schemas.db_column import DBColumnCreate, DBColumnUpdate


class CRUDDBColumn(CRUDBase[DBColumn, DBColumnCreate, DBColumnUpdate]):
    pass


db_column = CRUDDBColumn(DBColumn)
