from typing import Optional, List, Any
from pydantic import BaseModel, validator

from models.check import CheckType
from scheduler import CRON_REGEX


class CheckBase(BaseModel):
    name: str
    schedule: str
    type: CheckType
    description: Optional[str] = None
    active: Optional[bool] = False
    false_positives: Optional[List[Any]]
    delta_threshold_seconds: Optional[int]
    database_id: int
    schema_id: int
    table_id: int
    column_id: Optional[int]

    class Config:
        orm_mode = True

    @validator('schedule')
    def validate_schedule(cls, cron):
        assert CRON_REGEX.match(cron) is not None, "Invalid 'schedule' cron format"
        return cron


class CheckCreate(CheckBase):
    pass


class CheckUpdate(CheckBase):
    pass


class CheckInDBBase(CheckBase):
    id: int


class Check(CheckInDBBase):
    pass


class CheckWithLastExecution(CheckBase):
    id: int
    last_check_execution_id: Optional[int]


class CheckName(CheckBase):
    name: str


class CheckWithExecutions(CheckInDBBase):
    executions: List


class CheckInDB(CheckInDBBase):
    pass


class CheckUpdateMultiple(BaseModel):
    active: Optional[bool]
