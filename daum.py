# - 코스피: http://finance.daum.net/quote/all.daum?type=U&stype=P
# - 코스닥: http://finance.daum.net/quote/all.daum?type=U&stype=Q
from pprint import pprint

import requests
import bs4 as bs
import re

def get_data_from_daum():
    url = 'http://finance.daum.net/quote/all.daum?type=U&stype=P'
    response = requests.get(url)
    soup = bs.BeautifulSoup(response.text, 'html.parser')
    tables = soup.select("table.gTable.clr")
    # print(tables)
    stock_list = []
    for table in tables:
        trs = table.find_all('tr')[2:]
        for tr in trs:
            tds = tr.find_all('td')
            for i in range(0, int(len(tds)/3)):
                stock_name = tds[i*3].string
                stock_code = tds[i*3].a.get('href').replace('/item/main.daum?code=', '')
                stock_price = int(tds[i*3+1].string.replace(',', ''))
                stock_percent = float(tds[i*3+2].string.replace('%', ''))
                stock_list.append((stock_code, stock_name, stock_price, stock_percent))

    pprint(stock_list)

get_data_from_daum()

