from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Import custom helper modules
from utils import (
    load_nifty_data,
    get_latest_snapshot,
    compute_kpis,
    compute_technical_indicators,
    get_market_status
)

app = FastAPI(title="NIFTY 50 Live Market API")

# Enable CORS for the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this for production (e.g., ["http://localhost:5173"])
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def format_df_for_json(df):
    """Replace NaN, Infinity with None for JSON serialization and convert numpy types"""
    if df is None or df.empty:
        return []
    
    # Create a copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Convert numpy types to native python types
    for col in df.columns:
        if pd.api.types.is_integer_dtype(df[col]):
            df[col] = df[col].astype(object)
            df[col] = df[col].apply(lambda x: int(x) if pd.notnull(x) else None)
        elif pd.api.types.is_float_dtype(df[col]):
            df[col] = df[col].astype(object)
            df[col] = df[col].apply(lambda x: float(x) if pd.notnull(x) else None)
            
    # Convert to dict and handle any remaining NaN/NaT
    records = df.to_dict(orient="records")
    for row in records:
        for k, v in row.items():
            if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
                row[k] = None
            elif pd.isna(v):
                row[k] = None
                
    return records

@app.get("/api/market-status")
def get_status():
    status_text, is_open = get_market_status()
    
    # Check data loading status
    df, status_msg, error_type = load_nifty_data()
    
    return {
        "status_text": status_text,
        "is_open": is_open,
        "data_status": status_msg,
        "error_type": error_type
    }

@app.get("/api/dashboard-data")
def get_dashboard_data():
    df, status_msg, error_type = load_nifty_data()
    
    if error_type in ["missing", "empty"]:
        raise HTTPException(status_code=503, detail=status_msg)
        
    kpi_data = compute_kpis(df)
    snapshot = get_latest_snapshot(df)
    
    # Replace NaN/Inf and numpy types in KPI data
    for k, v in kpi_data.items():
        if isinstance(v, float) and (np.isnan(v) or np.isinf(v)):
            kpi_data[k] = None
        elif type(v).__module__ == np.__name__:
            kpi_data[k] = v.item()
    
    stocks_only = snapshot[snapshot['SYMBOL'] != 'NIFTY 50'].copy() if snapshot is not None else pd.DataFrame()
    
    top_gainers = stocks_only.sort_values('% CHANGE', ascending=False).head(10)
    top_losers = stocks_only.sort_values('% CHANGE', ascending=True).head(10)
    highest_volume = stocks_only.sort_values('VOLUME (shares)', ascending=False).head(10)
    highest_value = stocks_only.sort_values('VALUE (Crores)', ascending=False).head(10)

    return {
        "kpi_data": kpi_data,
        "all_stocks": format_df_for_json(stocks_only),
        "top_gainers": format_df_for_json(top_gainers),
        "top_losers": format_df_for_json(top_losers),
        "highest_volume": format_df_for_json(highest_volume),
        "highest_value": format_df_for_json(highest_value)
    }

@app.get("/api/stock/{symbol}")
def get_stock_details(symbol: str):
    df, status_msg, error_type = load_nifty_data()
    
    if error_type in ["missing", "empty"]:
        raise HTTPException(status_code=503, detail=status_msg)
        
    snapshot = get_latest_snapshot(df)
    stock_row = snapshot[snapshot['SYMBOL'] == symbol]
    
    if stock_row.empty:
        raise HTTPException(status_code=404, detail="Stock not found")
        
    # Get historical data for the chart
    historical_df = df[df['SYMBOL'] == symbol].sort_values('Timestamp')
    
    # Get technical indicators
    tech_df = compute_technical_indicators(df, symbol)
    
    return {
        "details": format_df_for_json(stock_row)[0],
        "historical": format_df_for_json(historical_df),
        "technical": format_df_for_json(tech_df)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
