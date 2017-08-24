import time
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs

import requests
from scrapy.selector import Selector

from database import session
from models import StockNews, SEOUL_TZ
from utils.logger import Logger
from utils.slack import Slack

logger = Logger().get_logger()
slack = Slack()


def get_news_list(limit=30, page=1):
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

            news_list.append(dict(link=link, doc_id=doc_id, title=title, offerer=offerer, date=date))

        return news_list
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

        db_news = [news[0] for news in session.query(StockNews.id).filter(StockNews.created_at >= datetime.now(SEOUL_TZ) - timedelta(minutes=10)).all()]

        affected_rows = 0
        news_list = get_news_list(limit=50)

        for news in [x for x in news_list if x.get('doc_id') not in db_news]:
            date = datetime.strptime(news.get('date'), '%y.%m.%d %H:%M')
            session.add(StockNews(id=news.get('doc_id'), offerer=news.get('offerer'), title=news.get('title'), date=date))
            affected_rows += 1

        if affected_rows > 0:
            session.commit()

        execution_time = time.time() - start_time

        logger.info('execution_time: {}'.format(execution_time))
        logger.info('{} rows added'.format(affected_rows))

    except Exception as e:
        logger.exception(exc_info=True)
        slack.send_message('BATCH:update_daum_stock_news fail {}'.format(e))


if __name__ == '__main__':
    update_daum_stock_news()
    # get_news_content('MD20170817230056038')