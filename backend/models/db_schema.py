from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.base_class import Base


class DBSchema(Base):
    """
    DBSchema class represents a schema on a given source DB. Schemas must have a name, and optionally they can
    have tables.
    """

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    database_id = Column(Integer, ForeignKey('db.id'))
    database = relationship('DB', back_populates='schemas')

    tables = relationship('DBTable', back_populates='schema')
