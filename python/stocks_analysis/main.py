#!/usr/bin/env python3

import readline
import yfinance as yf

from stock_scrapper import TickerAnalyzer

# import urllib
# from fake_useragent import UserAgent
from bs4 import BeautifulSoup as BS
# import urllib
# import re
# import urllib.request
import requests
import os
import urllib3
urllib3.disable_warnings()

import imgkit

import re
from PIL import Image
import pytesseract
import matplotlib.pyplot as plt

def parse_style_scores_and_industry(text):
    style_scores = {}
    industry_info = {}

    # Parse style scores
    match = re.search(r'Style Scores:\s*([A-F])\s*Value\s*\|\s*([A-F])\s*Growth\s*\|\s*([A-F])\s*Momentum\s*\|\s*([A-F])\s*VGM', text)
    if match:
        style_scores = {
            'Value': match.group(1),
            'Growth': match.group(2),
            'Momentum': match.group(3),
            'VGM': match.group(4)
        }

    # Parse industry rank
    rank_match = re.search(r'Industry Rank:\s*Top\s*(\d+%)\s*\((.*?)\)', text)
    if rank_match:
        industry_info['Rank'] = f"Top {rank_match.group(1)} ({rank_match.group(2)})"

    industry_line = re.search(r'Industry:\s*(.*)', text)
    if industry_line:
        industry_info['Industry'] = industry_line.group(1).strip()

    return style_scores, industry_info


def main():
    ta = TickerAnalyzer()
    ticker = input("Please enter a ticker: ")
    # data = ta.zacks(ticker)
    # print(ta.zacks(ticker))
    # print(ta.get_url(ticker))

    # header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
    url = f'https://www.zacks.com/stock/quote/{ticker.upper()}?q={ticker.upper()}'
    # r = requests.get(url, headers=header, verify=False)
    # soups = BS(r.text,"lxml")

    # with open(f'{ticker}_content.txt', 'w', encoding='utf-8') as file:
    #     file.write(soups.prettify())

    # fetch_style_scores_screenshot(ticker)
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

    plt.imshow(cropped_img)
    plt.axis('off')
    plt.show()

    # Save or show the cropped image
    # cropped_img.save("cropped_style_scores.png")

    # text = pytesseract.image_to_string(cropped_img)
    # print(text)



if __name__ == "__main__":
    main()