
import requests
from abc import ABC
import asyncio
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
from finvizfinance.screener.overview import Overview
from g4f.client import Client
import threading

import tickers_constants

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"
lock = threading.Lock()


def get_screen_size():
    try:
        import pyautogui
        return pyautogui.size()
    except Exception as e:
        return (1920, 1080)

def get_and_crop_screenshot(url, x, y, w, h, timeout=5000):
    options = {
        "javascript-delay": str(timeout),  # wait 5 seconds for JS
        "no-stop-slow-scripts": "",
        "enable-javascript": "",
        "width": "1280",  # or adjust based on your needs
    }

    width, height = get_screen_size()

    config = imgkit.config(wkhtmltoimage="/usr/bin/wkhtmltoimage") # First install - sudo apt-get install wkhtmltopdf

    img_bytes = imgkit.from_url(url, False, config=config, options=options)

    # screen resolution is based on a 1920x1080 size, so we need to adjust for the current screen resolution
    scale_x = width / 1920
    scale_y = height / 1080
    crop_box = (x * scale_x, y * scale_y, w * scale_x, h * scale_y)

    full_screenshot = Image.open(BytesIO(img_bytes))

    return full_screenshot, full_screenshot.crop(crop_box)


def get_display_image(cropped_img: Image):
    buffer = BytesIO()
    cropped_img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


