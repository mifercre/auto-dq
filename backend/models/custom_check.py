from sqlalchemy import Column, String
from models.check_base import CheckBase


class CustomCheck(CheckBase):
    """
    CustomCheck is a type of Check where users can manually write the actual query that runs against the source DB and
    the check passes if the query returns empty result.
    """

    __tablename__ = None

    source = Column(String)

    __mapper_args__ = {
        'polymorphic_identity': 'customcheck'
    }

    def get_func(self):
        from tasks import scripts
        return scripts.custom_check

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'schedule': self.schedule,
            'description': self.description,
            'source': self.source,
            'active': self.active,
            'database_id': self.database_id,
        }
