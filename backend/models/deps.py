import pandas as pd

from pyhive.exc import DatabaseError


def df_from_query(q, conn, retries=5):
    trial = 1
    while trial <= retries:
        try:
            return pd.read_sql_query(q, conn)
        except DatabaseError as e:
            print(e)
            trial += 1
    return ValueError(f'No result after {trial} retries')
