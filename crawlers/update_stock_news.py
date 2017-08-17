import feedparser

from utils.logger import Logger

logger = Logger().get_logger()


def test_stock_news(url):
    """뉴스 RSS 테스트 (etag, last-modified 지원여부)"""
    try:
        feed = feedparser.parse(url)
        etag = None
        modified = None
        # pprint(feed)
        if feed.status == 200:
            try:
                etag = feed.etag
            except Exception:
                etag = None

            try:
                modified = feed.modified
            except Exception:
                modified = None

            logger.info('etag: {}, modified: {}'.format(etag, modified))
        else:
            logger.error('error')

        if etag:
            feed = feedparser.parse(url, etag=etag)

            if feed.status == 304:
                logger.info('etag support')
            else:
                logger.info('etag not support')

        if modified:
            feed = feedparser.parse(url, modified=modified)

            if feed.status == 304:
                logger.info('last-modified support')
            else:
                logger.info('last-modified not support')

    except Exception as e:
        logger.exception(e)

if __name__ == '__main__':
    test_stock_news('http://file.mk.co.kr/news/rss/rss_50200011.xml')