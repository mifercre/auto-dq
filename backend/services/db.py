import crud
import schemas
from celery_app import celery_app
from core.db_engines import engine_specs
from services.base import BaseService
from utils import logger


class DBService(BaseService):

    def create_db(self, db_in):
        engine_spec = engine_specs.get(db_in.type)
        engine = engine_spec.get_sqla_engine(
            hostname=db_in.hostname, port=db_in.port, database=db_in.database, username=db_in.username,
            password=db_in.password
        )
        logger.debug(engine)

        db_in_internal = schemas.DBCreateInternal(
            name=db_in.name,
            type=db_in.type,
            hostname=db_in.hostname,
            port=db_in.port,
            database=db_in.database,
            username=db_in.username,
            password=db_in.password,
            blacklist=db_in.blacklist,
        )
        db_res = crud.db.create(db=self.db, obj_in=db_in_internal)
        return db_res

    @staticmethod
    def trigger_fetch_db_tree(db_id):
        celery_app.send_task('tasks.celery_worker.fetch_db_tree', args=[db_id])
