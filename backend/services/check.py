from models.check import CheckType
from services.base import BaseService


OUTLIER_METRIC_NAME = 'count'
ORDERED_METRIC_NAME = 'count'


class CheckService(BaseService):

    def get_query(self, check):
        # TODO: need to have some better logic that handles:
        #  - different databases (the db engine should dictate the check syntax in it's own class, not here)
        #  - different check types
        #  - individual column vs table checks
        #  - running for latest partition
        #  - running for old partitions on-demand
        #  Also probably can use a more OOP solution
        q = 'SELECT 1'
        if check.type in [CheckType.UNIQUENESS, CheckType.NON_NULL, CheckType.OUTLIERS]:
            q = f"""
                SELECT "{check.column.name}"
                FROM "{check.schema.name}"."{check.table.name}"
            """
        elif check.type == CheckType.FRESHNESS:
            q = f"""
                SELECT MAX("{check.column.name}") AS "{check.column.name}"
                FROM "{check.schema.name}"."{check.table.name}"
            """
        elif check.type == CheckType.ORDERED:
            q = f"""
                SELECT "{check.column.name}" 
                FROM "{check.schema.name}"."{check.table.name}" 
                GROUP BY 1 ORDER BY 1 ASC
            """
        return q
