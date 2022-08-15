from crud.base import CRUDBase
from models.db_table import DBTable
from schemas.db_table import DBTableCreate, DBTableUpdate


class CRUDDBTable(CRUDBase[DBTable, DBTableCreate, DBTableUpdate]):
    pass


db_table = CRUDDBTable(DBTable)
