from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from db.base_class import Base


class DBTable(Base):
    """
    DBTable class represents a table on a given schema and source DB. Tables must have a name, and optionally they can
    have colums, partitions, checks associated to them, and profiling metadata.
    """

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    # TODO auto-profiling metrics
    # profiling = Column(JSONB)

    schema_id = Column(Integer, ForeignKey('dbschema.id'), index=True)
    schema = relationship('DBSchema', back_populates='tables')

    columns = relationship('DBColumn', back_populates='table')
    partitions = relationship('DBTablePartition', back_populates='table')

    checks = relationship('Check', back_populates='table')

    __table_args__ = (
        UniqueConstraint('name', 'schema_id', name='unique_table_name_schema_id'),
    )

    @property
    def partition_column(self):
        for c in self.columns:
            if c.is_partition_column:
                return c

    @property
    def has_partition_column(self):
        for c in self.columns:
            if c.is_partition_column:
                return True
        return False

    def get_column(self, column_name):
        for c in self.columns:
            if c.name == column_name:
                return c
