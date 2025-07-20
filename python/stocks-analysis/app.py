#!/usr/bin/env python3

from stock_scrapper import TickerAnalyzer

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

import urllib3
import pandas as pd
import math

urllib3.disable_warnings()

ta = TickerAnalyzer()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

def sanitize_for_json(obj):
    if isinstance(obj, dict):
        return {k: sanitize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v) for v in obj]
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    elif isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    return obj


def handle_image(image_base64):
    image_data = None
    if image_base64:
        image_data = f"data:image/png;base64,{image_base64}"

    return image_data


@app.get("/")
def root():
    try:
        with open("static/index.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return JSONResponse(
            status_code=404,
            content={"error": "static/index.html not found"}
        )


@app.get("/Zacks/{ticker}")
def zacks(ticker: str):
    summary = ta.get_zacks_info(ticker)

    image_base64 = summary.pop("image", None)

    return JSONResponse({
        "summary": sanitize_for_json(summary),
        "image": handle_image(image_base64)
    })


@app.get("/TradingView/{ticker}")
def tradingview(ticker: str):
    summary = ta.get_tradingview_info(ticker)

    return JSONResponse({
        "summary": sanitize_for_json(summary),
    })


@app.get("/YahooFinance/{ticker}")
def yahoofinance(ticker: str):
    summary = ta.get_yf_info(ticker)
    return JSONResponse({"summary": sanitize_for_json(summary)})


@app.get("/Finviz/{ticker}")
def finviz(ticker: str):
    summary = ta.get_finviz_info(ticker)
    return JSONResponse({"summary": sanitize_for_json(summary)})


@app.get("/SimplyWallStreet/{ticker}")
def simplywallstreet(ticker: str):
    summary = ta.get_sws_info(ticker)

    image_base64 = summary.pop("image", None)

    return JSONResponse({
        "summary": sanitize_for_json(summary),
        "image": handle_image(image_base64)
    })


@app.get("/StockAnalysis/{ticker}")
def stockanalysis(ticker: str):
    summary = ta.get_sa_info(ticker)

    image_base64 = summary.pop("image", None)

    return JSONResponse({
        "summary": sanitize_for_json(summary),
        "image": handle_image(image_base64)
    })


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ChatGPT/{ticker}")
async def chatgpt(ticker: str, request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        if not prompt:
            return JSONResponse(status_code=400, content={"error": "Prompt is required."})

        summary = ta.get_chatgpt_info(ticker)
        return JSONResponse({"summary": sanitize_for_json(summary)})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
