import os
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, time

CSV_FILE_PATHS = [
    os.path.join("data", "nifty50_live.csv"),
    "nifty50_live.csv"
]

@st.cache_data(ttl=5)
def load_nifty_data():
    """
    Loads and normalizes NIFTY 50 stock data from CSV.
    Returns (df, status_message, error_type).
    error_type can be: None, 'missing', 'empty'
    """
    filepath = None
    for path in CSV_FILE_PATHS:
        if os.path.exists(path):
            filepath = path
            break

    if filepath is None:
        return None, "CSV data file missing. Please ensure 'data/nifty50_live.csv' exists.", "missing"

    try:
        if os.path.getsize(filepath) == 0:
            return None, "Waiting for Live Market Data...", "empty"

        df = None
        for attempt in range(5):
            try:
                df = pd.read_csv(filepath)
                break
            except (PermissionError, OSError):
                import time as t_mod
                t_mod.sleep(0.2)

        if df is None or df.empty:
            return None, "Waiting for Live Market Data...", "empty"

        # Standardize column mappings (handling both API column names and standard display names)
        column_mapping = {
            'symbol': 'SYMBOL',
            'lastPrice': 'LTP',
            'open': 'OPEN',
            'dayHigh': 'HIGH',
            'dayLow': 'LOW',
            'previousClose': 'PREV. CLOSE',
            'stockIndClosePrice': 'INDICATIVE CLOSE',
            'change': 'CHANGE',
            'pChange': '% CHANGE',
            'totalTradedVolume': 'VOLUME (shares)',
            'yearHigh': '52W H',
            'yearLow': '52W L',
            'perChange30d': '30 D %CHNG',
            'perChange365d': '365 D %CHNG',
            'companyName': 'COMPANY'
        }

        # Rename existing columns
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]

        # Calculate VALUE (Crores) if totalTradedValue is present
        if 'totalTradedValue' in df.columns and 'VALUE (Crores)' not in df.columns:
            df['VALUE (Crores)'] = df['totalTradedValue'] / 1e7
        elif 'VALUE (Crores)' not in df.columns:
            df['VALUE (Crores)'] = (df['LTP'] * df['VOLUME (shares)']) / 1e7

        # Fill any missing values gracefully
        numeric_cols = ['LTP', 'OPEN', 'HIGH', 'LOW', 'PREV. CLOSE', 'CHANGE', '% CHANGE',
                        'VOLUME (shares)', 'VALUE (Crores)', '52W H', '52W L', '30 D %CHNG', '365 D %CHNG']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        if 'Timestamp' in df.columns:
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
            df['Timestamp_Str'] = df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

        return df, "Data loaded successfully", None

    except Exception as e:
        return None, f"Error reading CSV file: {str(e)}", "missing"


def get_latest_snapshot(df):
    """
    Returns the dataframe corresponding to the latest Timestamp in the dataset.
    """
    if df is None or df.empty or 'Timestamp' not in df.columns:
        return df

    latest_time = df['Timestamp'].max()
    snapshot = df[df['Timestamp'] == latest_time].copy()
    return snapshot


def get_market_status():
    """
    Checks if current time corresponds to Indian Stock Market operating hours (09:15 - 15:30 IST Mon-Fri).
    Returns (status_text, is_open_boolean).
    """
    now = datetime.now()
    day = now.weekday()  # 0=Mon, 6=Sun
    current_time = now.time()

    market_open = time(9, 15)
    market_close = time(15, 30)

    if day < 5 and market_open <= current_time <= market_close:
        return "Market Open", True
    else:
        return "Market Closed", False


def compute_kpis(df):
    """
    Computes key performance indicators for NIFTY 50 and constituents.
    """
    if df is None or df.empty:
        return {}

    snapshot = get_latest_snapshot(df)

    # Separate index entry vs constituent stocks
    index_row = snapshot[snapshot['SYMBOL'] == 'NIFTY 50']
    stocks = snapshot[snapshot['SYMBOL'] != 'NIFTY 50']

    if stocks.empty:
        stocks = snapshot

    # Index metrics
    if not index_row.empty:
        nifty_ltp = index_row['LTP'].values[0]
        nifty_open = index_row['OPEN'].values[0]
        nifty_high = index_row['HIGH'].values[0]
        nifty_low = index_row['LOW'].values[0]
        nifty_prev_close = index_row['PREV. CLOSE'].values[0]
        nifty_change = index_row['CHANGE'].values[0]
        nifty_pchange = index_row['% CHANGE'].values[0]
    else:
        nifty_ltp = stocks['LTP'].mean()
        nifty_open = stocks['OPEN'].mean()
        nifty_high = stocks['HIGH'].max()
        nifty_low = stocks['LOW'].min()
        nifty_prev_close = stocks['PREV. CLOSE'].mean()
        nifty_change = nifty_ltp - nifty_prev_close
        nifty_pchange = (nifty_change / nifty_prev_close * 100) if nifty_prev_close else 0.0

    total_volume = stocks['VOLUME (shares)'].sum()
    total_value = stocks['VALUE (Crores)'].sum()
    num_stocks = len(stocks)

    advancers = len(stocks[stocks['% CHANGE'] > 0])
    decliners = len(stocks[stocks['% CHANGE'] < 0])
    unchanged = len(stocks[stocks['% CHANGE'] == 0])

    avg_pchange = stocks['% CHANGE'].mean()

    return {
        'nifty_ltp': nifty_ltp,
        'nifty_open': nifty_open,
        'nifty_high': nifty_high,
        'nifty_low': nifty_low,
        'nifty_prev_close': nifty_prev_close,
        'nifty_change': nifty_change,
        'nifty_pchange': nifty_pchange,
        'total_volume': total_volume,
        'total_value': total_value,
        'num_stocks': num_stocks,
        'advancers': advancers,
        'decliners': decliners,
        'unchanged': unchanged,
        'avg_pchange': avg_pchange,
        'latest_timestamp': snapshot['Timestamp_Str'].max() if 'Timestamp_Str' in snapshot.columns else 'N/A'
    }


def compute_technical_indicators(df, symbol):
    """
    Computes SMA 20, SMA 50, EMA 20, and Rolling Average Volume for a specific symbol over time.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    stock_df = df[df['SYMBOL'] == symbol].sort_values('Timestamp').copy()

    if stock_df.empty:
        return stock_df

    stock_df['SMA_20'] = stock_df['LTP'].rolling(window=20, min_periods=1).mean()
    stock_df['SMA_50'] = stock_df['LTP'].rolling(window=50, min_periods=1).mean()
    stock_df['EMA_20'] = stock_df['LTP'].ewm(span=20, adjust=False).mean()
    stock_df['Rolling_Avg_Vol'] = stock_df['VOLUME (shares)'].rolling(window=5, min_periods=1).mean()

    return stock_df
