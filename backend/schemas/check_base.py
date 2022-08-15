from typing import Optional
from pydantic import BaseModel, validator

from scheduler import CRON_REGEX


class CheckBase(BaseModel):
    name: str
    schedule: str
    description: Optional[str] = None
    active: Optional[bool] = False
    check_class: Optional[str]

    class Config:
        orm_mode = True

    @validator('schedule')
    def validate_schedule(cls, cron):
        assert CRON_REGEX.match(cron) is not None, "Invalid 'schedule' cron format"
        return cron


class CheckBaseWithLastExecution(CheckBase):
    id: int
    last_check_execution_id: Optional[int]
