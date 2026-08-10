import subprocess
import sys
import time
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def run_both():
    print("🚀 Starting NIFTY 50 Live Market System...")
    print("1️⃣ Starting Live Data Collector (main.py)...")
    p1 = subprocess.Popen([sys.executable, "main.py"])

    time.sleep(2)  # Short delay to allow initial fetch

    print("2️⃣ Starting Streamlit Dashboard (app.py)...")
    p2 = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "app.py"])

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        p1.terminate()
        p2.terminate()
        p1.wait()
        p2.wait()
        print("✅ Stopped successfully.")

if __name__ == "__main__":
    run_both()
