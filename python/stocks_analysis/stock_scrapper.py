
import requests
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import os

class TickerAnalyzer:
    def __init__(self):
        self.memory = {}

    def __get_browser(self):
        ''' Initiate and return firefox browser using gecko driver.
        '''
        opts = Options()
        opts.headless = False
        browser = Firefox(options=opts)
        return browser

    def get_url(self, ticker):
        browser = self.__get_browser()

        html = browser.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Open zacks.com
        url = f"https://www.zacks.com/stock/quote/{ticker}?q={ticker}"
        browser.get(url)

        # Try to find earnings table
        # If it cannot be found then the ticker probably is not reported on by zacks.com and we are looking at a searching results screen
        try:
            table = soup.find_all('table', id=f'Premium Research for {ticker}')
        except IndexError:
            error = "Encountered an error trying to access "+url+". The ticker you specified may not be available on Zacks.com."
            raise KeyError(error) from None

    def zacks(self, ticker: str):
        data_dict = {}
        response = requests.get(url=f"https://quote-feed.zacks.com/index.php?t={ticker}")
        data = dict(response.json())[ticker.upper()]
        data_dict.update({'name' : data['name']})
        data_dict.update({'ticker' : data['ticker']})
        data_dict.update({'zacks rank' : f"{data['zacks_rank']} ({data['zacks_rank_text']})"})
        data_dict.update({"P/E" : data['source']['sungard']["pe_ratio"]})

        data_dict.update({"dividend_freq" : data['source']['sungard']["dividend_freq"]})
        data_dict.update({'dividend_yield' : data['dividend_yield']+'%'})
        data_dict.update({"dividend" : data['source']['sungard']["dividend"]})

        return data_dict

