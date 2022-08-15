from typing import Optional, List
from pydantic import BaseModel, validator

from scheduler import CRON_REGEX


class CustomCheckBase(BaseModel):
    name: str
    schedule: str
    database_id: int
    description: Optional[str] = None
    source: Optional[str] = None
    active: Optional[bool] = False

    class Config:
        orm_mode = True

    @validator('schedule')
    def validate_schedule(cls, cron):
        assert CRON_REGEX.match(cron) is not None, "Invalid 'schedule' cron format"
        return cron


class CustomCheckCreate(CustomCheckBase):
    pass


class CustomCheckUpdate(CustomCheckBase):
    pass


class CustomCheckInDBBase(CustomCheckBase):
    id: int


class CustomCheck(CustomCheckInDBBase):
    pass


class CustomCheckWithLastExecution(CustomCheckBase):
    id: int
    last_check_execution_id: Optional[int]


class CustomCheckName(CustomCheckBase):
    name: str


class CustomCheckWithExecutions(CustomCheckInDBBase):
    executions: List


class CustomCheckInDB(CustomCheckInDBBase):
    pass


class CustomCheckUpdateMultiple(BaseModel):
    active: Optional[bool]
