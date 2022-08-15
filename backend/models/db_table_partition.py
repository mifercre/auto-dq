from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from db.base_class import Base


class DBTablePartition(Base):
    """
    DBTablePartition class represents a partition on a given table. Partitions must have a name and optionally they can
    have one or more check executions.
    """
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    table_id = Column(Integer, ForeignKey('dbtable.id'), index=True)
    table = relationship('DBTable', back_populates='partitions')

    # TODO: let check executions run on specific table partitions
    # check_executions = relationship('CheckExecution', back_populates='table_partition')

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'table_id': self.table_id
        }
