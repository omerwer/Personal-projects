#!/usr/bin/env python3

from stock_scrapper import TickerAnalyzer
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import urllib3
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
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
            return None  # Or 0.0 or "N/A" depending on your preference
        return obj
    return obj

@app.get("/")
def root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/Zacks/{ticker}")
def zacks(ticker: str):
    summary = ta.get_zacks_info(ticker)

    image_filename = f"style_scores_{ticker.upper()}.png"
    image_url = f"/static/images/{image_filename}"

    return JSONResponse({
        "summary": sanitize_for_json(summary),
        "image_url": image_url
    })


@app.get("/TradingView/{ticker}")
def tradingview(ticker: str):
    summary = ta.get_tradingview_info(ticker)

    return JSONResponse({
        "summary": sanitize_for_json(summary),
    })


@app.get("/YahooFinance/{ticker}")
def zacks(ticker: str):
    summary = ta.get_yf_info(ticker)
    return JSONResponse({"summary": sanitize_for_json(summary)})


@app.get("/Finviz/{ticker}")
def finviz(ticker: str):
    summary = ta.get_finviz_info(ticker)
    return JSONResponse({"summary": sanitize_for_json(summary)})


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

        summary = ta.get_chatgpt_info(ticker, prompt)
        return JSONResponse({"summary": sanitize_for_json(summary)})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})