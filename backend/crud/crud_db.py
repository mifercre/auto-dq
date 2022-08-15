from crud.base import CRUDBase
from models.db import DB
from schemas.db import DBCreateInternal, DBUpdate


class CRUDDB(CRUDBase[DB, DBCreateInternal, DBUpdate]):
    pass


db = CRUDDB(DB)
