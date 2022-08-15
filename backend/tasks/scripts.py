import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
from sqlalchemy.orm import sessionmaker

import crud
import schemas
from db.session import engine
from models import CheckExecutionStatus
from models.deps import df_from_query
from services.check import CheckService
from tasks.alerts import send_mm_alert
from tasks.tail_logger import init_logger


def init_check_execution(check_id: int):
    Session = sessionmaker(bind=engine)
    session = Session()
    check_exec_in = schemas.CheckExecutionCreate(exec_time=datetime.now(), check_id=check_id)
    check_execution = crud.check_execution.create(db=session, obj_in=check_exec_in)

    logger, tail = init_logger(check_execution.id)

    return session, check_execution, logger, tail


def uniqueness(check_id: int):
    """
    Checks that there are no duplicates in all values.
    """
    session, check_execution, logger, tail = init_check_execution(check_id)
    logger.debug('uniqueness check_id: {}'.format(check_id))

    try:
        check = crud.check.get(db=session, id=check_id)
        check_query = CheckService(session).get_query(check)
        logger.debug(check_query)

        df = df_from_query(check_query, conn=check.database.get_conn())
        logger.debug('Rows: {}'.format(df.shape[0]))
        logger.debug('Unique rows: {}'.format(df.drop_duplicates().shape[0]))

        # total rows equals unique rows
        status = CheckExecutionStatus.SUCCESS.value

        if df.shape[0] != df.drop_duplicates().shape[0]:
            logger.debug('Duplicated rows: {}'.format(df[df.duplicated()]))
            status = CheckExecutionStatus.FAIL.value
            send_mm_alert(check)

        check_execution.status = status
        check_execution.results = json.dumps({
                'total_rows': df.shape[0],
                'unique_rows': df.drop_duplicates().shape[0]
            })
        check_execution.logs = tail.contents()
        session.commit()
    except Exception as e:
        logger.debug(e)
        check_execution.status = CheckExecutionStatus.FAIL.value
        check_execution.logs = tail.contents()
        session.commit()


def outliers(check_id: int):
    """
    Checks that all values from the input source are within 3 standard deviations (i.e there are no outliers)
    """
    session, check_execution, logger, tail = init_check_execution(check_id)
    logger.debug('outliers check_id: {}'.format(check_id))

    try:
        check = crud.check.get(db=session, id=check_id)
        check_query = CheckService(session).get_query(check)
        logger.debug(check_query)

        df = df_from_query(check_query, conn=check.database.get_conn())
        df['is_outlier'] = np.abs(df[check.column.name] - df[check.column.name].mean()) > (3 * df[check.column.name].std())
        logger.debug('Rows with outliers: {}'.format(df[df['is_outlier']].shape[0]))
        status = CheckExecutionStatus.SUCCESS.value

        if df[df['is_outlier']].shape[0] != 0:
            status = CheckExecutionStatus.FAIL.value
            send_mm_alert(check)

        check_execution.status = status
        check_execution.results = json.dumps({'outlier_rows': df[df['is_outlier']].shape[0]})
        check_execution.logs = tail.contents()
        session.commit()
    except Exception as e:
        logger.debug(e)
        check_execution.status = CheckExecutionStatus.FAIL.value
        check_execution.logs = tail.contents()
        session.commit()


def freshness(check_id: int):
    """
    Checks that all values (timestamps) from the input source are within certain time delta
    """
    session, check_execution, logger, tail = init_check_execution(check_id)
    logger.debug('freshness check_id: {}'.format(check_id))

    try:
        check = crud.check.get(db=session, id=check_id)
        check_query = CheckService(session).get_query(check)
        logger.debug(check_query)

        df = df_from_query(check_query, conn=check.database.get_conn())

        # TODO fix column conversion
        logger.debug(df.head())
        logger.debug(df[check.column.name].dtypes)

        df[check.column.name] = pd.to_datetime(df[check.column.name])
        oldest_possible_time = datetime.now() - timedelta(seconds=check.delta_threshold_seconds)
        logger.debug('Oldest possible time: {}'.format(oldest_possible_time))
        df['is_fresh'] = df[check.column.name] >= oldest_possible_time
        logger.debug(df)

        logger.debug('Rows with non-fresh values: {}'.format(df[~df['is_fresh']].shape[0]))
        status = CheckExecutionStatus.SUCCESS.value

        if df[~df['is_fresh']].shape[0] != 0:
            status = CheckExecutionStatus.FAIL.value
            send_mm_alert(check)

        check_execution.status = status
        check_execution.results = json.dumps({'non_fresh_rows': df[~df['is_fresh']].shape[0]})
        check_execution.logs = tail.contents()
        session.commit()
    except Exception as e:
        logger.debug(e)
        check_execution.status = CheckExecutionStatus.FAIL.value
        check_execution.logs = tail.contents()
        session.commit()


