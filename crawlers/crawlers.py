import time
from datetime import datetime, timedelta

import krx
from crawlers.update_daum_stock_news import get_news_list
from database import Session
from models import StockNews, 종목_마스터, SEOUL_TZ
from utils.logger import Logger
from utils.slack import Slack

logger = Logger().get_logger()
slack = Slack()


def update_stock_master():
    """종목 DB 갱신"""
    try:
        session = Session()
        start_time = time.time()

        stock_master = [stock[0] for stock in session.query(종목_마스터.거래소코드).all()]

        affected_rows = 0
        for stock in krx.get_stock_list():
            if stock['short_code'].endswith('0') and stock['full_code'] not in stock_master:
                session.add(종목_마스터(stock['marketName'], stock['short_code'][1:], stock['codeName'], stock['full_code']))
                affected_rows += 1

        if affected_rows > 0:
            session.commit()
            slack.send_message('BATCH:update_stock_master success {}건 업데이트'.format(affected_rows))

        execution_time = time.time() - start_time

        logger.info('execution_time: {}'.format(execution_time))
        logger.info('{} rows added'.format(affected_rows))

    except Exception as e:
        logger.exception(e)
        slack.send_message('BATCH:update_stock_master fail {}'.format(e))
    finally:
        session.close()


def update_daum_stock_news():
    """다음뉴스 크롤링하여 DB 저장"""
    try:
        start_time = time.time()

        session = Session()

        last_id = session.query(StockNews.id).order_by(StockNews.date.desc(), StockNews.id.desc()).first()
        if last_id:
            last_id = last_id[0]

        logger.info('last_id: {}'.format(last_id))

        news_list = get_news_list(last_id=last_id, limit=100)

        affected_rows = 0
        for news in news_list:
            try:
                date = datetime.strptime(news.get('date'), '%y.%m.%d %H:%M')
                session.add(StockNews(id=news.get('doc_id'), offerer=news.get('offerer'), title=news.get('title'),
                                      date=date))
                session.commit()
                affected_rows += 1
            except Exception as e:
                logger.exception('duplicated: {}'.format(news))
                session.rollback()

        execution_time = time.time() - start_time

        logger.info('execution_time: {}'.format(execution_time))
        logger.info('{} rows added'.format(affected_rows))

    except Exception as e:
        logger.exception('update_daum_stock_news', exc_info=True)
        session.rollback()
        slack.send_message('BATCH:update_daum_stock_news fail {}'.format(e))
    finally:
        session.close()


def tag_stock_code_to_news():
    """증권뉴스에 관련종목 태깅"""
    try:
        start_time = time.time()

        session = Session()
        stock_list = session.query(종목_마스터.종목코드, 종목_마스터.종목이름).all()

        stock_news = session.query(StockNews).filter(StockNews.종목코드 == None, StockNews.created_at >= (datetime.now(SEOUL_TZ) - timedelta(hours=1))).all()

        # print(str(stock_news.statement.compile(dialect=mysql.dialect())))
        affected_rows = 0
        for news in stock_news:
            try:
                stock = next((stock for stock in stock_list if stock[1] in news.title), None)
                if stock:
                    logger.info('news: {} => {}'.format(news.title, stock[1]))
                    news.종목코드 = stock[0]
                    news.modified_at = datetime.now(SEOUL_TZ)
                    affected_rows += 1
            except Exception:
                logger.exception('tag_stock_code_to_news', exc_info=True)

        session.commit()

        execution_time = time.time() - start_time

        logger.info('execution_time: {}'.format(execution_time))
        logger.info('{} rows added'.format(affected_rows))
    except Exception as e:
        logger.exception('tag_stock_code_to_news', exc_info=True)
        session.rollback()
        slack.send_message('BATCH:tag_stock_code_to_news fail {}'.format(e))
    finally:
        session.close()

if __name__ == '__main__':
    tag_stock_code_to_news()
    # get_news_content('MD20170817230056038')