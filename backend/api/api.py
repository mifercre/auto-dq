from fastapi import APIRouter
from api.endpoints import check_base, checks, custom_checks, check_executions, dbs, db_schemas, db_tables, \
    db_columns, db_table_partitions

api_router_admin = APIRouter()
api_router_admin.include_router(check_base.router, prefix='/checks_base', tags=['checks_base'])
api_router_admin.include_router(checks.router, prefix='/checks', tags=['checks'])
api_router_admin.include_router(custom_checks.router, prefix='/custom_checks', tags=['custom_checks'])
api_router_admin.include_router(check_executions.router, prefix='/check_executions', tags=['check_executions'])
api_router_admin.include_router(dbs.router, prefix='/dbs', tags=['dbs'])
api_router_admin.include_router(db_schemas.router, prefix='/db_schemas', tags=['db_schemas'])
api_router_admin.include_router(db_tables.router, prefix='/db_tables', tags=['db_tables'])
api_router_admin.include_router(db_columns.router, prefix='/db_columns', tags=['db_columns'])
api_router_admin.include_router(db_table_partitions.router, prefix='/db_table_partitions', tags=['db_table_partitions'])
