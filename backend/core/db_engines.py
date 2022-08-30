import re
import warnings
from builtins import sorted
from typing import Dict

from psycopg2 import sql
from sqlalchemy import inspect
from sqlalchemy.engine import create_engine

from tasks.utils import required_args


class BaseEngineSpec:

    def get_sqla_engine(self, hostname: str, port: int, database: str, username: str = None, password: str = None):
        raise NotImplementedError()

    @staticmethod
    def get_schema_names(inspector):
        return sorted(inspector.get_schema_names())

    @staticmethod
    def get_table_names(inspector, schema):
        tables = inspector.get_table_names(schema)
        return sorted(tables)

    @staticmethod
    def get_inspector(engine):
        return inspect(engine)

    @staticmethod
    def get_indexes(inspector, schema_name: str, table_name: str):
        return inspector.get_indexes(table_name=table_name, schema=schema_name)

    @staticmethod
    def get_columns(inspector, schema_name: str, table_name: str):
        return inspector.get_columns(table_name, schema=schema_name)

    def ordered_table_q_template(self, *args, **kwargs):
        return """
            SELECT ":column_to_check" 
            FROM ":schema".":table" 
            GROUP BY 1 ORDER BY 1 ASC
        """

    def unique_column_q_template(self, *args, **kwargs):
        return """
            SELECT ":column_to_check"
            FROM ":schema".":table" 
        """

    def freshness_column_q_template(self, *args, **kwargs):
        return """
            SELECT MAX(":column_to_check") AS column_to_check
            FROM ":schema".":table" 
        """

    def get_partitions_q_template(self, *args, **kwargs):
        return NotImplementedError()

    def partition_exists_q_template(self, *args, **kwargs):
        raise NotImplementedError()

    def outlier_table_q_template(self, *args, **kwargs):
        raise NotImplementedError()

    def outlier_column_q_template(self, *args, **kwargs):
        raise NotImplementedError()

    def non_null_column_q_template(self, *args, **kwargs):
        raise NotImplementedError()


class PrestoEngineSpec(BaseEngineSpec):
    """
    We use SQLAlchemy with PyHive to connect to presto, query parametrization of schema, table and column names is not
    supported so we default to python format instead.
    """
    engine = 'presto'

    def get_sqla_engine(self, hostname: str, port: int, database: str, username: str = None, password: str = None):
        return create_engine(f'presto://{username or "dq-default"}@{hostname}:{port}/{database}/default')

    @staticmethod
    def get_columns(inspector, schema_name: str, table_name: str):

        # PyHive doesn't support Presto struct columns ATM, so here we catch those warnings and fix the data types
        with warnings.catch_warnings(record=True) as warns:
            warnings.simplefilter('always')
            columns = inspector.get_columns(table_name, schema=schema_name)

            warn_dict = {}
            if len(warns) > 0:
                for w in warns:
                    print(w.message)
                    column_search = re.search("^did not recognize type '(.*)' of column '(.*)'$", str(w.message), re.IGNORECASE)

                    if column_search:
                        warn_dict[column_search.group(2)] = column_search.group(1).replace('row(', 'STRUCT(')

            for c in columns:
                if c.get('name') in warn_dict.keys():
                    c['type'] = warn_dict.get(c.get('name'))

        return columns

    @staticmethod
    def _plain_select_column_q(check):
        return """
            SELECT "{column_to_check}"
            FROM "{schema}"."{table}" 
        """.format(schema=check.schema.name, table=check.table.name, column_to_check=check.column.name)

    @required_args(['check'])
    def unique_column_q_template(self, check):
        return self._plain_select_column_q(check)

    @required_args(['check'])
    def outlier_column_q_template(self, check):
        return self._plain_select_column_q(check)

    @required_args(['check'])
    def non_null_column_q_template(self, check):
        return self._plain_select_column_q(check)

    def get_partitions_q_template(self):
        return """
            SELECT * FROM "{schema}"."{table}$partitions"
        """

    def partition_exists_q_template(self):
        return """
            SELECT * 
            FROM "{schema}"."{table}$partitions" 
            WHERE "{partition_column}" = '{partition_value}'
        """


