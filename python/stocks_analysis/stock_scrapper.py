
import requests
import imgkit
from PIL import Image
from tradingview_ta import TA_Handler, Interval
import yfinance as yf
from datetime import datetime

class TickerAnalyzer:
    def __init__(self):
        self.zacks = None
        self.tv = None

    def get_zacks_info(self, ticker: str):
        self.zacks = self.Zacks()
        return self.zacks.get_ticker_info(ticker)

    def get_tradingview_info(self, ticker: str):
        self.tv = self.Tradingview()
        return self.tv.get_ticker_info(ticker)
    
    def get_yf_info(self, ticker: str):
        self.tv = self.YahooFinance()
        return self.tv.get_ticker_info(ticker)

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

            # Crop the image
            cropped_img = Image.open(image_path).crop(crop_box)

            # Save or show the cropped image
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

                    # Retrieve the analysis
                    analysis = handler.get_analysis()

                    return analysis.summary
                except:
                    continue



