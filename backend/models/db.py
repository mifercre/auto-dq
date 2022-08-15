from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import EncryptedType
from sqlalchemy.orm import relationship
from core.config import settings
from db.base_class import Base
from core.db_engines import engine_specs


class DB(Base):
    """
    DB class represents a source database. DBs must have a name and type. The `type` field determines the database
    engine, such as "presto", "postgresql", or any other engine that we implement in the future.

    Optionally DBs can have connection details such as hostname, port, username, password..., schemas and a blacklist.

    The blacklist is used to reduce the exploration search tree for Auto-DQ's metadata. If a schema name matches with
    any value from the blacklist, Auto-DQ won't go deeper into that schema to explore its tables > columns.
    """

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    type = Column(String, nullable=False)
    hostname = Column(String)
    port = Column(Integer)
    database = Column(String)
    username = Column(String)
    password = Column(EncryptedType(String(1024), settings.SECRET_KEY))

    schemas = relationship('DBSchema', back_populates='database', lazy='dynamic')

    # Comma separated list of schemas that shouldn't be included in the metadata (accepts regex too)
    blacklist = Column(String)

    def get_conn(self):
        engine_spec = engine_specs.get(self.type)
        return engine_spec.get_sqla_engine(
            hostname=self.hostname,
            port=self.port,
            database=self.database,
            username=self.username,
            password=self.password
        )

    def fetchone(self, statement):
        return self.get_conn().execute(statement).fetchone()

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'hostname': self.hostname,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'password': self.password,
            'blacklist': self.blacklist
        }
