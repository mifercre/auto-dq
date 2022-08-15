import random
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('app.log')


def get_random_daily_cron():
    return '{} {} * * *'.format(random.randint(0, 59), random.randint(0, 23))
