#!/usr/bin/env python3

import readline

from stock_scrapper import TickerAnalyzer
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
import urllib3
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

urllib3.disable_warnings()

ta = TickerAnalyzer()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    with open("static/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/zacks/{ticker}")
def zacks(ticker: str):
    summary = ta.get_zacks_info(ticker)

    image_filename = f"style_scores_{ticker.upper()}.png"
    image_url = f"/static/images/{image_filename}"

    return JSONResponse({
        "summary": summary,
        "image_url": image_url
    })


@app.get("/tradingview/{ticker}")
def tradingview(ticker: str):
    summary = ta.get_tradingview_info(ticker)

    image_filename = f"{ticker.upper()}_ks.png"

    image_url = f"/static/images/{image_filename}"

    return JSONResponse({
        "summary": summary,
        "image_url": image_url
    })


@app.get("/yahoofinance/{ticker}")
def zacks(ticker: str):
    summary = ta.get_yf_info(ticker)
    return JSONResponse({"summary": summary})

@app.get("/finviz/{ticker}")
def finviz(ticker: str):
    summary = ta.get_finviz_info(ticker)
    return JSONResponse({"summary": summary})


# CORS to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend's origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chatgpt/{ticker}")
async def chatgpt(ticker: str, request: Request):
    try:
        data = await request.json()
        prompt = data.get("prompt", "")
        if not prompt:
            return JSONResponse(status_code=400, content={"error": "Prompt is required."})

        # Get the summary from your Chatgpt class logic
        summary = ta.get_chatgpt_info(ticker, prompt)
        return JSONResponse({"summary": summary})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})