#!/usr/bin/env python3

import urllib3
import pandas as pd
import math
import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse
import asyncio
import bcrypt
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from stock_scrapper import TickerAnalyzer

urllib3.disable_warnings()

PIN_FILE = Path(".pswd.txt")
if not PIN_FILE.exists():
    raise RuntimeError("❌ .pswd.txt not found. Run create_pswd.sh first.")
SECRET_PIN = PIN_FILE.read_text().strip().encode()


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


@app.post("/validate_pin")
def validate_pin(payload: dict):
    user_pin = payload.get("pin", "").encode()
    if bcrypt.checkpw(user_pin, SECRET_PIN):
        ta.clear_cache()
        return {"success": True}
    return {"success": False}


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

@app.get("/Reddit/{ticker}")
def reddit(ticker: str):
    summary = ta.get_rdt_info(ticker)
    return JSONResponse({"summary": sanitize_for_json(summary)})



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ChatGPTStream/{ticker}")
async def chatgpt_stream(ticker: str, request: Request):
    alias_to_name = {"zacks": "Zacks", "tv": "TradingView", "yf": "Yahoo Finance", 
                     "finviz": "Finviz", "sws": "Simply Wall Street", "sa": "StockAnalysis", 
                     "rdt": "Reddit"}

    async def event_generator():
        finished = {k: False for k in alias_to_name}
        total_sources = len(finished)
        removed = []
        try:
            task = asyncio.create_task(ta.gather_chatgpt_info(ticker, finished))
            num_no_finished = total_sources
            while num_no_finished > 0:
                if await request.is_disconnected():
                    break

                finished_tasks = [src for src, done in finished.items() if done and src not in removed]
                num_no_finished -= len(finished_tasks)

                for src in finished_tasks:
                    removed.append(src)
                    percent = int((len(removed) / total_sources) * 100)
                    yield {
                        "event": "progress",
                        "data": json.dumps({"source": alias_to_name[src], "progress": percent})
                    }
                
                if num_no_finished == 0:
                    yield {
                        "event": "status",
                        "data": json.dumps({"data": "Running ChatGPT analysis..."})
                    }

                await asyncio.sleep(0.1)

            sources_data = await task

            for chunk in ta.chatgpt.get_ticker_info(ticker, *sources_data):
                if await request.is_disconnected():
                    break
                yield {
                    "event": "stream",
                    "data": json.dumps({"chunk": chunk})
                }

            yield {
                "event": "status",
                "data": json.dumps({"data": "ChatGPT analysis was successful!"})
            }

        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)})
            }

    return EventSourceResponse(event_generator())