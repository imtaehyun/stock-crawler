import time
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

import requests
from scrapy.selector import Selector
from sqlalchemy import and_

from database import session
from models import StockNews, 종목_마스터, SEOUL_TZ
from utils.logger import Logger
from utils.slack import Slack

logger = Logger().get_logger()
slack = Slack()


def get_news_list(limit=30, page=1, last_id=None):
    """다음 금융 뉴스 리스트 크롤링"""
    r = requests.get('http://finance.daum.net/news/news_list.daum?type=all&section=&limit={}&page={}'.format(limit, page))

    if r.status_code == 200:
        news_list = list()

        for idx, news_selector in enumerate(Selector(text=r.text).css('.newsList li')):
            link = 'http://finance.daum.net' + news_selector.css('a::attr(href)').extract()[0]
            doc_id = parse_qs(urlparse(link).query)['docid'][0]
            title = news_selector.css('b::text').extract()[0]
            offerer = news_selector.css('span.offerer::text').extract()[0]
            date = news_selector.css('span.datetime::text').extract()[0]

            if last_id and last_id == doc_id:
                break

            news_list.append(dict(link=link, doc_id=doc_id, title=title, offerer=offerer, date=date))

        return news_list
    else:
        raise Exception('get_news_list error: status_code[{}]'.format(r.status_code))


def get_news_content(doc_id):
    """기사 상세 내용 크롤링"""
    r = requests.get('http://finance.daum.net/news/news_print.daum?type=all&sub_type=&docid={}'.format(doc_id))

    if r.status_code == 200:
        # print(r.text)
        content = Selector(text=r.text).css('#dmcfContents div::text, #dmcfContents p::text').extract()
        return ' '.join(content)
    else:
        raise Exception('get_news_content error: status_code[{}]'.format(r.status_code))


def update_daum_stock_news():
    try:
        start_time = time.time()

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


def update_news_stock_code():
    stock_list = session.query(종목_마스터.종목코드, 종목_마스터.종목이름).all()

    stock_news = session.query(StockNews).filter(StockNews.종목코드 == None).all()

    for news in stock_news:
        logger.info('news: {}'.format(news.title))
        stock = next((stock for stock in stock_list if stock[1] in news.title), None)
        if stock:
            news.종목코드 = stock[0]
            session.commit()


if __name__ == '__main__':
    update_news_stock_code()
    # get_news_content('MD20170817230056038')