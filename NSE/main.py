import requests
import pandas as pd
import schedule
import time
import os
import sys
from datetime import datetime

# Ensure Windows console supports UTF-8 logging
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

URL = "https://www.nseindia.com/api/NextApi/apiClient/marketWatchApi?functionName=getIndicesData&symbol=NIFTY%2050"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "Referer": "https://www.nseindia.com/",
    "Accept-Language": "en-US,en;q=0.9"
}

session = requests.Session()

# Get cookies once
session.get("https://www.nseindia.com", headers=headers)

CSV_FILE = "nifty50_live.csv"


def fetch_and_save():
    try:
        response = session.get(URL, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Change this according to your JSON structure
        df = pd.DataFrame(data["data"]["data"])

        # Add timestamp
        df["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Target file paths to sync
        target_files = ["nifty50_live.csv", os.path.join("data", "nifty50_live.csv")]
        
        for file_path in target_files:
            dir_name = os.path.dirname(file_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)

            # Retry writing up to 5 times to handle Windows file locks cleanly
            for attempt in range(5):
                try:
                    file_exists = os.path.exists(file_path) and os.path.getsize(file_path) > 0
                    df.to_csv(
                        file_path,
                        mode="a",
                        header=not file_exists,
                        index=False
                    )
                    break
                except PermissionError:
                    time.sleep(0.2)
                except Exception as file_err:
                    print(f"⚠️ Warning saving to {file_path}: {file_err}")
                    break

        print(f"✅ Saved {len(df)} rows at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        print("❌ Error fetching market data:", e)


# Run immediately
fetch_and_save()

# Schedule every 2 minutes
schedule.every(30).seconds.do(fetch_and_save)

print("Scheduler started... Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(1)