class PostgresEngineSpec(BaseEngineSpec):
    """
    We are using SQLAlchemy with psycopg2 to connect to Postgres backends. Schema, table and column names cannot be
    parametrized directly, instead we need to rely on psycopg2.sql module to dynamically format this fields and return
    the query template already formatted.
    """
    engine = 'postgresql'

    def get_sqla_engine(self, hostname, port, database, username=None, password=None):
        return create_engine(f'postgresql://{username}:{password}@{hostname}:{port}/{database}')

    def get_table_names(self, inspector, schema):
        tables = inspector.get_table_names(schema)
        tables.extend(inspector.get_foreign_table_names(schema))
        return sorted(tables)

    @staticmethod
    def _plain_select_column_q(check, cursor):
        return sql.SQL("""
            SELECT {column_to_check} 
            FROM {schema}.{table} 
        """).format(
            schema=sql.Identifier(check.schema.name),
            table=sql.Identifier(check.table.name),
            column_to_check=sql.Identifier(check.column.name)
        ).as_string(cursor)

    @required_args(['check', 'cursor'])
    def unique_column_q_template(self, check, cursor):
        return self._plain_select_column_q(check, cursor)

    @required_args(['check', 'cursor'])
    def outlier_column_q_template(self, check, cursor):
        return self._plain_select_column_q(check, cursor)

    @required_args(['check', 'cursor'])
    def non_null_column_q_template(self, check, cursor):
        return self._plain_select_column_q(check, cursor)

    @required_args(['check', 'cursor'])
    def ordered_table_q_template(self, check, cursor):
        return sql.SQL("""
            SELECT {column_to_check} 
            FROM {schema}.{table} 
            GROUP BY 1 ORDER BY 1 ASC
        """).format(
            schema=sql.Identifier(check.schema.name),
            table=sql.Identifier(check.table.name),
            column_to_check=sql.Identifier(check.column.name)
        ).as_string(cursor)

    @required_args(['check', 'cursor'])
    def freshness_column_q_template(self, check, cursor):
        return sql.SQL("""
            SELECT MAX({column_to_check}) AS column_to_check
            FROM {schema}.{table} 
        """).format(
            schema=sql.Identifier(check.schema.name),
            table=sql.Identifier(check.table.name),
            column_to_check=sql.Identifier(check.column.name)
        ).as_string(cursor)


class MysqlEngineSpec(BaseEngineSpec):
    """
    Use back ticks (`) instead of double quotes to escape columns, tables and schemas.
    """
    engine = 'mysql'

    def get_sqla_engine(self, hostname, port, database, username=None, password=None):
        return create_engine(f'mysql://{username}:{password}@{hostname}:{port}/{database}')

    def get_table_names(self, inspector, schema):
        tables = inspector.get_table_names(schema)
        tables.extend(inspector.get_foreign_table_names(schema))
        return sorted(tables)

    @staticmethod
    def _plain_select_column_q(check):
        return f"""
            SELECT `{check.column.name}` 
            FROM `{check.schema.name}`.`{check.table.name}`
        """

    @required_args(['check'])
    def unique_column_q_template(self, check):
        return self._plain_select_column_q(check)

    @required_args(['check'])
    def outlier_column_q_template(self, check):
        return self._plain_select_column_q(check)

    @required_args(['check'])
    def non_null_column_q_template(self, check):
        return self._plain_select_column_q(check)

    @required_args(['check'])
    def freshness_column_q_template(self, check):
        return f"""
            SELECT MAX(`{check.column.name}`) AS column_to_check
            FROM `{check.schema.name}`.`{check.table.name}` 
        """

    @required_args(['check'])
    def ordered_table_q_template(self, check):
        return f"""
            SELECT `{check.column.name}` 
            FROM `{check.schema.name}`.`{check.table.name}`
            GROUP BY 1 ORDER BY 1 ASC
        """


engine_specs: Dict[str, BaseEngineSpec] = {
    'presto': PrestoEngineSpec(),
    'postgresql': PostgresEngineSpec(),
    'mysql': MysqlEngineSpec()
}
