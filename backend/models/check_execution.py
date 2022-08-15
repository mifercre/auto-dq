import enum

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from db.base_class import Base


class CheckExecutionStatus(enum.Enum):
    SUCCESS = 'success'
    RUNNING = 'running'
    FAIL = 'fail'


class CheckExecution(Base):
    """
    CheckExecution class represents each individual execution of a DQ check, it keeps information about the check that
    is being executed, the execution time, the status, the results and the logs.
    """

    id = Column(Integer, primary_key=True, index=True)
    exec_time = Column(TIMESTAMP, nullable=False)
    status = Column(String)
    # TODO: right now just storing free key-values on the `results`, could standardize the json schema/spec
    results = Column(JSONB)
    logs = Column(Text)

    check_id = Column(Integer, ForeignKey('check.id'))
    check = relationship('CheckBase', back_populates='executions')

    # TODO: let check executions run on specific table partitions
    # table_partition_id = Column(Integer, ForeignKey('dbtablepartition.id'))
    # table_partition = relationship('DBTablePartition', back_populates='check_executions')

    def json(self):
        return {
            'id': self.id,
            'exec_time': self.exec_time,
            'status': self.status,
            'results': self.results,
            'logs': self.logs,
            'check_id': self.check_id,
        }
