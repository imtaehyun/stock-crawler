from urllib.parse import urlparse, parse_qs

import requests
import time
from scrapy.selector import Selector
from sqlalchemy import func

from database import session
from models import StockNews
from utils.logger import Logger
from utils.slack import Slack

logger = Logger().get_logger()
slack = Slack()


def get_news_list(last_id=None, limit=30, page=1):
    """다음 금융 뉴스 리스트 크롤링"""
    r = requests.get('http://finance.daum.net/news/news_list.daum?type=all&section=&limit={}&page={}'.format(limit, page))

    if r.status_code == 200:
        news_list = list()
        new_last_id = None

        for idx, news_selector in enumerate(Selector(text=r.text).css('.newsList li')):
            link = 'http://finance.daum.net' + news_selector.css('a::attr(href)').extract()[0]
            doc_id = parse_qs(urlparse(link).query)['docid'][0]
            title = news_selector.css('b::text').extract()[0]
            offerer = news_selector.css('span.offerer::text').extract()[0]
            date = news_selector.css('span.datetime::text').extract()[0]

            if idx == 0:
                new_last_id = doc_id

            if last_id and last_id == doc_id:
                break

            news_list.append(dict(link=link, doc_id=doc_id, title=title, offerer=offerer, date=date))

        return news_list, new_last_id
    else:
        raise Exception(r.status_code)


def get_news_content(doc_id):
    """기사 상세 내용 크롤링"""
    r = requests.get('http://finance.daum.net/news/news_print.daum?type=all&sub_type=&docid={}'.format(doc_id))

    if r.status_code == 200:
        # print(r.text)
        content = Selector(text=r.text).css('#dmcfContents div::text, #dmcfContents p::text').extract()
        return ' '.join(content)
    else:
        raise Exception(r.status_code)


def update_daum_stock_news():
    try:
        start_time = time.time()

        last_id = session.query(func.max(StockNews.id)).scalar()
        logger.info('last_id: {}'.format(last_id))

        news_list, new_last_id = get_news_list(last_id=last_id, limit=50)
        for news in news_list:
            session.add(StockNews(id=news.get('doc_id'), offerer=news.get('offerer'), title=news.get('title'), link=news.get('link'), date=news.get('date')))

        if len(news_list) > 0:
            session.commit()

        execution_time = time.time() - start_time

        logger.info('execution_time: {}'.format(execution_time))
        logger.info('{} rows added'.format(len(news_list)))

    except Exception as e:
        logger.exception(e, exc_info=True)
        slack.send_message('BATCH:update_daum_stock_news fail {}'.format(e))


if __name__ == '__main__':
    # update_daum_stock_news()
    get_news_content('MD20170817230056038')