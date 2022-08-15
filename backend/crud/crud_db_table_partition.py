from crud.base import CRUDBase
from models.db_table_partition import DBTablePartition
from schemas.db_table_partition import DBTablePartitionCreate, DBTablePartitionUpdate


class CRUDDBTablePartition(CRUDBase[DBTablePartition, DBTablePartitionCreate, DBTablePartitionUpdate]):
    pass


db_table_partition = CRUDDBTablePartition(DBTablePartition)