class TickerAnalyzer:
    def __init__(self):
        self.curr_ticker = ""
        self.cache = {"zacks" : {}, "tv" : {}, "yf" : {}, "finviz" : {}, "sws" : {}, "sa" : {}, "rdt" : {}, "chatgpt" : {}}
        self.zacks = self.Zacks()
        self.tv = self.Tradingview()
        self.yf = self.YahooFinance()
        self.finviz = self.Finviz()
        self.sws = self.SimplyWallStreet()
        self.sa = self.StockAnalysis()
        self.rdt = self.Reddit()
        self.chatgpt = self.Chatgpt()

    def clear_cache(self):
        for source in self.cache.keys():
            self.cache[source] = {}

    def get_zacks_info(self, ticker: str):
        if self.cache["zacks"] and ticker in self.cache["zacks"].keys():
            return self.cache["zacks"][ticker]
        else:
            zacks_ret =  self.zacks.get_ticker_info(ticker)
            if "msg" not in zacks_ret.keys():
                if len(self.cache["zacks"]) == 20:
                    lock.acquire()
                    _, _ = self.cache["zacks"].popitem(last=False)
                    lock.release()
                lock.acquire()
                self.cache["zacks"].update({ticker : zacks_ret})
                lock.release()

            return zacks_ret

    def get_tradingview_info(self, ticker: str):
        if self.cache["tv"] and ticker in self.cache["tv"].keys():
            return self.cache["tv"][ticker]
        else:
            tv_ret =  self.tv.get_ticker_info(ticker)
            if len(self.cache["tv"]) == 20:
                lock.acquire()
                _, _ = self.cache["tv"].popitem(last=False)
                lock.release()
            lock.acquire()
            self.cache["tv"].update({ticker : tv_ret})
            lock.release()

            return tv_ret
    
    def get_yf_info(self, ticker: str):
        if self.cache["yf"] and ticker in self.cache["yf"].keys():
            return self.cache["yf"][ticker]
        else:
            yf_ret = self.yf.get_ticker_info(ticker)
            if len(self.cache["yf"]) == 20:
                lock.acquire()
                _, _ = self.cache["yf"].popitem(last=False)
                lock.release()
            lock.acquire()
            self.cache["yf"].update({ticker : yf_ret})
            lock.release()

            return yf_ret

    def get_finviz_info(self, ticker: str):
        if self.cache["finviz"] and ticker in self.cache["finviz"].keys():
            return self.cache["finviz"][ticker]
        else:
            finviz_ret = self.finviz.get_ticker_info(ticker)
            if len(self.cache["finviz"]) == 20:
                lock.acquire()
                _, _ = self.cache["finviz"].popitem(last=False)
                lock.release()
            lock.acquire()
            self.cache["finviz"].update({ticker : finviz_ret})
            lock.release()

            return finviz_ret

    def get_sws_info(self, ticker: str):
        if self.cache["sws"] and ticker in self.cache["sws"].keys():
            return self.cache["sws"][ticker]
        else:
            sws_ret = self.sws.get_ticker_info(ticker)
            if len(self.cache["sws"]) == 20:
                lock.acquire()
                _, _ = self.cache["sws"].popitem(last=False)
                lock.release()
            lock.acquire()
            self.cache["sws"].update({ticker : sws_ret})
            lock.release()

            return sws_ret
        
    def get_sa_info(self, ticker: str):
        if self.cache["sa"] and ticker in self.cache["sa"].keys():
            return self.cache["sa"][ticker]
        else:
            sa_ret = self.sa.get_ticker_info(ticker)
            if len(self.cache["sa"]) == 20:
                lock.acquire()
                _, _ = self.cache["sa"].popitem(last=False)
                lock.release()
            lock.acquire()
            self.cache["sa"].update({ticker : sa_ret})
            lock.release()

            return sa_ret
        
    def get_rdt_info(self, ticker: str):
        if self.cache["rdt"] and ticker in self.cache["rdt"].keys():
            return self.cache["rdt"][ticker]
        else:
            rdt_ret = self.rdt.get_ticker_info(ticker)
            if len(self.cache["rdt"]) == 20:
                lock.acquire()
                _, _ = self.cache["rdt"].popitem(last=False)
                lock.release()
            lock.acquire()
            self.cache["rdt"].update({ticker : rdt_ret})
            lock.release()

            return rdt_ret

    async def gather_chatgpt_info(self, ticker: str, finished: dict):
        if self.cache["chatgpt"] and ticker in self.cache["chatgpt"].keys():
            return self.cache["chatgpt"][ticker]
        
        non_valid_msg = {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}
        
        source_methods = {
            "zacks": self.zacks,
            "tv": self.tv,
            "yf": self.yf,
            "finviz": self.finviz,
            "sws": self.sws,
            "sa": self.sa,
            "rdt": self.rdt
        }

        futures = {}
        non_valid_count = 0

        loop = asyncio.get_event_loop()

        for source, obj in source_methods.items():
            if ticker not in self.cache[source]:
                futures[source] = asyncio.create_task(asyncio.to_thread(obj.get_ticker_info, ticker))
            else:
                finished[source] = True
        
        while futures:
            to_remove = []
            for source, future in futures.items():
                if future.done():
                    finished[source] = True
                    try:
                        result = future.result()
                        if result == non_valid_msg:
                            non_valid_count+=1
                        self.cache[source][ticker] = result
                    except Exception as e:
                        error_result = {"error": str(e)}
                        self.cache[source][ticker] = error_result

                    to_remove.append(source)

            for source in to_remove:
                futures.pop(source)

            await asyncio.sleep(0.1)

        if non_valid_count == len(source_methods):
            non_valid_count = 0
            return non_valid_msg

        non_valid_count = 0

        return [self.cache[source][ticker] for source in source_methods]
    

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
                    data_dict.update({"name" : data["name"]})
                    data_dict.update({"ticker" : data["ticker"]})
                    data_dict.update({"zacks rank" : f"{data['zacks_rank']} ({data['zacks_rank_text']})"})
                    data_dict.update({"Forward P/E" : data["source"]["sungard"]["pe_ratio"]})

                    data_dict.update({"dividend_freq" : data["source"]["sungard"]["dividend_freq"]})
                    data_dict.update({"dividend_yield" : data["dividend_yield"]+"%"})
                    data_dict.update({"dividend" : data["source"]["sungard"]["dividend"]})
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
            url = f"https://www.zacks.com/stock/quote/{ticker}?q={ticker}"

            _, cropped_img = get_and_crop_screenshot(url, 330, 180, 1145, 480)

            return get_display_image(cropped_img)


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

                    self.summary.update({"Analysis" : analysis.summary})

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
            indicators_list = ["TTM", "indicated", "FY"]
            while (index < len(ks_string_list) - 1):
                if ks_string_list[index] == "":
                    index = index + 1
                else:
                    if index == len(ks_string_list) - 1:
                        key_stats[ks_string_list[index]] = ""
                        index = index + 1
                    else:
                        if any(word in ks_string_list[index] for word in indicators_list) and \
                        any(word in ks_string_list[index+1] for word in indicators_list):
                            key_stats[ks_string_list[index]] = ""
                            index = index + 1
                        elif ks_string_list[index+1] == "" and \
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

                if str == "forecast":
                    text = pytesseract.image_to_string(cropped_img)
                    match = re.search(r"\d+\.\d+", text)
                    if match:
                        price_target = float(match.group())
                        last_price = float(analysis.indicators["close"])
                        shared["Last closing price"] = last_price
                        shared["Price target"] = price_target
                        potential =  round((((price_target - last_price) / last_price) * 100), 2)
                        shared["Potential %"] = f"{potential}%"

                else:
                    text = pytesseract.image_to_string(cropped_img)
                    
                    pattern = r"(Key stats.*?(?:Beta \(1Y\)|Expense ratio)[^\d\-]*[-+]?\d*\.?\d+)"
                    match = re.search(pattern, text, re.DOTALL)
                    if match:
                        key_stats_raw = match.group(1)
                        key_stats_words = key_stats_raw.split("\n")
                        for i, word in enumerate(key_stats_words):
                            key_stats_words[i] = word.replace(" >", "").replace("uso", "").replace(" M", "M").replace(" B", "B")
                        key_stats = {}

                        self._adjust_ks_string(key_stats_words, key_stats)

                        shared["Key stats"] = key_stats

            except Exception as e:
                print(f"{e}please try again if any data is missing...")

        
        def _get_tv_stats_from_image(self, ticker: str, exchange: str, analysis: dict):
            url = f"https://www.tradingview.com/symbols/{exchange}-{ticker}/"
            forecast_url = url + "forecast/"

            options = {
                "javascript-delay": "5000",
                "load-error-handling": "ignore",
                "no-stop-slow-scripts": "",
                "enable-javascript": "",
                "width": "1280",  # or adjust based on your needs
            }

            config = imgkit.config(wkhtmltoimage="/usr/bin/wkhtmltoimage")

            stats_and_price_target = {}

            width, height = get_screen_size()

            scale_x = width / 1920
            scale_y = height / 1080

            with ThreadPoolExecutor() as executor:
                future_ks  = executor.submit(
                    self._render_imgkit,
                    url, config, options,
                    (15 * scale_x, 1375 * scale_y, 315 * scale_x, 2600 * scale_y),
                    "ks", stats_and_price_target
                )
                future_forecast = executor.submit(
                    self._render_imgkit,
                    forecast_url, config, options,
                    (19 * scale_x, 654 * scale_y, 199 * scale_x, 732 * scale_y),
                    "forecast", stats_and_price_target, analysis
                )

            future_ks.result()
            future_forecast.result()
            
            self.summary.update(stats_and_price_target)
                     

    class YahooFinance(Source):
        def __init__(self):
            super().__init__()
            self.attributes = ["analyst_price_targets", "news", "recommendations_summary", "upgrades_downgrades"]

        def get_ticker_info(self, ticker: str):
            try:
                ticker_uppercase = ticker.upper()
                self.ticker = yf.Ticker(ticker_uppercase)
                for attr in dir(self.ticker):
                    if attr in self.attributes and not attr == "news":
                        attr_value = getattr(self.ticker, attr)
                        self._not_news_attr_handeling(attr, attr_value, ticker_uppercase)
                        
                    elif attr == "news":
                        self._news_attr_handeling(attr)
        
            except Exception as e:
                print(f"Error msg: {e}.")
                
                
            if not self.summary["News"] and not self.summary["recommendations"] and not self.summary["Upgrades & downgrades"]:
                price, _ = self.summary["Price target"]
                if not price:
                    self.summary = {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}
            
            return self.summary
        
        def _news_attr_handeling(self, attr):
            recent_news_dict = {}
            for news in getattr(self.ticker, attr):
                content = news["content"]
                curr_date = datetime.now()
                year, month, _ = content["pubDate"].split("-")
                if (int(year) == curr_date.year or (int(year) == curr_date.year - 1 and abs(curr_date.month -  int(month)) > 6)):
                    for key in ["id", "description", "displayTime", "isHosted", 
                                "bypassModal", "previewUrl", "thumbnail", "provider", 
                                "clickThroughUrl", "metadata", "finance", "storyline"]:
                        _ = content.pop(key)

                    content_type = content.pop("contentType")
                    raw_url_data = content.pop("canonicalUrl")
                    content["url"] = raw_url_data["url"]
                    recent_news_dict.update({content_type : content})


            news = {
                str(k): v for k, v in recent_news_dict.items()
            }
            self.summary.update({"News" : news})
        
        def _upgrades_downgrades(self, attr_value):
                upgrades_dict = attr_value.to_dict(orient="index")
                recent_upgrades_dict = {}
                for date, values in upgrades_dict.items():
                    if date.year >= datetime.now().year - 1:
                        recent_upgrades_dict.update({date : values})

                upgrades = {
                    str(k): v for k, v in recent_upgrades_dict.items()
                }

                self.summary.update({"Upgrades & downgrades" : upgrades})


        def _recommendations(self, attr_value):
            self.summary.update({"recommendations" : {}})
            recommendations_dict = attr_value.to_dict(orient="index")
            for (key, value) in recommendations_dict.items():
                _ = value.pop("period")
                self.summary["recommendations"].update({f"{key}-Month" : value})


        def _analyst_price_targets(self, attr_value, ticker_uppercase):
            conclusion = None
            if "low" in attr_value and attr_value["current"] < attr_value["low"]:
                conclusion = f"{ticker_uppercase} trades lower than low target! seems undervalued."
            elif "high" in attr_value and attr_value["current"] >= attr_value["high"]:
                conclusion = f"{ticker_uppercase} trades higher than high target! seems overvalued."
            else:
                conclusion = f"{ticker_uppercase} trades within range."
            
            reccomendation_and_conclusion = (attr_value, conclusion)

            self.summary.update({"Price target" : reccomendation_and_conclusion})
        

        def _not_news_attr_handeling(self, attr, attr_value, ticker_uppercase):
            if attr == "analyst_price_targets":
                self._analyst_price_targets(attr_value, ticker_uppercase)

            self._get_otm_calls()

            if attr == "recommendations_summary":
                self._recommendations(attr_value)

            elif attr == "upgrades_downgrades":
                self._upgrades_downgrades(attr_value)


        def _get_otm_calls(self, otm_threshold: float=1.2):
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

                try:
                    fundament = stock.ticker_fundament()
                    
                    for attr in tickers_constants.FINVIZ_ATTR_LIST:
                        try:
                            _ = fundament.pop(attr)
                        except:
                            continue

                    self.summary.update({"General info" : fundament})
                except:
                    pass

                curr_date = datetime.now()

                try:
                    ratings_outer = stock.ticker_outer_ratings()
                    self._upgrades_downgrades(curr_date, ratings_outer)
                except:
                    pass

                try:
                    news = stock.ticker_news()
                    self._news(curr_date, news)
                except:
                    pass

                insiders_dict = {}

                try:
                    for key, insider in stock.ticker_inside_trader().to_dict(orient="index").items():
                        if str(curr_date.year)[-2:] in insider["Date"] or str(int(curr_date.year)-1)[-2:] in insider["Date"]:
                            insider_name = insider.pop("Insider Trading")
                            insiders_dict.update({insider_name : insider})

                    insiders = {
                        str(k): v for k, v in insiders_dict.items()
                    }

                    self.summary.update({"Insiders trading" : insiders})
                except:
                    pass
            
            except Exception as e:
                print(f"Error msg: {e}")
                self.summary = {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}

            return self.summary

        
        def _news(self, curr_date, news_raw):
            news_dict = news_raw.to_dict(orient="index")
            recent_news_dict = {}
            
            for key, news in news_dict.items():
                date = news.pop("Date")
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

            self.summary.update({"News" : news})

        
        def _upgrades_downgrades(self, curr_date, ratings_outer):
            upgrades_dict = ratings_outer.to_dict(orient="index")
            recent_upgrades_dict = {}
            for key, values in upgrades_dict.items():
                date = values.pop("Date")
                updgrade_downgrade_year = int(date.year)
                if updgrade_downgrade_year >= curr_date.year - 1:
                    recent_upgrades_dict.update({date : values})

            upgrades = {
                str(k): v for k, v in recent_upgrades_dict.items()
            }

            self.summary.update({"Upgrades/Downgrades" : upgrades})

    class SimplyWallStreet(Source):
        @lru_cache(maxsize=128)       
        def get_ticker_info(self, ticker: str):
            base_url = "https://simplywall.st/en/stocks/us"
            try:
                for industry in tickers_constants.SWS_INDUSTRIES:
                    for us_mkt in tickers_constants.SWS_US_MARKETS:
                        company_name = yf.Ticker(ticker).info["shortName"].lower()
                        adjusted_cpmpany_name = self._normalize_company_name(company_name)
                        adjusted_cpmpany_name = adjusted_cpmpany_name.replace(",", "").replace(".", "").replace("&", "").replace(" ", "-").replace("--", "-")
                        adjusted_cpmpany_name = adjusted_cpmpany_name[:-1] if adjusted_cpmpany_name[-1] == "-" else adjusted_cpmpany_name

                        url = f"{base_url}/{industry}/{us_mkt}-{ticker.lower()}/{adjusted_cpmpany_name}"

                        if not self._is_valid_simplywallstreet_url(url, random.choice(tickers_constants.USER_AGENTS_LIST)):
                            continue

                        full_screenshot, cropped_img = get_and_crop_screenshot(url, 344, 712, 1175, 1490)

                        width, height = cropped_img.size
                        mid_height = height // 2 

                        bottom_half = cropped_img.crop((0, mid_height, width, height))

                        gray = bottom_half.convert("L")
                        sharpened = gray.filter(ImageFilter.SHARPEN)
                        contrast = ImageEnhance.Contrast(sharpened).enhance(2.0)
                        inverted = ImageOps.invert(contrast)
                        binarized = inverted.point(lambda x: 255 if x > 128 else 0, mode="1")
                        binarized = binarized.resize((binarized.width * 2, binarized.height * 2))
                        text = pytesseract.image_to_string(binarized)
                        text_dict = self._extract_sections(text)

                        if text_dict:
                            top_half = cropped_img.crop((0, 0, width, mid_height))

                            if "Rewards" in text_dict.keys():
                                self.summary.update({"Rewards" : text_dict["Rewards"]})
                            if "Risk Analysis" in text_dict.keys():
                                self.summary.update({"Risk Analysis" : text_dict["Risk Analysis"]})

                            self.summary.update({"image" : get_display_image(top_half)})
                        else:
                            self.summary.update({"OCR error:" : "OCR retrieval was not successful"})

                        return self.summary
            except Exception as e:
                pass
                
            if not self.summary:
                return {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}


        def _normalize_company_name(self, name):
            pattern = r"\b(?:" + "|".join(tickers_constants.COMMON_SUFFIXES) + r")\b\.?,?"
            name = re.sub(pattern, "", name, flags=re.IGNORECASE)
            return name
        

        def _is_valid_simplywallstreet_url(self, url: str, user_agent: str):
            headers = {"User-Agent": user_agent}
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
                    cleaned_line = re.sub(r"^(\*|¥|@|¥e|xe|ve|e\s|%\s|%*|=\s|[-•→©\u2022]|\s)+", "", line, flags=re.IGNORECASE)
                    if cleaned_line and "See" not in cleaned_line:
                        data[current_section][str(index)] = cleaned_line
                        index += 1

            return data


    class StockAnalysis(Source):
        def get_ticker_info(self, ticker: str):
            try:
                url = f"https://stockanalysis.com/stocks/{ticker.lower()}/forecast/"

                full_screenshot, cropped_img = get_and_crop_screenshot(url, 23, 1173, 1191, 1690)

                text = pytesseract.image_to_string(cropped_img)
                
                if text:
                    lines = text.splitlines()
                    price_target = next((line for line in lines if line.strip().startswith("Price Target:")), None)
                    analysts_consensus = next((line for line in lines if line.strip().startswith("Analyst Consensus:")), None)

                    if price_target:
                        self.summary.update({"Price target" : price_target.split(": ", 1)[1]})
                    if analysts_consensus:
                        self.summary.update({"Analyst consensus" : analysts_consensus.split(": ", 1)[1]})
                    self.summary.update({"image" : get_display_image(full_screenshot.crop((23, 1173, 1191, 2650)))})
                else:
                    self.summary = {"msg" : f"{ticker.upper()} retrieval failed."}
            except Exception as e:
                print(e)
                self.summary = {"msg" : f"{ticker.upper()} is not a valid stock ticker. Please provide a valid stock ticker"}

            return self.summary


    class Reddit(Source):
        def get_ticker_info(self, ticker: str):
            reddit_url = f"https://www.reddit.com/search.json?q={ticker.lower()}&type=posts&sort=relevance"

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/115.0.0.0 Safari/537.36",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Referer": "https://www.reddit.com/",
                "Connection": "keep-alive"
            }

            proxies = {
                "http": "socks5h://127.0.0.1:9050",
                "https": "socks5h://127.0.0.1:9050"
            }

            try:
                response = requests.get(
                    reddit_url,
                    headers=headers,
                    proxies=proxies,
                    timeout=15
                )

                if response.status_code == 429:
                    import os
                    os.system("systemctl restart tor@default")
                    time.sleep(1.5)
                    response = requests.get(reddit_url, headers=headers, proxies=proxies, timeout=15)

                if response.status_code != 200:
                    return {"error": f"Failed to fetch Reddit posts. Status: {response.status_code}"}

                data = response.json()
                children = data.get("data", {}).get("children", [])

                top_10_urls = [
                    f"https://www.reddit.com{child['data']['permalink']}"
                    for child in children[:15]
                ]

                self.summary.update({"Top discussions": top_10_urls})
                return self.summary

            except Exception as e:
                return {"error": str(e)}
        

    class Chatgpt:
        def _format_dict(self, name: str, data: dict) -> str:
            if not data:
                return f"## {name} Data:\nNo data available.\n"
            
            formatted = f"## {name} Data:\n"
            for key, value in data.items():
                formatted += f"- {key}: {value}\n"
            return formatted + "\n"

        def _build_prompt(self, ticker: str, zacks: dict, tv: dict, yf: dict, finviz: dict, sws: dict, sa: dict, rdt: dict) -> str:
            sections = [
                self._format_dict("Zacks", zacks),
                self._format_dict("TradingView", tv),
                self._format_dict("Yahoo Finance", yf),
                self._format_dict("Finviz", finviz),
                self._format_dict("SimplyWallStreet", sws),
                self._format_dict("StockAnalysis", sa),
                self._format_dict("Reddit", rdt)
            ]

            return f"""You are a professional financial analyst. Analyze the stock {ticker.upper()}
            using the following structured data from {len(sections)} sources: {"".join(sections)}. 
            Please provide:
            1. A concise summary of the stock's financial and technical status.
            2. Key strengths and weaknesses found in the data.
            3. A clear investment recommendation (e.g., Strong Buy, Buy, Hold, Sell, Strong Sell).
            4. A one-sentence justification for your recommendation.
            Make sure you keep you answer for each clause up to 5 lines.
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
                web_search=False,
                stream=True
            )

            for chunk in response:
                delta = chunk.choices[0].delta
                if hasattr(delta, "content") and delta.content:
                    yield delta.content

        def get_ticker_info(self, ticker: str, zacks: dict, tv: dict, yf: dict, finviz: dict, sws: dict, sa: dict, rdt: dict):
            prompt = self._build_prompt(ticker, zacks, tv, yf, finviz, sws, sa, rdt)
            return self._send_prompt(ticker, prompt)