# 📊 Stock Analyzer

An interactive web-based stock analyzer app built with **FastAPI** and **vanilla JavaScript + Tailwind CSS**.

Query live data from **Zacks**, **TradingView**, **Yahoo Finance**, **Finviz**, and **ChatGPT** — all through a sleek frontend and Python-powered backend.

---

## ⚠️ Disclaimer

This application is **not intended to provide financial advice**.

It is strictly for **educational and non-commercial use only**.

All data is sourced from third-party services:

- [Zacks](https://www.zacks.com/)
- [TradingView](https://www.tradingview.com/)
- [Yahoo Finance](https://finance.yahoo.com/)
- [Finviz](https://finviz.com/)
- [ChatGPT](https://openai.com/)

Use of this application is **subject to the terms of use of each of the above services**.  
Always conduct your own research and consult a licensed financial advisor before making investment decisions.



## 🚀 Features

- 🔍 Lookup a stock ticker across:
  - Zacks
  - TradingView
  - Yahoo Finance
  - Finviz
- 🧠 Generate stock-specific insights using a custom **ChatGPT prompt**
- 🌐 Clean and responsive UI with Tailwind CSS
- 📈 Automatically renders JSON responses into human-readable HTML
- 🔗 Hyperlink and Markdown support for rich text formatting

---

## 🧩 Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
- **Frontend:** HTML + JavaScript + TailwindCSS
- **Data Parsing:** Custom `TickerAnalyzer` class (from `stock_scrapper.py`)
- **Markdown Rendering:** Custom `markdownToHtml()` function

---

## 🖼️ UI Preview

> Enter a ticker symbol, click a data source, and get back structured financial data. You can also submit a free-form ChatGPT prompt.

---

## 📁 Project Structure

├── main.py # FastAPI backend
├── static/
│ ├── index.html # Main frontend page
│ ├── images/ # Zacks image assets (e.g., style scores)
│ └── ... # CSS/JS if separated later
└── stock_scrapper.py # Your custom class for fetching data

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/stock-analyzer.git
cd stock-analyzer
```

### 2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r ta_installs.txt
```

### 4. Run the backend server
```bash
./run_web.sh
```

Server will run at: http://127.0.0.1:8000

