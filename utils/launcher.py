import os
import sys
import subprocess
import time
import webbrowser
import threading
from pathlib import Path

# Redirect to project directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

def run_server():
    """Run Flask server"""
    os.environ['FLASK_ENV'] = 'production'
    from app import app
    app.run(debug=False, port=5000, use_reloader=False, threaded=True)

def main():
    # Start Flask server in a separate thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Open browser
    webbrowser.open('http://localhost:5000/ru')
    
    # Keep the app running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
