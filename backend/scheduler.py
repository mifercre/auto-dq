import re
import crud

from pytz import utc
from sqlalchemy.orm import sessionmaker
from db.session import engine
from core.config import settings
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.base import JobLookupError

jobstores = {
    'default': SQLAlchemyJobStore(url=settings.SQLALCHEMY_DATABASE_URI)
}
executors = {
    'default': ThreadPoolExecutor(20)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}


class DQScheduler(BackgroundScheduler):

    def remove_all_jobs(self):
        for job in super().get_jobs():
            try:
                job.remove()
            except JobLookupError as e:
                print(e)

    def add_job(self, func, id, cron, args):
        cron_dict = CRON_REGEX.match(cron).groupdict()
        super().add_job(
            func, id=id, trigger='cron', minute=cron_dict['minute'], month=cron_dict['month'],
            day=cron_dict['day'], hour=cron_dict['hour'], day_of_week=cron_dict['day_of_week'], replace_existing=True,
            args=args, next_run_time=None, misfire_grace_time=60
        )

    def reschedule_job(self, id, cron):
        cron_dict = CRON_REGEX.match(cron).groupdict()
        super().reschedule_job(
            id, trigger='cron', minute=cron_dict['minute'], month=cron_dict['month'],
            day=cron_dict['day'], hour=cron_dict['hour'], day_of_week=cron_dict['day_of_week']
        )

    def safe_start(self):
        try:
            super().start()
        except JobLookupError as e:
            print(e)

    def app_init_start(self):
        self.safe_start()
        self.remove_all_jobs()
        session = sessionmaker(bind=engine)()
        all_checks = crud.check_base.get_all(db=session, limit=None)
        for check in all_checks:
            self.add_job(func=check.get_func(), id=check.name, cron=check.schedule, args=[check.id])
            if check.active:
                self.resume_job(check.name)


scheduler = DQScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)


CRON_REGEX = re.compile(
    r'^{0}\s+{1}\s+{2}\s+{3}\s+{4}$'.format(
        r'(?P<minute>[\d\*]{1,2}([\,\-\/][\d\*]{1,2})*)',
        r'(?P<hour>[\d\*]{1,2}([\,\-\/][\d\*]{1,2})*)',
        r'(?P<day>[\d\*]{1,2}([\,\-\/][\d\*]{1,2})*)',
        r'(?P<month>[\d\*]{1,2}([\,\-\/][\d\*]{1,2})*)',
        r'(?P<day_of_week>[0-6\*]([\,\-\/][0-6\*])*)'
    )
)
