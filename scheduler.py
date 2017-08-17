from datetime import datetime

import pytz
from apscheduler.schedulers.background import BlockingScheduler

from crawlers.update_stock_master import update_stock_master
from utils.logger import Logger

logger = Logger().get_logger()
SEOUL_TZ = pytz.timezone('Asia/Seoul')

sched = BlockingScheduler(timezone=SEOUL_TZ)

logger.info('now: {}'.format(datetime.now(SEOUL_TZ)))
sched.add_job(update_stock_master, trigger='cron', day='*', hour=7, minute=0, second=0)
sched.start()
