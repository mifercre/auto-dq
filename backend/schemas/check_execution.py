import datetime
from typing import Optional, Any, List

from pydantic import BaseModel
from models import CheckExecutionStatus


class CheckExecutionBase(BaseModel):
    check_id: int
    exec_time: datetime.datetime
    status: Optional[str] = None

    class Config:
        orm_mode = True


class CheckExecutionCreate(CheckExecutionBase):
    check_id: int
    exec_time: datetime.datetime
    status: Optional[str] = CheckExecutionStatus.RUNNING.value
    results: Optional[Any] = '{}'
    logs: Optional[str] = ''


class CheckExecutionUpdate(CheckExecutionBase):
    pass


class CheckExecutionInDBBase(CheckExecutionBase):
    pass


class CheckExecution(CheckExecutionInDBBase):
    pass


class CheckExecutionWithCheckName(CheckExecutionInDBBase):
    id: Optional[int]
    check_id: Optional[int]
    exec_time: Optional[datetime.datetime]
    status: Optional[str] = None
    check_name: Optional[str]
    check_class: Optional[str]
    results: Optional[Any]


class CheckExecutionWithLogs(CheckExecutionInDBBase):
    id: Optional[int]
    check_id: Optional[int]
    exec_time: Optional[datetime.datetime]
    status: Optional[str] = None
    check_name: Optional[str]
    check_class: Optional[str]
    results: Optional[Any]
    logs: Optional[str]


class CheckExecutionInDB(CheckExecutionInDBBase):
    pass


class Stats(BaseModel):
    id: int = -1
    meta: dict
    data: List
