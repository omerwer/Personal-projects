#!/usr/bin/env python3

import readline

from stock_scrapper import TickerAnalyzer
import urllib3

urllib3.disable_warnings()


def main():
    ta = TickerAnalyzer()
    ticker = input("Please enter a ticker: ")
    print(ta.get_zacks_info(ticker))
    print(ta.get_tradingview_info(ticker))
    print(ta.get_yf_info(ticker))
    print(ta.get_finviz_info(ticker))
    print(ta.get_chatgpt_info(ticker))





if __name__ == "__main__":
    main()