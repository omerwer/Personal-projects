
import requests
from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import os
import imgkit
from PIL import Image

class TickerAnalyzer:
    def __init__(self):
        self.zacks = None

    def get_zacks_info(self, ticker: str):
        self.zacks = self.Zacks()
        self.zacks.get_ticker_info(ticker)


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

            print(data_dict)