def non_null(check_id: int):
    """
    Checks that all values from the input source are non-null
    """
    session, check_execution, logger, tail = init_check_execution(check_id)
    logger.debug('non_null check_id: {}'.format(check_id))

    try:
        check = crud.check.get(db=session, id=check_id)
        check_query = CheckService(session).get_query(check)
        logger.debug(check_query)

        df = df_from_query(check_query, conn=check.database.get_conn())

        df['has_null'] = df.isnull().values.sum() > 0
        logger.debug(df[df['has_null']])

        logger.debug('Rows with null values: {}'.format(df[df['has_null']].shape[0]))
        status = CheckExecutionStatus.SUCCESS.value

        if df[df['has_null']].shape[0] != 0:
            status = CheckExecutionStatus.FAIL.value
            send_mm_alert(check)

        check_execution.status = status
        check_execution.results = json.dumps({'null_rows': df[df['has_null']].shape[0]})
        check_execution.logs = tail.contents()
        session.commit()
    except Exception as e:
        logger.debug(e)
        check_execution.status = CheckExecutionStatus.FAIL.value
        check_execution.logs = tail.contents()
        session.commit()


def ordered(check_id: int):
    """
    Checks that all values from the input source are in order (smaller to bigger)
    """
    session, check_execution, logger, tail = init_check_execution(check_id)
    logger.debug('non_null check_id: {}'.format(check_id))
    try:
        check = crud.check.get(db=session, id=check_id)
        check_query = CheckService(session).get_query(check)
        logger.debug(check_query)

        df = df_from_query(check_query, conn=check.database.get_conn())

        from models.check import ORDERED_METRIC_NAME
        df['prev'] = df[ORDERED_METRIC_NAME].shift()
        df['bigger_than_previous'] = df[ORDERED_METRIC_NAME] >= df['prev'].fillna(df[ORDERED_METRIC_NAME])
        logger.debug(df)
        logger.debug(df[~df['bigger_than_previous']])

        logger.debug('Rows with unordered values: {}'.format(df[~df['bigger_than_previous']].shape[0]))
        status = CheckExecutionStatus.SUCCESS.value

        if df[~df['bigger_than_previous']].shape[0] != 0:
            status = CheckExecutionStatus.FAIL.value
            send_mm_alert(check)

        check_execution.status = status
        check_execution.results = json.dumps({'unordered_rows': df[~df['bigger_than_previous']].shape[0]})
        check_execution.logs = tail.contents()
        session.commit()
    except Exception as e:
        logger.debug(e)
        check_execution.status = CheckExecutionStatus.FAIL.value
        check_execution.logs = tail.contents()
        session.commit()


def custom_check(check_id: int):
    """
    Checks that the SQL from the custom check returns no rows
    """
    session, check_execution, logger, tail = init_check_execution(check_id)
    logger.debug('custom_check check_id: {}'.format(check_id))
    try:
        check = crud.custom_check.get(db=session, id=check_id)
        logger.debug(check.source)

        df = df_from_query(check.source, conn=check.database.get_conn())
        logger.debug(df)

        if df.empty:
            status = CheckExecutionStatus.SUCCESS.value
        else:
            status = CheckExecutionStatus.FAIL.value
            send_mm_alert(check)

        check_execution.status = status
        check_execution.results = json.dumps({'row_count': df.shape[0]})
        check_execution.logs = tail.contents()
        session.commit()
    except Exception as e:
        logger.debug(e)
        check_execution.status = CheckExecutionStatus.FAIL.value
        check_execution.logs = tail.contents()
        session.commit()
