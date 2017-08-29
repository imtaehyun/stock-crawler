from urllib.parse import urlparse, parse_qs

import requests
from scrapy.selector import Selector

from utils.logger import Logger

logger = Logger().get_logger()


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