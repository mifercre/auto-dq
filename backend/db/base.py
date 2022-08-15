# Import all the models, so that Base has them before being
# imported by Alembic
from db.base_class import Base  # noqa
from models.check_base import CheckBase # noqa
from models.check import Check # noqa
from models.custom_check import CustomCheck # noqa
from models.check_execution import CheckExecution # noqa
from models.db import DB # noqa
from models.db_schema import DBSchema # noqa
from models.db_table import DBTable # noqa
from models.db_column import DBColumn # noqa
from models.db_table_partition import DBTablePartition # noqa
