
import requests
import imgkit
import os
from PIL import Image
from tradingview_ta import TA_Handler, Interval
import yfinance as yf
from datetime import datetime
import pytesseract
import multiprocessing
import re
from finvizfinance.quote import finvizfinance

class TickerAnalyzer:
    def __init__(self):
        self.zacks = None
        self.tv = None
        self.yf = None
        self.finviz = None

    def get_zacks_info(self, ticker: str):
        self.zacks = self.Zacks()
        return self.zacks.get_ticker_info(ticker)

    def get_tradingview_info(self, ticker: str):
        self.tv = self.Tradingview()
        return self.tv.get_ticker_info(ticker)
    
    def get_yf_info(self, ticker: str):
        self.yf = self.YahooFinance()
        return self.yf.get_ticker_info(ticker)
    
    def get_finviz_info(self, ticker: str):
        self.finviz = self.Finviz()
        return self.finviz.get_ticker_info(ticker)

    class Zacks():
        def __init__(self):
            self.ticker = None

        def _get_zacks_styles_score_image(self, ticker: str):
            url = f'https://www.zacks.com/stock/quote/{ticker}?q={ticker}'

            options = {
                'javascript-delay': '5000',  # wait 3 seconds for JS
                'no-stop-slow-scripts': '',
                'enable-javascript': '',
                'width': '1280',  # or adjust based on your needs
            }

            config = imgkit.config(wkhtmltoimage='/usr/bin/wkhtmltoimage')
            image_path = 'image.png'
            imgkit.from_url(url, image_path, config=config, options=options)

            crop_box = (330, 180, 1145, 480)

            cropped_img = Image.open(image_path).crop(crop_box)
            os.remove(image_path)

            cropped_img.save(f"style_scores_{ticker}.png")

        def get_ticker_info(self, ticker: str):
            data_dict = {}

            self.ticker = ticker.upper()

            self._get_zacks_styles_score_image(self.ticker)

            response = requests.get(url=f"https://quote-feed.zacks.com/index.php?t={self.ticker}")
            data = dict(response.json())[self.ticker]
            data_dict.update({'name' : data['name']})
            data_dict.update({'ticker' : data['ticker']})
            data_dict.update({'zacks rank' : f"{data['zacks_rank']} ({data['zacks_rank_text']})"})
            data_dict.update({"Forward P/E" : data['source']['sungard']["pe_ratio"]})

            data_dict.update({"dividend_freq" : data['source']['sungard']["dividend_freq"]})
            data_dict.update({'dividend_yield' : data['dividend_yield']+'%'})
            data_dict.update({"dividend" : data['source']['sungard']["dividend"]})

            return data_dict

    class YahooFinance():
        def __init__(self):
            self.ticker = None
            self.attributes = ['analyst_price_targets', 'news', 'recommendations_summary', 'upgrades_downgrades']
            self.summary = dict()
        
        def get_ticker_info(self, ticker: str):
            ticker_uppercase = ticker.upper()
            self.ticker = yf.Ticker(ticker_uppercase)
            for attr in dir(self.ticker):
                if attr in self.attributes and not attr == 'news':
                    attr_value = getattr(self.ticker, attr)
                    if attr == 'analyst_price_targets':
                        conclusion = None
                        if attr_value['current'] < attr_value['low']:
                            conclusion = f'{ticker_uppercase} trades lower than low target! seems undervalued.'
                        elif attr_value['current'] >= attr_value['high']:
                            conclusion = f'{ticker_uppercase} trades higher than high target! seems overvalued.'
                        else:
                            conclusion = f'{ticker_uppercase} trades within range.'
                        
                        reccomendation_and_conclusion = (attr_value, conclusion)

                        self.summary.update({'Price targets' : reccomendation_and_conclusion})
                    elif attr == 'recommendations_summary':
                        self.summary.update({'recommendations' : {}})
                        attr_value = getattr(self.ticker, attr)
                        recommendations_dict = attr_value.to_dict(orient='index')
                        for (key, value) in recommendations_dict.items():
                            _ = value.pop('period')
                            self.summary['recommendations'].update({f'{key}-Month' : value})

                    elif attr == 'upgrades_downgrades':
                        upgrades_dict = attr_value.to_dict(orient='index')
                        recent_upgrades_dict = {}
                        for date, values in upgrades_dict.items():
                            if date.year >= datetime.now().year - 1:
                                recent_upgrades_dict.update({date : values})

                        self.summary.update({"Upgrades & downgrades" : recent_upgrades_dict})
                    
                elif attr == 'news':
                    recent_news_list = []
                    for news in getattr(self.ticker, attr):
                        curr_date = datetime.now()
                        year, month, _ = news['content']['pubDate'].split('-')
                        if (int(year) == curr_date.year or (int(year) == curr_date.year - 1 and abs(curr_date.month -  int(month)) > 6)):
                            for key in ['id', 'description', 'displayTime', 'isHosted', 
                                        'bypassModal', 'previewUrl', 'thumbnail', 'provider', 
                                        'clickThroughUrl', 'metadata', 'finance', 'storyline']:
                                _ = news['content'].pop(key)

                            recent_news_list.append(news['content'])

                    self.summary.update({'News' : recent_news_list})

            return self.summary
    
    
    class Tradingview():
        def __init__(self):
            self.ticker = None
            self.summary = dict()
            self.exchange  = {
                                # North America
                                "NYSE": "america",
                                "NASDAQ": "america",
                                "AMEX": "america",
                                "TSX": "america",
                                "TSXV": "america",
                                "CSE": "america",

                                # Europe
                                "LSE": "europe",
                                "XETRA": "europe",
                                "FWB": "europe",
                                "Euronext": "europe",
                                "BME": "europe",
                                "SIX": "europe",
                                "Borsa Italiana": "europe",
                                "Oslo": "europe",
                                "WSE": "europe",

                                # Asia
                                "TSE": "asia",         # Tokyo
                                "HKEX": "asia",        # Hong Kong
                                "SGX": "asia",         # Singapore
                                "KOSPI": "asia",       # Korea
                                "SSE": "asia",         # Shanghai
                                "SZSE": "asia",        # Shenzhen
                                "TWSE": "asia",        # Taiwan
                                "NSE": "india",
                                "BSE": "india",

                                # Australia
                                "ASX": "oceania",

                                # Middle East
                                "TASE": "middle_east",
                                "DFM": "middle_east",
                                "ADX": "middle_east",
                                "QSE": "middle_east",
                                "KSE": "middle_east",
                                "BHB": "middle_east",
                                "MSM": "middle_east",

                                # Africa
                                "JSE": "africa",
                                "NSE Nigeria": "africa",
                                "EGX": "africa",

                                # Latin America
                                "B3": "america",       # Brazil
                                "BMV": "america",      # Mexico
                                "BCBA": "america",     # Argentina
                                "Santiago": "america", # Chile
                                "Lima": "america",     # Peru
                                "BVC": "america",      # Colombia

                                # Other / Eastern Europe & Misc
                                "MOEX": "europe",
                                "MICEX": "europe",
                                "IDX": "asia",         # Indonesia
                                "PSE": "asia",         # Philippines
                                "SET": "asia",         # Thailand
                                "HNX": "asia",         # Vietnam
                                "BIST": "europe",      # Turkey
                            }
        
        def _render_imgkit(self, url, output_path, config, options, crop_box, str, shared=None):
            try:
                
                imgkit.from_url(url, output_path, config=config, options=options)

                cropped_img = Image.open(output_path).crop(crop_box)
                os.remove(output_path)

                if str == 'forecast':
                    text = pytesseract.image_to_string(cropped_img)
                    match = re.search(r"\d+\.\d+", text)
                    if match:
                        price_target = float(match.group())
                        shared['Price target'] = price_target

                else:
                    cropped_img.save(f"{self.ticker}_{str}.png")

            except Exception as e:
                pass
        
        def _get_tv_stats_from_image(self, ticker: str, exchange: str):
            url = f'https://www.tradingview.com/symbols/{exchange}-{ticker}/'
            forecast_url = url + 'forecast/'

            options = {
                'javascript-delay': '10000',
                'no-stop-slow-scripts': '',
                'enable-javascript': '',
                'width': '1280',  # or adjust based on your needs
            }

            config = imgkit.config(wkhtmltoimage='/usr/bin/wkhtmltoimage')

            price_target = multiprocessing.Manager().dict()

            image_path_ks = 'tv_ks.png'
            image_path_forecast = 'tv_forecast.png'

            process_ks = multiprocessing.Process(target=self._render_imgkit, args=(url, image_path_ks, config, options, (15, 1721, 286, 2219), 'ks'))
            process_forecast = multiprocessing.Process(target=self._render_imgkit, args=(forecast_url, image_path_forecast, config, options, (19, 654, 199, 732), 'forecast', price_target))

            process_ks.start()
            process_forecast.start()

            process_ks.join(30)
            process_forecast.join(30)

            self.summary.update(price_target)

        
        def get_ticker_info(self, ticker: str):
            self.ticker = ticker.upper()
            for ex, region in self.exchange.items():
                try:
                    handler = TA_Handler(
                        symbol=self.ticker,
                        exchange=ex,
                        screener=region,
                        interval=Interval.INTERVAL_1_MONTH,
                    )

                    self._get_tv_stats_from_image(self.ticker, ex)

                    # Retrieve the analysis
                    analysis = handler.get_analysis()

                    self.summary.update({'Analysis' : analysis.summary})

                    return self.summary
                except:
                    continue

    class Finviz:
        def __init__(self):
            self.ticker = None
            self.summary = dict() 
        
        def get_ticker_info(self, ticker: str):
            stock = finvizfinance(ticker.upper())
            data = stock.ticker_full_info()
            # print(data.keys())
            # print(data['ratings_outer'].to_dict(orient='index'))
            # print(data['news'].to_dict(orient='index'))
            
            for attr in  ['Index', 'Perf Week','EPS next Y','Insider Trans','Perf Month','EPS next Q','Short Float','Shs Float',
                          'Perf Quarter','EPS this Y','Inst Trans','Perf Half Y','Book/sh','EPS next 5Y','ROE','Perf YTD',
                          'EPS past 5Y','ROI','52W High','Quick Ratio','Sales past 5Y','52W Low','ATR (14)','Current Ratio',
                          'EPS Y/Y TTM','RSI (14)','Volatility W','Volatility M','Sales Y/Y TTM','Recom','Option/Short','LT Debt/Eq',
                          'EPS Q/Q','Payout','Rel Volume','Prev Close','Sales Surprise','EPS Surprise','Sales Q/Q','EPS next Y Percentage',
                          'ROA','Short Interest','Perf Year','Avg Volume','SMA20','SMA50','SMA200','Trades','Volume','Change']:
                _ = data['fundament'].pop(attr)

            self.summary.update({'General info' : data['fundament']})

            upgrade_downgrade_list = list()
            curr_date = datetime.now()

            for key, rating in data['ratings_outer'].to_dict(orient='index').items():
                updgrade_downgrade_year = int(rating['Date'].year)
                if updgrade_downgrade_year >= curr_date.year - 1:
                    upgrade_downgrade_list.append(rating)

            self.summary.update({'Upgrades/Downgrades' : upgrade_downgrade_list})

            news_list = list()

            for key, news in data['news'].to_dict(orient='index').items():
                news_year = news['Date'].year
                news_month = news['Date'].month
                news_day = news['Date'].day

                if ((int(news_year) == curr_date.year and int(news_month) == curr_date.month and abs(int(news_day) - curr_date.day) <= 3) or 
                    (int(news_month) == curr_date.month - 1 and abs(curr_date.day -  int(news_day)) > 28) or
                    (int(news_year) == curr_date.year - 1 and news_month == 12 and abs(curr_date.day -  int(news_day)) > 28)):
                        news_list.append(news)

            self.summary.update({'News' : news_list})

            insiders_list = list()

            for key, insider in stock.ticker_inside_trader().to_dict(orient='index').items():
                if str(curr_date.year)[-2:] in insider['Date'] or str(int(curr_date.year)-1)[-2:] in insider['Date']:
                    insiders_list.append(insider)

            self.summary.update({'Insiders trading' : insiders_list})


            return self.summary


