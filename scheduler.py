from datetime import datetime

import pytz
from apscheduler.schedulers.background import BlockingScheduler

from crawlers.crawlers import update_stock_master, update_daum_stock_news, tag_stock_code_to_news
from utils.logger import Logger

logger = Logger().get_logger()

SEOUL_TZ = pytz.timezone('Asia/Seoul')
logger.info('now: {}'.format(datetime.now(SEOUL_TZ)))

sched = BlockingScheduler(timezone=SEOUL_TZ)

# 매일 오전 7시 주식종목 업데이트
sched.add_job(update_stock_master, trigger='cron', day='*', hour=7, minute=0, second=0)

# 2분마다 다음 증권 뉴스 업데이트
sched.add_job(update_daum_stock_news, trigger='interval', minutes=2)

# 30분마다 뉴스 관련 종목 태깅
sched.add_job(tag_stock_code_to_news, trigger='interval', minutes=30)

sched.start()
