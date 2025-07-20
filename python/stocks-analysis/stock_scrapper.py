
import requests
from abc import ABC

import imgkit
import re
import random
import time
from io import BytesIO
import base64
from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from tradingview_ta import TA_Handler, Interval
from functools import lru_cache
import yfinance as yf
from datetime import datetime, timedelta
import pytesseract
from concurrent.futures import ThreadPoolExecutor
from finvizfinance.quote import finvizfinance
from g4f.client import Client

import tickers_constants

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"


def get_screen_size():
    try:
        import pyautogui
        return pyautogui.size()
    except Exception as e:
        return (1920, 1080)


class TickerAnalyzer:
    def __init__(self):
        self.curr_ticker = ""
        self.cache = {"zacks" : {}, "tv" : {}, "yf" : {}, "finviz" : {}, "sws" : {}, "chatgpt" : {}}
        self.zacks = self.Zacks()
        self.tv = self.Tradingview()
        self.yf = self.YahooFinance()
        self.finviz = self.Finviz()
        self.sws = self.SimplyWallStreet()
        self.chatgpt = self.Chatgpt()

    def get_zacks_info(self, ticker: str):
        if self.cache["zacks"] and ticker in self.cache["zacks"].keys():
            return self.cache["zacks"][ticker]
        else:
            zacks_ret =  self.zacks.get_ticker_info(ticker)
            if "msg" not in zacks_ret.keys():
                if len(self.cache["zacks"]) == 20:
                    _, _ = self.cache["zacks"].popitem(last=False)
                self.cache["zacks"].update({ticker : zacks_ret})

            return zacks_ret

    def get_tradingview_info(self, ticker: str):
        if self.cache["tv"] and ticker in self.cache["tv"].keys():
            return self.cache["tv"][ticker]
        else:
            tv_ret =  self.tv.get_ticker_info(ticker)
            if len(self.cache["tv"]) == 20:
                _, _ = self.cache["tv"].popitem(last=False)
            self.cache["tv"].update({ticker : tv_ret})

            return tv_ret
    
    def get_yf_info(self, ticker: str):
        if self.cache["yf"] and ticker in self.cache["yf"].keys():
            return self.cache["yf"][ticker]
        else:
            yf_ret = self.yf.get_ticker_info(ticker)
            if len(self.cache["yf"]) == 20:
                _, _ = self.cache["yf"].popitem(last=False)
            self.cache["yf"].update({ticker : yf_ret})

            return yf_ret

    def get_finviz_info(self, ticker: str):
        if self.cache["finviz"] and ticker in self.cache["finviz"].keys():
            return self.cache["finviz"][ticker]
        else:
            finviz_ret = self.finviz.get_ticker_info(ticker)
            if len(self.cache["finviz"]) == 20:
                _, _ = self.cache["finviz"].popitem(last=False)
            self.cache["finviz"].update({ticker : finviz_ret})

            return finviz_ret

    def get_sws_info(self, ticker: str):
        if self.cache["sws"] and ticker in self.cache["sws"].keys():
            return self.cache["sws"][ticker]
        else:
            sws_ret = self.sws.get_ticker_info(ticker)
            if len(self.cache["sws"]) == 20:
                _, _ = self.cache["sws"].popitem(last=False)
            self.cache["sws"].update({ticker : sws_ret})

            return sws_ret

    def get_chatgpt_info(self, ticker: str):
        if self.cache["chatgpt"] and ticker in self.cache["chatgpt"].keys():
            return self.cache["chatgpt"][ticker]
        
        source_methods = {
            'zacks': self.zacks,
            'tv': self.tv,
            'yf': self.yf,
            'finviz': self.finviz,
            'sws': self.sws
        }

        futures = {}
        non_valid_count = 0
        with ThreadPoolExecutor() as executor:
            for source, obj in source_methods.items():
                if ticker not in self.cache[source]:
                    futures[source] = executor.submit(obj.get_ticker_info, ticker)

        non_valid_msg = {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}
        
        for source, future in futures.items():
            try:
                result = future.result()
                if result == non_valid_msg:
                    non_valid_count+=1
                self.cache[source][ticker] = result
            except Exception as e:
                self.cache[source][ticker] = {"error": str(e)}

        if non_valid_count == len(source_methods):
            non_valid_count = 0
            return non_valid_msg

        non_valid_count = 0
        
        chatgpt_ret = self.chatgpt.get_ticker_info(
            ticker,
            self.cache["zacks"][ticker],
            self.cache["tv"][ticker],
            self.cache["yf"][ticker],
            self.cache["finviz"][ticker],
            self.cache["sws"][ticker],
        )

        if len(self.cache["chatgpt"]) == 20:
            self.cache["chatgpt"].popitem(last=False)

        self.cache["chatgpt"][ticker] = chatgpt_ret
        return chatgpt_ret 
    

    class Source(ABC):
        def __init__(self):
            self.ticker = None
            self.summary = dict()
    
    class Zacks(Source):
        def get_ticker_info(self, ticker: str):
            data_dict = {}

            self.ticker = ticker.upper()

            url = f"https://quote-feed.zacks.com/index.php?t={self.ticker}"

            if not self._is_valid_zacks_ticker(url, self.ticker):
                self.summary = {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}
            else:
                try:
                    image = self._get_zacks_styles_score_image(self.ticker)

                    response = requests.get(url=url)
                    data = dict(response.json())[self.ticker]
                    data_dict.update({'name' : data['name']})
                    data_dict.update({'ticker' : data['ticker']})
                    data_dict.update({'zacks rank' : f"{data['zacks_rank']} ({data['zacks_rank_text']})"})
                    data_dict.update({"Forward P/E" : data['source']['sungard']["pe_ratio"]})

                    data_dict.update({"dividend_freq" : data['source']['sungard']["dividend_freq"]})
                    data_dict.update({'dividend_yield' : data['dividend_yield']+'%'})
                    data_dict.update({"dividend" : data['source']['sungard']["dividend"]})
                    data_dict.update({"image" : image})

                    self.summary = data_dict
            
                except Exception as e:
                    self.summary = {"msg" : f"{e}. Please provide a valid stock ticker."}

            return self.summary
        
        def _is_valid_zacks_ticker(self, url: str, ticker: str):
            headers = {"User-Agent": "Mozilla/5.0"}
            try:
                res = requests.get(url, headers=headers, timeout=5)
                data = res.json()
                return False if "error" in data[ticker].keys() else True
            except Exception as e:
                return False
        
        def _get_zacks_styles_score_image(self, ticker: str):
            url = f'https://www.zacks.com/stock/quote/{ticker}?q={ticker}'

            options = {
                'javascript-delay': '5000',  # wait 3 seconds for JS
                'no-stop-slow-scripts': '',
                'enable-javascript': '',
                'width': '1280',  # or adjust based on your needs
            }

            width, height = get_screen_size()

            config = imgkit.config(wkhtmltoimage='/usr/bin/wkhtmltoimage') # First install - sudo apt-get install wkhtmltopdf

            img_bytes = imgkit.from_url(url, False, config=config, options=options)

            # screen resolution is based on a 1920x1080 size, so we need to adjust for the current screen resolution
            scale_x = width / 1920
            scale_y = height / 1080
            crop_box = (330 * scale_x, 180 * scale_y, 1145 * scale_x, 480 * scale_y)

            cropped_img = Image.open(BytesIO(img_bytes)).crop(crop_box)

            buffer = BytesIO()
            cropped_img.save(buffer, format="PNG")
            buffer.seek(0)
            return base64.b64encode(buffer.read()).decode('utf-8')


    class Tradingview(Source):
        def __init__(self):
            super().__init__()
            self.exchange  = tickers_constants.TV_STOCKS_EXCHAGE

        @lru_cache(maxsize=128)
        def get_ticker_info(self, ticker: str):
            self.ticker = ticker.upper()
            error_429 = False
            for ex, region in self.exchange.items():
                try:
                    handler = TA_Handler(
                        symbol=self.ticker,
                        exchange=ex,
                        screener=region,
                        interval=Interval.INTERVAL_1_MONTH,
                    )

                    analysis = handler.get_analysis()

                    self._get_tv_stats_from_image(self.ticker, ex, analysis)

                    self.summary.update({'Analysis' : analysis.summary})

                except Exception as e:
                    time.sleep(1)
                    if "429" in str(e):
                        error_429 = True
                        break
                    else:
                        continue

            if not self.summary:
                if error_429:
                    self.summary = {"msg" : "Too many requets to Tradingview's server. Service is temporarly blocked for your IP."}
                else:
                    self.summary = {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}

            return self.summary
        

        def _adjust_ks_string(self, ks_string_list, key_stats):
            index = 2
            indicators_list = ['TTM', 'indicated', 'FY']
            while (index < len(ks_string_list) - 1):
                if ks_string_list[index] == '':
                    index = index + 1
                else:
                    if index == len(ks_string_list) - 1:
                        key_stats[ks_string_list[index]] = ''
                        index = index + 1
                    else:
                        if any(word in ks_string_list[index] for word in indicators_list) and \
                        any(word in ks_string_list[index+1] for word in indicators_list):
                            key_stats[ks_string_list[index]] = ''
                            index = index + 1
                        elif ks_string_list[index+1] == '' and \
                        any(char.isdigit() for char in ks_string_list[index+2]):
                            key_stats[ks_string_list[index]] = ks_string_list[index+2]
                            index = index + 3
                        else:
                            key_stats[ks_string_list[index]] = ks_string_list[index+1]
                            index = index + 2
        
        def _render_imgkit(self, url, config, options, crop_box, str, shared, analysis=None):
            try:
                img_bytes = imgkit.from_url(url, False, config=config, options=options)

                cropped_img = Image.open(BytesIO(img_bytes)).crop(crop_box)

                if str == 'forecast':
                    text = pytesseract.image_to_string(cropped_img)
                    match = re.search(r"\d+\.\d+", text)
                    if match:
                        price_target = float(match.group())
                        last_price = float(analysis.indicators['close'])
                        shared['Last closing price'] = last_price
                        shared['Price target'] = price_target
                        potential =  round((((price_target - last_price) / last_price) * 100), 2)
                        shared['Potential %'] = f'{potential}%'

                else:
                    text = pytesseract.image_to_string(cropped_img)
                    
                    pattern = r"(Key stats.*?(?:Beta \(1Y\)|Expense ratio)[^\d\-]*[-+]?\d*\.?\d+)"
                    match = re.search(pattern, text, re.DOTALL)
                    if match:
                        key_stats_raw = match.group(1)
                        key_stats_words = key_stats_raw.split('\n')
                        for i, word in enumerate(key_stats_words):
                            key_stats_words[i] = word.replace(' >', '').replace('uso', '').replace(' M', 'M').replace(' B', 'B')
                        key_stats = {}

                        self._adjust_ks_string(key_stats_words, key_stats)

                        shared['Key stats'] = key_stats

            except Exception as e:
                print(f"{e}please try again if any data is missing...")

        
        def _get_tv_stats_from_image(self, ticker: str, exchange: str, analysis: dict):
            url = f'https://www.tradingview.com/symbols/{exchange}-{ticker}/'
            forecast_url = url + 'forecast/'

            options = {
                'javascript-delay': '5000',
                'load-error-handling': 'ignore',
                'no-stop-slow-scripts': '',
                'enable-javascript': '',
                'width': '1280',  # or adjust based on your needs
            }

            config = imgkit.config(wkhtmltoimage='/usr/bin/wkhtmltoimage')

            stats_and_price_target = {}

            width, height = get_screen_size()

            scale_x = width / 1920
            scale_y = height / 1080

            with ThreadPoolExecutor() as executor:
                future_ks  = executor.submit(
                    self._render_imgkit,
                    url, config, options,
                    (15 * scale_x, 1375 * scale_y, 315 * scale_x, 2600 * scale_y),
                    'ks', stats_and_price_target
                )
                future_forecast = executor.submit(
                    self._render_imgkit,
                    forecast_url, config, options,
                    (19 * scale_x, 654 * scale_y, 199 * scale_x, 732 * scale_y),
                    'forecast', stats_and_price_target, analysis
                )

            future_ks.result()
            future_forecast.result()
            
            self.summary.update(stats_and_price_target)
                     

    class YahooFinance(Source):
        def __init__(self):
            super().__init__()
            self.attributes = ['analyst_price_targets', 'news', 'recommendations_summary', 'upgrades_downgrades']

        def get_ticker_info(self, ticker: str):
            try:
                ticker_uppercase = ticker.upper()
                self.ticker = yf.Ticker(ticker_uppercase)
                for attr in dir(self.ticker):
                    if attr in self.attributes and not attr == 'news':
                        attr_value = getattr(self.ticker, attr)
                        self._not_news_attr_handeling(attr, attr_value, ticker_uppercase)
                        
                    elif attr == 'news':
                        self._news_attr_handeling(attr)
        
            except Exception as e:
                print(f"Error msg: {e}.")
                
                
            if not self.summary['News'] and not self.summary['recommendations'] and not self.summary['Upgrades & downgrades']:
                price, _ = self.summary['Price target']
                if not price:
                    self.summary = {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}
            
            return self.summary
        
        def _news_attr_handeling(self, attr):
            recent_news_dict = {}
            for news in getattr(self.ticker, attr):
                content = news['content']
                curr_date = datetime.now()
                year, month, _ = content['pubDate'].split('-')
                if (int(year) == curr_date.year or (int(year) == curr_date.year - 1 and abs(curr_date.month -  int(month)) > 6)):
                    for key in ['id', 'description', 'displayTime', 'isHosted', 
                                'bypassModal', 'previewUrl', 'thumbnail', 'provider', 
                                'clickThroughUrl', 'metadata', 'finance', 'storyline']:
                        _ = content.pop(key)

                    content_type = content.pop('contentType')
                    raw_url_data = content.pop('canonicalUrl')
                    content['url'] = raw_url_data['url']
                    recent_news_dict.update({content_type : content})


            news = {
                str(k): v for k, v in recent_news_dict.items()
            }
            self.summary.update({'News' : news})
        
        def _upgrades_downgrades(self, attr_value):
                upgrades_dict = attr_value.to_dict(orient='index')
                recent_upgrades_dict = {}
                for date, values in upgrades_dict.items():
                    if date.year >= datetime.now().year - 1:
                        recent_upgrades_dict.update({date : values})

                upgrades = {
                    str(k): v for k, v in recent_upgrades_dict.items()
                }

                self.summary.update({"Upgrades & downgrades" : upgrades})


        def _recommendations(self, attr_value):
            self.summary.update({'recommendations' : {}})
            recommendations_dict = attr_value.to_dict(orient='index')
            for (key, value) in recommendations_dict.items():
                _ = value.pop('period')
                self.summary['recommendations'].update({f'{key}-Month' : value})


        def _analyst_price_targets(self, attr_value, ticker_uppercase):
            conclusion = None
            if 'low' in attr_value and attr_value['current'] < attr_value['low']:
                conclusion = f'{ticker_uppercase} trades lower than low target! seems undervalued.'
            elif 'high' in attr_value and attr_value['current'] >= attr_value['high']:
                conclusion = f'{ticker_uppercase} trades higher than high target! seems overvalued.'
            else:
                conclusion = f'{ticker_uppercase} trades within range.'
            
            reccomendation_and_conclusion = (attr_value, conclusion)

            self.summary.update({'Price target' : reccomendation_and_conclusion})
        

        def _not_news_attr_handeling(self, attr, attr_value, ticker_uppercase):
            if attr == 'analyst_price_targets':
                self._analyst_price_targets(attr_value, ticker_uppercase)

            self._get_otm_calls()

            if attr == 'recommendations_summary':
                self._recommendations(attr_value)

            elif attr == 'upgrades_downgrades':
                self._upgrades_downgrades(attr_value)


        def _get_otm_calls(self, otm_threshold: float=1.15):
            current_price = float(self.ticker.info.get("regularMarketPrice", 0))

            if current_price is None:
                raise ValueError("Couldn't fetch current price.")

            expirations = self.ticker.options
            cutoff = datetime.today() + timedelta(days=60)
            valid_expirations = [d for d in expirations if datetime.strptime(d, "%Y-%m-%d") <= cutoff]

            results = []

            index = 0

            for exp in valid_expirations:
                try:
                    calls = self.ticker.option_chain(exp).calls
                    for i in range(len(calls["strike"])):
                        strike = float(calls["strike"][i])
                        if strike > current_price * otm_threshold:
                            index += 1
                            option = { str(index) :
                                {"strike": str(strike),
                                "expiration": exp,
                                "volume": str(calls["volume"][i]),
                                "openInterest": str(calls["openInterest"][i]),
                                "lastPrice": str(calls["lastPrice"][i])}
                            }

                            results.append(option)
                except Exception as e:
                    print(f"Error retrieving options for {exp}: {e}")
                    continue

            self.summary.update({"Options flow (Deep OTM)" : results})


    class Finviz(Source):       
        def get_ticker_info(self, ticker: str):
            try:
                stock = finvizfinance(ticker.upper())
                                
                data = stock.ticker_full_info()
                
                for attr in tickers_constants.FINVIZ_ATTR_LIST:
                    try:
                        _ = data['fundament'].pop(attr)
                    except:
                        continue

                self.summary.update({'General info' : data['fundament']})

                curr_date = datetime.now()

                self._upgrades_downgrades(curr_date, data)
                self._news(curr_date, data)

                insiders_dict = {}

                for key, insider in stock.ticker_inside_trader().to_dict(orient='index').items():
                    if str(curr_date.year)[-2:] in insider['Date'] or str(int(curr_date.year)-1)[-2:] in insider['Date']:
                        insider_name = insider.pop('Insider Trading')
                        insiders_dict.update({insider_name : insider})

                insiders = {
                    str(k): v for k, v in insiders_dict.items()
                }

                self.summary.update({'Insiders trading' : insiders})
            
            except Exception as e:
                print(f"Error msg: {e}")
                self.summary = {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}

            return self.summary

        
        def _news(self, curr_date, data):
            news_dict = data['news'].to_dict(orient='index')
            recent_news_dict = {}
            
            for key, news in news_dict.items():
                date = news.pop('Date')
                news_year = date.year
                news_month = date.month
                news_day = date.day

                if ((int(news_year) == curr_date.year and int(news_month) == curr_date.month and abs(int(news_day) - curr_date.day) <= 3) or 
                    (int(news_month) == curr_date.month - 1 and abs(curr_date.day -  int(news_day)) > 28) or
                    (int(news_year) == curr_date.year - 1 and news_month == 12 and abs(curr_date.day -  int(news_day)) > 28)):
                        recent_news_dict.update({date : news})

            news = {
                str(k): v for k, v in recent_news_dict.items()
            }

            self.summary.update({'News' : news})
        
        def _upgrades_downgrades(self, curr_date, data):
            if 'ratings_outer' not in data:
                self.summary.update({'Upgrades/Downgrades' : {}})
            else:
                upgrades_dict = data['ratings_outer'].to_dict(orient='index')
                recent_upgrades_dict = {}
                for key, values in upgrades_dict.items():
                    date = values.pop('Date')
                    updgrade_downgrade_year = int(date.year)
                    if updgrade_downgrade_year >= curr_date.year - 1:
                        recent_upgrades_dict.update({date : values})

                upgrades = {
                    str(k): v for k, v in recent_upgrades_dict.items()
                }

                self.summary.update({'Upgrades/Downgrades' : upgrades})

    class SimplyWallStreet(Source):
        @lru_cache(maxsize=128)       
        def get_ticker_info(self, ticker: str):
            base_url = "https://simplywall.st/en/stocks/us"
            try:
                for industry in tickers_constants.SWS_INDUSTRIES:
                    for us_mkt in tickers_constants.SWS_US_MARKETS:
                        company_name = yf.Ticker(ticker).info["shortName"].lower()
                        adjusted_cpmpany_name = self._normalize_company_name(company_name)
                        adjusted_cpmpany_name = adjusted_cpmpany_name.replace(',', '').replace('.', '').replace('&', '').replace(' ', '-').replace('--', '-')
                        adjusted_cpmpany_name = adjusted_cpmpany_name[:-1] if adjusted_cpmpany_name[-1] == '-' else adjusted_cpmpany_name

                        url = f"{base_url}/{industry}/{us_mkt}-{ticker.lower()}/{adjusted_cpmpany_name}"

                        if not self._is_valid_simplywallstreet_url(url, random.choice(tickers_constants.USER_AGENTS_LIST)):
                            continue

                        options = {
                            'javascript-delay': '5000',
                            'load-error-handling': 'ignore',
                            'no-stop-slow-scripts': '',
                            'enable-javascript': '',
                            'width': '1280',  # or adjust based on your needs
                        }

                        config = imgkit.config(wkhtmltoimage='/usr/bin/wkhtmltoimage')

                        width, height = get_screen_size()

                        scale_x = width / 1920
                        scale_y = height / 1080

                        crop_box = (344 * scale_x, 261 * scale_y, 1174 * scale_x, 1085 * scale_y)

                        img_bytes = imgkit.from_url(url, False, config=config, options=options)

                        cropped_img = Image.open(BytesIO(img_bytes)).crop(crop_box)

                        width, height = cropped_img.size
                        mid_height = height // 2 

                        bottom_half = cropped_img.crop((0, mid_height, width, height))

                        gray = bottom_half.convert("L")
                        sharpened = gray.filter(ImageFilter.SHARPEN)
                        contrast = ImageEnhance.Contrast(sharpened).enhance(2.0)
                        inverted = ImageOps.invert(contrast)
                        binarized = inverted.point(lambda x: 255 if x > 128 else 0, mode='1')
                        binarized = binarized.resize((binarized.width * 2, binarized.height * 2))
                        text = pytesseract.image_to_string(binarized)
                        text_dict = self._extract_sections(text)

                        top_half = cropped_img.crop((0, 0, width, mid_height))

                        buffer = BytesIO()
                        top_half.save(buffer, format="PNG")
                        buffer.seek(0)

                        self.summary.update({'Rewards' : text_dict["Rewards"]})
                        self.summary.update({'Risk Analysis' : text_dict["Risk Analysis"]})
                        self.summary.update({"image" : base64.b64encode(buffer.read()).decode('utf-8')})

                        return self.summary
            except:
                pass
                
            if not self.summary:
                return {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}


        def _normalize_company_name(self, name):
            pattern = r'\b(?:' + '|'.join(tickers_constants.COMMON_SUFFIXES) + r')\b\.?,?'
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)
            return name
        

        def _is_valid_simplywallstreet_url(self, url: str, user_agent: str):
            headers = {'User-Agent': user_agent}
            try:
                response = requests.get(url, headers=headers, timeout=5)

                if response.status_code == 404 or "Sorry, this page was not found" in response.text:
                    return False

                return True
            except requests.RequestException:
                return False
        
        def _extract_sections(self, text):
            lines = text.strip().splitlines()
            data = {}
            current_section = None
            index = 0

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                elif line.isupper():
                    current_section = line.title()
                    data[current_section] = {}
                    index = 1

                elif current_section:
                    cleaned_line = re.sub(r"^(\*|¥|@|¥e|xe|ve|e\s|[-•→©\u2022]|\s)+", "", line, flags=re.IGNORECASE)
                    if cleaned_line and "See" not in cleaned_line:
                        data[current_section][str(index)] = cleaned_line
                        index += 1

            return data

    
    class Chatgpt:
        def _format_dict(self, name: str, data: dict) -> str:
            if not data:
                return f"## {name} Data:\nNo data available.\n"
            
            formatted = f"## {name} Data:\n"
            for key, value in data.items():
                formatted += f"- {key}: {value}\n"
            return formatted + "\n"

        def _build_prompt(self, ticker: str, zacks: dict, tv: dict, yf: dict, finviz: dict, sws: dict) -> str:
            sections = [
                self._format_dict("Zacks", zacks),
                self._format_dict("TradingView", tv),
                self._format_dict("Yahoo Finance", yf),
                self._format_dict("Finviz", finviz),
                self._format_dict("SimplyWallStreet", sws)
            ]

            return f"""You are a professional financial analyst. Analyze the stock {ticker.upper()}
            using the following structured data from four sources: {''.join(sections)}. 
            Please provide:
            1. A concise summary of the stock's financial and technical status.
            2. Key strengths and weaknesses found in the data.
            3. A clear investment recommendation (e.g., Strong Buy, Buy, Hold, Sell, Strong Sell).
            4. A one-sentence justification for your recommendation.
            Remember to mention in capital letters that what you provide is not a financial advice before you analysis.
            """

        def _send_prompt(self, ticker, prompt):
            if not prompt:
                raise ValueError("Prompt is required.")
            if ticker.lower() not in prompt.lower():
                raise ValueError("Prompt must mention the relevant stock ticker.")

            client = Client()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                web_search=False
            )
            return response.choices[0].message.content

        def get_ticker_info(self, ticker: str, zacks: dict, tv: dict, yf: dict, finviz: dict, sws: dict):
            prompt = self._build_prompt(ticker, zacks, tv, yf, finviz, sws)
            return self._send_prompt(ticker, prompt)
        


