import subprocess
import sys
import time
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def run_both():
    print("🚀 Starting NIFTY 50 Live Market System...")

    print("1️⃣ Starting Live Data Collector (main.py)...")
    p1 = subprocess.Popen([sys.executable, "main.py"])

    time.sleep(2)

    print("2️⃣ Starting FastAPI Backend (api.py)...")

    port = os.environ.get("PORT", "8000")

    p2 = subprocess.Popen([
        sys.executable,
        "-m",
        "uvicorn",
        "api:app",
        "--host",
        "0.0.0.0",
        "--port",
        port
    ])

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