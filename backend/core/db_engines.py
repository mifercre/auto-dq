import re
import warnings
from builtins import sorted
from typing import Dict, Type

from sqlalchemy import inspect
from sqlalchemy.engine import create_engine


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

    def get_partitions_q_template(self):
        return NotImplementedError()

    def partition_exists_q_template(self):
        raise NotImplementedError()

    def outlier_table_q_template(self):
        raise NotImplementedError()

    def ordered_table_q_template(self):
        raise NotImplementedError()

    def outlier_column_q_template(self):
        raise NotImplementedError()

    def unique_column_q_template(self):
        raise NotImplementedError()

    def non_null_column_q_template(self):
        raise NotImplementedError()


class PrestoEngineSpec(BaseEngineSpec):
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

    def get_partitions_q_template(self):
        return """
            SELECT * FROM {schema}."{table}$partitions"
        """

    def partition_exists_q_template(self):
        return """
            SELECT * 
            FROM {schema}."{table}$partitions" 
            WHERE "{partition_column}" = '{partition_value}'
        """

    def outlier_table_q_template(self):
        return """
            SELECT {partition_column}, COUNT(*) AS cnt
            FROM {schema}.{table} 
            WHERE {partition_column} >= CAST(CURRENT_DATE - INTERVAL '20' DAY AS VARCHAR) AND {partition_column} < CAST(CURRENT_DATE AS VARCHAR)
            GROUP BY 1 ORDER BY 1
        """

    def outlier_column_q_template(self):
        return """
            SELECT {column_to_check}
            FROM {schema}.{table} 
            WHERE {partition_column} = CAST(CURRENT_DATE - INTERVAL '1' DAY AS VARCHAR)
        """

    def ordered_table_q_template(self):
        return """
            SELECT {partition_column}, COUNT(*) AS cnt
            FROM {schema}.{table} 
            WHERE {partition_column} >= CAST(CURRENT_DATE - INTERVAL '20' DAY AS VARCHAR) AND {partition_column} < CAST(CURRENT_DATE AS VARCHAR)
            GROUP BY 1 ORDER BY 1
        """

    def unique_column_q_template(self):
        return """
            SELECT {column_to_check}
            FROM {schema}.{table} 
            WHERE {partition_column} = CAST(CURRENT_DATE - INTERVAL '1' DAY AS VARCHAR)
        """

    def non_null_column_q_template(self):
        return """
            SELECT {column_to_check}
            FROM {schema}.{table} 
            WHERE {partition_column} = CAST(CURRENT_DATE - INTERVAL '1' DAY AS VARCHAR)
        """


class PostgresEngineSpec(BaseEngineSpec):
    engine = 'postgresql'

    def get_sqla_engine(self, hostname, port, database, username=None, password=None):
        return create_engine(f'postgresql://{username}:{password}@{hostname}:{port}/{database}')

    def get_table_names(self, inspector, schema):
        tables = inspector.get_table_names(schema)
        tables.extend(inspector.get_foreign_table_names(schema))
        return sorted(tables)

    def outlier_table_q_template(self):
        raise NotImplementedError()

    def outlier_column_q_template(self):
        raise NotImplementedError()

    def unique_column_q_template(self):
        raise NotImplementedError()

    def non_null_column_q_template(self):
        raise NotImplementedError()


engine_specs: Dict[str, Type[BaseEngineSpec]] = {'presto': PrestoEngineSpec(), 'postgresql': PostgresEngineSpec()}
