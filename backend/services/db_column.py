import json

from crud import db_column
from services.base import BaseService


class DBColumnService(BaseService):

    def get_columns(self, skip, limit, sort, filter):
        sort_list = None
        if sort:
            sort_list = json.loads(sort)
        filter_dict = json.loads(filter)

        return db_column.get_filtered(db=self.db, skip=skip, limit=limit, sort=sort_list, **filter_dict)

    def get(self, id):
        return db_column.get(self.db, id=id)
