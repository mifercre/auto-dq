import json
from fastapi import HTTPException

from celery_app import celery_app
from crud import db_table
from services.base import BaseService


class DBTableService(BaseService):

    def get_tables(self, skip, limit, sort, filter):
        sort_list = None
        if sort:
            sort_list = json.loads(sort)
        filter_dict = json.loads(filter)

        return db_table.get_filtered(db=self.db, skip=skip, limit=limit, sort=sort_list, **filter_dict)

    def trigger_checks(self, id):
        table = db_table.get(db=self.db, id=id)
        if not table:
            raise HTTPException(status_code=404, detail='DBTable not found')

        for check in db_table.checks:
            celery_app.send_task('tasks.celery_worker.exec_check', args=[check.id])

        return db_table.checks

    def trigger_fetch_table_tree(self, id):
        table = db_table.get(db=self.db, id=id)
        celery_app.send_task('tasks.celery_worker.fetch_db_table_tree', args=[table.id])
        return table
