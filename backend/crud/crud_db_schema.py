from crud.base import CRUDBase
from models.db_schema import DBSchema
from schemas.db_schema import DBSchemaCreate, DBSchemaUpdate


class CRUDDBSchema(CRUDBase[DBSchema, DBSchemaCreate, DBSchemaUpdate]):
    pass


db_schema = CRUDDBSchema(DBSchema)
