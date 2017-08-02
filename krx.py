# coding=utf-8
import json
from datetime import datetime
from pprint import pprint

import requests

"""한국거래소(http://www.krx.co.kr/) 정보 파싱"""


def generate_otp(bld, name):
    """OTP Key 생성"""
    r = requests.get('http://marketdata.krx.co.kr/contents/COM/GenerateOTP.jspx?bld=' + bld + '&name=' + name)
    # print('otp: {}'.format(r.text))
    return r.text


def get_stock_list():
    """주식종목 추출"""
    key = generate_otp(bld='COM/finder_stkisu', name='form')
    payload = dict(mktsel='ALL', code=key)
    r = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx', data=payload)

    if r.status_code == 200:
        return json.loads(r.text)['block1']
    else:
        return None


def get_stock_info(krx_code):
    """주식 > 종목정보 > [30037] 종합정보"""
    key = generate_otp(bld='MKD/04/0402/04020100/mkd04020100t1_05', name='tablesubmit')
    payload = dict(isu_cd=krx_code, code=key)
    r = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx', data=payload)

    if r.status_code == 200:
        return json.loads(r.text)['DS5'][0]
    else:
        return None


def get_stock_price_by_tick(krx_code):
    """주식 > 종목정보 > [30039] 시간대별시세"""
    key = generate_otp(bld='MKD/04/0402/04020100/mkd04020100t3_01', name='form')
    payload = dict(isu_cd=krx_code, code=key)
    r = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx', data=payload)

    if r.status_code == 200:
        return json.loads(r.text)['result']
    else:
        return None


def get_stock_price_by_day(krx_code, from_date=None, to_date=None):
    """주식 > 종목정보 > [30040] 일자별시세"""
    if not from_date:
        from_date = datetime.today().strftime('%Y%m%d')
    if not to_date:
        to_date = datetime.today().strftime('%Y%m%d')

    key = generate_otp(bld='MKD/04/0402/04020100/mkd04020100t3_02', name='chart')
    payload = dict(isu_cd=krx_code, fromdate=from_date, todate=to_date, code=key)
    r = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx', data=payload)

    if r.status_code == 200:
        return json.loads(r.text)['block1']
    else:
        return None


def get_stock_news(krx_code):
    """주식 > 종목정보 > [30042] 뉴스/공시"""
    # 공시 MKD/04/0402/04020100/mkd04020100t4t1, grid
    # 뉴스 MKD/04/0402/04020100/mkd04020100t4t2_01, list
    key = generate_otp(bld='MKD/04/0402/04020100/mkd04020100t4t2_01', name='list')
    payload = dict(isu_cd=krx_code, curPage=1, pageSize=50, code=key)
    r = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx', data=payload)

    if r.status_code == 200:
        return json.loads(r.text)['DS1']
    else:
        return None


def get_kospi_200_list():
    """지수 > 주가지수 > [20011] KOSPI시리즈"""
    key = generate_otp(bld='MKD/03/0304/03040101/mkd03040101T3_01', name='form')
    payload = dict(ind_tp_cd='1', idx_ind_cd='028', lang='ko', compst_isu_tp='1', schdate='20161207',
                   pagePath='/contents/MKD/03/0304/03040101/MKD03040101T3.jsp', code=key)
    r = requests.post('http://marketdata.krx.co.kr/contents/MKD/99/MKD99000001.jspx', data=payload)

    if r.status_code == 200:
        return json.loads(r.text)['output']
    else:
        return None


if __name__ == "__main__":
    pprint(get_stock_list())
    # pprint(get_stock_info('KR7078890001'))
    # pprint(get_stock_price_by_tick('KR7078890001'))
    # pprint(get_stock_price_by_day('KR7078890001', '20161222'))
    # 028 kospi 200
    # 034 kospi 100
    # pprint(get_stock_news('KR7005930003'))
    # pprint(get_kospi_200_list())
