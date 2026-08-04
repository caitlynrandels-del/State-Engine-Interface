import threading
import uvicorn
import webview  # Optional, or use webbrowser
import webbrowser
import os
import sys

def start_server():
    # Run FastAPI server locally
    uvicorn.run("api.oroboro_api:app", host="127.0.0.1", port=8000, log_level="warning")

if __name__ == "__main__":
    # Start the backend server in a background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Determine path for cockpit UI
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)



    cockpit_path = os.path.join(base_path, "cockpit", "index.html")
    
    # Open the frontend cockpit interface in the browser
    webbrowser.open(f"file://{os.path.abspath(cockpit_path)}")

    # Keep application alive
    try:
        while server_thread.is_alive():
            server_thread.join(1)
    except KeyboardInterrupt:
        sys.exit(0)

        