# Stock Intelligence Dashboard 📈
An AI-driven equity intelligence dashboard that monitors retail sentiment trends alongside political portfolio activity. The application aggregates raw data streams from public financial forums and uses a Gemini LLM agent to extract actionable investment structures.

The backend leverages FastAPI to handle high-performance data processing and structuring via the modern Google GenAI SDK. The user interface is a responsive Streamlit architecture designed to retain metrics seamlessly across isolated operations using session memory states.

## Technical Features
### Retail Forum Parser 
Extracts real-time text arrays across several stock discussion groups anonymously without needing Reddit developer keys.

### Small & Mid-Cap Filter
Configured prompt architecture that excludes large/mega-cap tech companies to highlight small-to-mid-cap trading activity (market valuations under $10 Billion).

### Capitol Portfolio Audit
Implements a high-volume pipeline data structures to parse historical transactions over a 90-day window.

### Unified Single-Terminal Process Manager
Includes an asynchronous multi-threaded entry point (app.py) that manages both the REST API and UI servers simultaneously.

### Persistent Session State
Employs Streamlit session state memory buffers to prevent data from being cleared when interacting with different buttons.

## Directory Structure
#### ├── backend.py                 # FastAPI Application Server & Gemini SDK Layer</br>
#### ├── frontend.py                # Streamlit Web User Interface Modules</br>
#### ├── app.py                     # Single-Command Multiprocess Execution Entry Point</br>
#### └── README.md                  # System Documentation Guide</br>

## Setup & Local Installation Prereqs
This application is built to run entirely inside your configured project directory and isolated virtual environment.

#### 1. Initialize Context & Dependencies
Open your terminal workspace, navigate to your root directory, and activate your pre-existing environment:

```
cd /path/to/trending/stocks/folder
python3 -m venv trending_stocks
source trending_stocks_env/bin/activate
```

##### Upgrade pip and install the structural software requirements matrix
```
pip install --upgrade pip
pip install fastapi uvicorn google-genai requests streamlit pandas pydantic
```

#### 2. Obtain and Export Your Gemini API Token
Visit Google AI Studio and authenticate with your Google account.

Click Get API key, select or generate a standard project workspace, and copy your key.

Export the credential string straight into your active shell environment variables profile:
```
export GEMINI_API_KEY="AIzaSyYourExactGeneratedKeyStringHere"
```
Running the Application
```
python app.py
```

### What Occurs Automatically Under the Hood:
The script initializes an independent FastAPI instance on [http://127.0.0.1:8000](http://127.0.0.1:8000) via a background thread.

It pauses briefly to guarantee network socket bindings are secure.

It spawns the Streamlit user interface runner on http://localhost:8501 and opens your default web browser to the dashboard.

Graceful Teardown: Pressing Ctrl+C in your terminal intercepts system signals to shut down both processes simultaneously, keeping your local ports clear.

### Architecture Deep-Dive
Data Processing Pipe (backend.py)
Gemini Core Model Config: Runs on gemini-2.5-flash for high-speed analysis and utilizes structured response_schema enforcement to guarantee clean JSON outputs.

Network Stability: Configures explicit HttpOptions timeouts up to 60 seconds to ensure the connection stays open during complex parsing tasks.

### Interface State Management (frontend.py)
The application manages data display using st.session_state.reddit_data and st.session_state.politician_data.

When you click "Fetch Politician Activities", the page re-renders from top to bottom, but reads your previously loaded Reddit metrics from persistent memory to kep them visible on your screen.
