import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Trending Stocks & Political Tracker", layout="wide")
st.title("📈 Stock Intelligence Dashboard")
st.subheader("AI-Driven Reddit Buzz & Congressional Portfolio Intelligence")
st.markdown("---")

BACKEND_URL = "http://127.0.0.1:8000/api"

# ==========================================
# MEMORY INITIALIZATION (SESSION STATE)
# ==========================================
# This keeps the data loaded by one button from being deleted when the other is clicked.
if "reddit_data" not in st.session_state:
    st.session_state.reddit_data = None

if "politician_data" not in st.session_state:
    st.session_state.politician_data = None


col1, col2 = st.columns(2)

# ==========================================
# COLUMN 1: RETAIL SENTIMENT
# ==========================================
with col1:
    st.header("💬 Retail Forum Sentiment (Small/Mid-Cap)")
    
    # Trigger API fetch and store result in session state
    if st.button("Fetch from Reddit", type="primary", use_container_width=True):
        with st.spinner("Gemini Agent filtering for Small & Mid-Cap traffic..."):
            try:
                res = requests.get(f"{BACKEND_URL}/reddit-trending", timeout=60)
                if res.status_code == 200:
                    data = res.json()
                    if data:
                        df = pd.DataFrame(data)
                        df.columns = ["Stock Ticker", "Market Cap Category", "Mention Frequency", "AI Sentiment Synthesis"]
                        st.session_state.reddit_data = df  # Save to memory
                    else:
                        st.session_state.reddit_data = "No active small/mid-cap trends parsed in this window."
                else:
                    st.error(f"Backend processing failure. Status: {res.status_code}")
            except requests.exceptions.Timeout:
                st.error("The request timed out. The LLM parsing took longer than 60 seconds to respond.")
            except Exception as e:
                st.error(f"Could not connect to service pipeline: {e}")

    # Render data from persistent memory space if available
    if st.session_state.reddit_data is not None:
        if isinstance(st.session_state.reddit_data, str):
            st.info(st.session_state.reddit_data)
        else:
            st.dataframe(st.session_state.reddit_data, use_container_width=True, hide_index=True)


# ==========================================
# COLUMN 2: CAPITOL DISCLOSURES
# ==========================================
with col2:
    st.header("🏛️ Capitol Disclosures Tracker (QuiverQuant)")
    
    # Trigger API fetch and store result in session state
    if st.button("Fetch Politician Activities", type="primary", use_container_width=True):
        with st.spinner("Gemini Agent auditing QuiverQuant legislative transaction feeds (Last 3 Months)..."):
            try:
                res = requests.get(f"{BACKEND_URL}/politician-trades", timeout=60)
                if res.status_code == 200:
                    data = res.json()
                    if data:
                        df = pd.DataFrame(data)
                        df = df[["name", "role", "activity_date", "asset", "transaction_type", "amount_range"]]
                        df.columns = ["Politician Name", "Committee / Legislative Role", "Activity Date", "Traded Asset", "Transaction Type", "Value Bracket Tier"]
                        st.session_state.politician_data = df  # Save to memory
                    else:
                        st.session_state.politician_data = "No disclosures recorded."
                else:
                    st.error(f"Backend processing failure. Status: {res.status_code}")
            except requests.exceptions.Timeout:
                st.error("The request timed out. The LLM parsing took longer than 60 seconds to respond.")
            except Exception as e:
                st.error(f"Could not connect to service pipeline: {e}")

    # Render data from persistent memory space if available
    if st.session_state.politician_data is not None:
        if isinstance(st.session_state.politician_data, str):
            st.info(st.session_state.politician_data)
        else:
            st.dataframe(st.session_state.politician_data, use_container_width=True, hide_index=True)
