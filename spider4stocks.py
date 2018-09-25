import requests
from bs4 import BeautifulSoup
import os
import json
import numpy as np
import pprint
import sys
import random
import warnings
warnings.filterwarnings("ignore")

_HOST_AASTOCKS = "http://www.aastocks.com/en/usq/quote"
_SYMBOL_SEARCH = "/symbolsearch.aspx?comp={0}"
_QUOTE = "/quote.aspx?symbol={0}"

_QUOTE_YAHOO = "https://finance.yahoo.com/quote/{0}?p={0}"

_AGENTS = [
    "Googlebot/2.1 (+http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/6.0 Mobile/10A5376e Safari/8536.25 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12F70 Safari/600.1.4 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.96 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Googlebot/2.1; +http://www.google.com/bot.html) Safari/537.36",
    "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; Google Web Preview Analytics) Chrome/27.0.1453 Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/41.0.2272.76 Chrome/41.0.2272.76 Safari/537.36",


]

_HEADERS = {
    'User-Agent': random.choice(_AGENTS),
    }

# proxies
_PROXY_HOST = "proxy.crawlera.com"
_PROXY_POST = "8010"
_PROXY_AUTH = "020f566483124ffabffb045089a73b11:"
_PROXIES = {
    "https": "https://{0}@{1}:{2}/".format(_PROXY_AUTH, _PROXY_HOST, _PROXY_POST),
}

# requests
_SESSION = requests.Session()


def _get_page(pagerequest):
    resp = _SESSION.get(
        pagerequest,
        headers=_HEADERS,
        proxies=_PROXIES,
        verify=False,
        timeout=random.choice(range(30, 100))
    )
    resp.encoding = "utf-8"
    if resp.status_code == 200:
        return resp.text
    else:
        raise Exception('Error: {0} {1}'.format(resp.status_code, resp.reason))


def _make_soup(pagerequest):
    html = _get_page(pagerequest)
    # save_str_to_file("1", html)
    return BeautifulSoup(html, "lxml")


# 处理json.dumps的问题
def default_json(o):
    if isinstance(o, np.int64):
        return int(o)
    raise TypeError


# 存储list形式的文件
def save_list_to_file(filename, list):
    with open(filename, "w", encoding="utf-8") as f:
        for l in list:
            f.write(json.dumps(l, default=default_json) + "\n")


def save_str_to_file(filename, s):
    with open(filename, "w", encoding="utf-8") as f:
            f.write(s)


# 查询股票代号
def _search_stock_symbol(soup):
    """Generator that returns Author objects from the author search page"""
    # 暂时不做翻页
    l = soup.select("div[class='common_box'] tr")[1:]
    for row in l:
        # print(row)
        yield Stock(row)


class Stock(object):
    """Returns an object for a single stock"""
    def __init__(self, __data):
        if isinstance(__data, str):
            self.Symbol = __data
        else:
            self.Symbol = __data.select("a[class='lnk']")[0].text.split(".")[0]
            self.Stock_Name = __data.select("td")[1].text.replace("\xa0", " ")
            self.Exchange = __data.select("td")[2].text
        self._filled = False

    def fill(self):
        soup = _make_soup(_QUOTE_YAHOO.format(self.Symbol))
        self.Prev_Close = self.choose_soup(soup, r"td[data-test='PREV_CLOSE-value']")
        self.Open = self.choose_soup(soup, r"td[data-test='OPEN-value']")
        self.BID = self.choose_soup(soup, r"td[data-test='BID-value']")
        self.ASK = self.choose_soup(soup, r"td[data-test='ASK-value']")
        self.Days_Range = self.choose_soup(soup, r"td[data-test='DAYS_RANGE-value']")
        self.Fifty_Two_Weeks_Range = self.choose_soup(soup, r"td[data-test='FIFTY_TWO_WK_RANGE-value']")
        self.TD_Volume = self.choose_soup(soup, r"td[data-test='TD_VOLUME-value']")
        self.Average_Volume_3Month = self.choose_soup(soup, r"td[data-test='AVERAGE_VOLUME_3MONTH-value']")
        self.Market_Cap = self.choose_soup(soup, r"td[data-test='MARKET_CAP-value']")
        self.Beta = self.choose_soup(soup, r"td[data-test='MARKET_CAP-value']")
        self.PE_Ratio = self.choose_soup(soup, r"td[data-test='PE_RATIO-value']")
        self.EPS_Ratio = self.choose_soup(soup, r"td[data-test='EPS_RATIO-value']")
        self.Earnings_Date = self.choose_soup(soup, r"td[data-test='EARNINGS_DATE-value']")
        self.Dividend_and_Yield = self.choose_soup(soup, r"td[data-test='DIVIDEND_AND_YIELD-value']")
        self.ex_Dividend_Date = self.choose_soup(soup, r"td[data-test='EX_DIVIDEND_DATE-value']")
        self.One_Year_Target_Price = self.choose_soup(soup, r"td[data-test='ONE_YEAR_TARGET_PRICE-value']")

        self._filled = True
        return self

    def choose_soup(self, soup, pattern, default="N/A"):
        mc = soup.select(pattern)
        return mc[0].text if mc else default

    def __str__(self):
        return pprint.pformat(self.__dict__)

    def get_attr_dict(self):
        return self.__dict__


# 查询入口
def search_stock(name):
    """Search by author name and return a generator of Author objects"""
    url = _HOST_AASTOCKS + _SYMBOL_SEARCH.format(requests.utils.quote(name))
    soup = _make_soup(url)
    return _search_stock_symbol(soup)


if __name__ == '__main__':
    company = sys.argv[1]
    # company = "apple"
    stock = None
    MC = "N/A"
    _generator = search_stock(company)
    while MC == "N/A":
        try:
            stock = next(_generator).fill()
            print(stock)
            MC = stock.Market_Cap
        except StopIteration as e:
            print(e)
            break
    print(stock.get_attr_dict(), "\n")
    print("Market Cap: ", MC)
