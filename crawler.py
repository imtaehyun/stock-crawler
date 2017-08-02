"""종목 DB 갱신"""
import time

import krx
from database import session
from models import 종목_마스터

try:
    start_time = time.time()

    stock_master = [stock[0] for stock in session.query(종목_마스터.거래소코드).all()]

    affected_rows = 0
    for stock in krx.get_stock_list():

        if stock['short_code'].endswith('0') and stock['full_code'] not in stock_master:
            session.add(종목_마스터(stock['marketName'], stock['short_code'][1:], stock['codeName'], stock['full_code']))
            affected_rows += 1

    session.commit()

    execution_time = time.time() - start_time

    print('execution_time: {}'.format(execution_time))
    print('{} rows added'.format(affected_rows))
except Exception as e:
    print(e)
