from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base_class import Base


class DBColumn(Base):
    """
    DBColumn class is meant to represent a single column from a given table. Columns must have a name, and optionally
    they can have a data type, profiling metadata (this are metrics like MIN/MAX/... values) and partition information
    """

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String)

    # TODO auto-profiling metrics
    # profiling = Column(JSONB)

    is_partition_column = Column(Boolean)

    table_id = Column(Integer, ForeignKey('dbtable.id'), index=True)
    table = relationship('DBTable', back_populates='columns')

    __table_args__ = (
        UniqueConstraint('name', 'table_id', name='unique_column_name_table_id'),
    )

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'is_partition_column': self.is_partition_column,
            'table_id': self.table_id
        }
