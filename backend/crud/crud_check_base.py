from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session
from crud.base import CRUDBase, ORDER_BY_MAP
from models import CheckExecution
from models.check_base import CheckBase
from schemas.check_base import CheckBaseWithLastExecution


class CRUDCheckBase(CRUDBase[CheckBase, None, None]):

    def _base_cols(self):
        return self.model.id, self.model.name, self.model.schedule, self.model.description,\
               self.model.active, self.model.check_class, func.max(CheckExecution.id).label('last_check_execution_id')

    def get_all(self, db: Session, *, skip: int = 0, limit: int = 10) -> List[CheckBase]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_with_last_execution(self, db: Session, id: int) -> CheckBaseWithLastExecution:
        return db.query(*self._base_cols())\
            .filter(self.model.id == id)\
            .outerjoin(CheckExecution)\
            .group_by(self.model.id)\
            .first()

    def get_all_with_last_execution(self, db: Session, *, skip: int = 0, limit: int = 10, sort: list = None, **kwargs) -> List[CheckBaseWithLastExecution]:
        order_by = None
        if sort and len(sort) == 2 and sort[0] and sort[1]:
            order_by = ORDER_BY_MAP[sort[1]](getattr(self.model, sort[0]))

        return db.query(*self._base_cols()) \
            .filter(*self.get_filter_by_args(kwargs)) \
            .outerjoin(CheckExecution) \
            .group_by(self.model.id) \
            .order_by(order_by) \
            .offset(skip).limit(limit) \
            .all()


check_base = CRUDCheckBase(CheckBase)
