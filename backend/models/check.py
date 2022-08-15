import re
from enum import Enum

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from models.check_base import CheckBase


CRON_REGEX = re.compile(
    r'^{0}\s+{1}\s+{2}\s+{3}\s+{4}$'.format(
        r'(?P<minute>[\d\*]{1,2}([\,\-\/][\d\*]{1,2})*)',
        r'(?P<hour>[\d\*]{1,2}([\,\-\/][\d\*]{1,2})*)',
        r'(?P<day>[\d\*]{1,2}([\,\-\/][\d\*]{1,2})*)',
        r'(?P<month>[\d\*]{1,2}([\,\-\/][\d\*]{1,2})*)',
        r'(?P<day_of_week>[0-6\*]([\,\-\/][0-6\*])*)'
    )
)


class CheckType(str, Enum):
    UNIQUENESS = 'uniqueness'
    # TODO: CONSISTENCY = 'consistency'
    OUTLIERS = 'outliers'
    FRESHNESS = 'freshness'
    NON_NULL = 'non_null'
    ORDERED = 'ordered'


class Check(CheckBase):
    """
    "Check" is a type of Check where users can specify the source DB, schema, table (and optionally column) and type of
    check (uniqueness, non null...) and DQ will generate the needed query to run the check.
    """

    __tablename__ = None

    type = Column(String, nullable=False)
    false_positives = Column(ARRAY(String))
    delta_threshold_seconds = Column(Integer)

    schema_id = Column(Integer, ForeignKey('dbschema.id'))
    schema = relationship('DBSchema')

    table_id = Column(Integer, ForeignKey('dbtable.id'))
    table = relationship('DBTable')

    column_id = Column(Integer, ForeignKey('dbcolumn.id'))
    column = relationship('DBColumn')

    __mapper_args__ = {
        'polymorphic_identity': 'check'
    }

    def get_func(self):
        from tasks import scripts
        return getattr(scripts, self.type)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'schedule': self.schedule,
            'type': self.type,
            'description': self.description,
            'active': self.active,
            'database_id': self.database_id,
            'schema_id': self.schema_id,
            'table_id': self.table_id,
            'column_id': self.column_id,
            'false_positives': self.false_positives,
            'delta_threshold_seconds': self.delta_threshold_seconds,
        }
