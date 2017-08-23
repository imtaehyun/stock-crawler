from datetime import datetime

import pytz
from sqlalchemy import Column, DateTime, String, Integer

from database import Base
SEOUL_TZ = pytz.timezone('Asia/Seoul')

class 뉴스_마스터(Base):
    __tablename__ = '뉴스_마스터'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    rss_url = Column(String(50))
    etag = Column(String(50))
    modified = Column(String(50))
    created_at = Column(DateTime, default=datetime.now(SEOUL_TZ))
    modified_at = Column(DateTime)

    def __init__(self, name, rss_url):
        self.name = name
        self.rss_url = rss_url

class StockNews(Base):
    __tablename__ = 'STOCK_NEWS'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    id = Column(String(20), primary_key=True)
    offerer = Column(String(30))
    title = Column(String(50))
    link = Column(String(150))
    date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now(SEOUL_TZ))
    modified_at = Column(DateTime)

    def __init__(self, id, offerer, title, link, date):
        self.id = id
        self.offerer = offerer
        self.title = title
        self.link = link
        self.date = date

class 종목_마스터(Base):
    __tablename__ = '종목_마스터'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}

    종목코드 = Column(String(6), primary_key=True)
    시장구분 = Column(String(6))
    종목이름 = Column(String(50))
    거래소코드 = Column(String(12))
    created_at = Column(DateTime, default=datetime.now(SEOUL_TZ))
    modified_at = Column(DateTime)

    def __init__(self, 시장구분, 종목코드, 종목이름, 거래소코드):
        self.시장구분 = 시장구분
        self.종목코드 = 종목코드
        self.종목이름 = 종목이름
        self.거래소코드 = 거래소코드