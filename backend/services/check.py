from typing import Tuple, Dict

from models.check import CheckType
from services.base import BaseService

from core.db_engines import engine_specs

OUTLIER_METRIC_NAME = 'count'
ORDERED_METRIC_NAME = 'count'


class CheckService(BaseService):

    def get_query(self, check, cursor=None) -> Tuple[str, Dict]:
        # TODO: need to have some better logic that handles:
        #  - (done) different databases (the db engine should dictate the check syntax in it's own class, not here)
        #  - different check types
        #  - individual column vs table checks
        #  - running for latest partition
        #  - running for old partitions on-demand

        engine_spec = engine_specs.get(check.database.type)

        q = 'SELECT 1'
        if check.type == CheckType.UNIQUENESS:
            q = engine_spec.unique_column_q_template(check=check, cursor=cursor)
        if check.type == CheckType.NON_NULL:
            q = engine_spec.non_null_column_q_template(check=check, cursor=cursor)
        if check.type == CheckType.OUTLIERS:
            q = engine_spec.outlier_column_q_template(check=check, cursor=cursor)
        elif check.type == CheckType.FRESHNESS:
            q = engine_spec.freshness_column_q_template(check=check, cursor=cursor)
        elif check.type == CheckType.ORDERED:
            q = engine_spec.ordered_table_q_template(check=check, cursor=cursor)

        return q, {'schema': check.schema.name, 'table': check.table.name, 'column_to_check': check.column.name}
