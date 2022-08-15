from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from db.base_class import Base


class CheckBase(Base):
    """
    CheckBase class is meant to represent the basics of any kind of Data Quality check available on Auto-DQ. On it's
    most basic form, a check must have a source database (where the check will be executed on), a name, a schedule
    (cronjob time), and a check class type (so far either "check" or "customcheck").

    Different check types are represented using SQLAlchemy "Single Table Inheritance", with the `check_class` column
    indicating the type of check.

    Optionally checks can have description, they can be enabled/disabled, and they can have one or more executions.
    """

    __tablename__ = 'check'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    schedule = Column(String, nullable=False)
    description = Column(String)
    active = Column(Boolean)
    check_class = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'checkbase',
        'polymorphic_on': check_class
    }
    executions = relationship('CheckExecution', back_populates='check')

    database_id = Column(Integer, ForeignKey('db.id'), nullable=False)
    database = relationship('DB')

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'schedule': self.schedule,
            'description': self.description,
            'active': self.active,
            'database_id': self.database_id,
        }
