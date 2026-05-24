import sys
import subprocess
import time
import signal

processes = []

def kill_processes(signum, frame):
    """Gracefully terminates both backend and frontend processes on Ctrl+C."""
    print("\nShutting down Stock Intelligence components...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    sys.exit(0)

if __name__ == "__main__":
    # Register Ctrl+C interruption handler
    signal.signal(signal.SIGINT, kill_processes)
    
    # Identify the current python executable inside your virtual environment
    python_bin = sys.executable

    print("🚀 Booting up FastAPI Analytics Engine on http://127.0.0.1:8000...")
    backend_proc = subprocess.Popen([python_bin, "backend.py"])
    processes.append(backend_proc)

    # Wait briefly for FastAPI to bind port 8000
    time.sleep(1.0)

    print("🖥️ Booting up Streamlit User Interface on http://localhost:8501...")
    frontend_proc = subprocess.Popen([python_bin, "-m", "streamlit", "run", "frontend.py"])
    processes.append(frontend_proc)

    # Keep the orchestrator alive to maintain child processes
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        kill_processes(None, None)
