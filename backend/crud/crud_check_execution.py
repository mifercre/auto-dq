from datetime import datetime, timedelta
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, case
from crud.base import CRUDBase, ORDER_BY_MAP
from models import CheckBase
from models.check_execution import CheckExecution, CheckExecutionStatus
from schemas.check_execution import CheckExecutionCreate, CheckExecutionUpdate, CheckExecutionWithCheckName


class CRUDCheckExecution(CRUDBase[CheckExecution, CheckExecutionCreate, CheckExecutionUpdate]):

    def _base_cols(self):
        return self.model.id, self.model.status, self.model.exec_time, self.model.results, self.model.check_id, \
               CheckBase.name.label('check_name'), CheckBase.check_class.label('check_class')

    def get_with_logs(self, db: Session, id: Optional[Any] = None, **kwargs) -> CheckExecution:
        if id:
            return db.query(*self._base_cols(), self.model.logs).join(self.model.check).filter(self.model.id == id).first()
        else:
            return db.query(*self._base_cols(), self.model.logs).join(self.model.check).filter(*self.get_filter_by_args(kwargs)).first()

    def get_all(self, db: Session, *, skip: int = 0, limit: int = 10, sort: list = None, **kwargs) -> List[CheckExecutionWithCheckName]:
        order_by = None
        if sort and len(sort) == 2:
            order_by = ORDER_BY_MAP[sort[1]](getattr(self.model, sort[0]))

        return db.query(*self._base_cols()) \
            .join(self.model.check) \
            .filter(*self.get_filter_by_args(kwargs)) \
            .order_by(order_by) \
            .offset(skip).limit(limit) \
            .all()

    def stats(self, db: Session):
        # Group by date, count total check executions and successful ones
        return db.query(
            func.date(self.model.exec_time).label('exec_date'),
            func.count(1).label('count'),
            func.sum(case(value=self.model.status, whens={CheckExecutionStatus.SUCCESS.value: 1}, else_=0)).label('count_success')
        ) \
            .filter(self.model.exec_time >= (datetime.now() - timedelta(days=10))) \
            .group_by(func.date(self.model.exec_time)) \
            .order_by(func.date(self.model.exec_time))


check_execution = CRUDCheckExecution(CheckExecution)
