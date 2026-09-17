import streamlit as st
import pandas as pd
import numpy as np
import time
from datetime import datetime, time
from zoneinfo import ZoneInfo

# Import custom helper modules
from utils import (
    load_nifty_data,
    get_latest_snapshot,
    compute_kpis,
    compute_technical_indicators
)
from charts import (
    plot_live_price_trend,
    plot_highest_volume_stocks,
    plot_highest_value_stocks,
    plot_market_breadth_donut,
    plot_price_distribution,
    plot_volume_distribution,
    plot_correlation_heatmap,
    plot_scatter_volume_price,
    plot_historical_trends,
    plot_technical_indicators_chart,
    plot_market_heatmap
)

IST = ZoneInfo("Asia/Kolkata")

MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)


def get_ist_now():
    return datetime.now(IST)


def is_market_open():
    now = get_ist_now()

    # Saturday = 5, Sunday = 6
    if now.weekday() >= 5:
        return False

    return MARKET_OPEN <= now.time() <= MARKET_CLOSE
# Set Streamlit page configuration
st.set_page_config(
    page_title="NIFTY 50 Live Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS styles
def load_css():
    try:
        with open("assets/style.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except Exception:
        pass

load_css()

# Load Data
df, status_msg, error_type = load_nifty_data()

# ---------------------------------------------------------
# ERROR HANDLING (Requirement 21)
# ---------------------------------------------------------
if error_type == "missing":
    st.error(f"⚠️ **Missing Data Warning**: {status_msg}")
    st.info("💡 **Instructions**: Please run `python main.py` or place `nifty50_live.csv` inside the `data/` directory.")
    st.stop()
elif error_type == "empty":
    st.warning("⏳ **Waiting for Live Market Data...**")
    st.info("The data file is empty. Streaming pipeline is initializing. Auto-retrying...")
    time.sleep(5)
    st.rerun()

snapshot = get_latest_snapshot(df)
stocks_only = snapshot[snapshot['SYMBOL'] != 'NIFTY 50'].copy() if snapshot is not None else pd.DataFrame()

# ---------------------------------------------------------
# SIDEBAR CONTROLS (Requirement 3)
# ---------------------------------------------------------
st.sidebar.markdown("### 🎛️ Market Controls & Filters")

# Symbol list for dropdown
all_symbols = sorted(stocks_only['SYMBOL'].unique().tolist()) if not stocks_only.empty else []
default_stock = "RELIANCE" if "RELIANCE" in all_symbols else (all_symbols[0] if all_symbols else "NIFTY 50")

selected_stock = st.sidebar.selectbox("📌 Select Stock Ticker", options=all_symbols, index=all_symbols.index(default_stock) if default_stock in all_symbols else 0)
search_query = st.sidebar.text_input("🔍 Search Symbol", value="", placeholder="Type ticker e.g. INFY, TCS...")

top_n_filter = st.sidebar.slider("📊 Top N Stocks Display", min_value=5, max_value=25, value=10, step=5)

# Volume and % Change Filters
min_vol = int(stocks_only['VOLUME (shares)'].min()) if not stocks_only.empty else 0
max_vol = int(stocks_only['VOLUME (shares)'].max()) if not stocks_only.empty else 100000000
vol_filter = st.sidebar.slider("🌊 Min Traded Volume", min_value=min_vol, max_value=max_vol, value=min_vol)

min_pct = float(stocks_only['% CHANGE'].min()) if not stocks_only.empty else -10.0
max_pct = float(stocks_only['% CHANGE'].max()) if not stocks_only.empty else 10.0
pct_range = st.sidebar.slider("📉/📈 % Change Range", min_value=-15.0, max_value=15.0, value=(-15.0, 15.0))

auto_refresh = st.sidebar.checkbox("🔄 Auto Refresh (30s)", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("💡 **Tip**: Use filters above to customize live market tables, gainers, losers, and stock details.")

# Apply filters to snapshot data
filtered_snapshot = stocks_only.copy()
if search_query:
    filtered_snapshot = filtered_snapshot[filtered_snapshot['SYMBOL'].str.contains(search_query.upper(), na=False)]
filtered_snapshot = filtered_snapshot[
    (filtered_snapshot['VOLUME (shares)'] >= vol_filter) &
    (filtered_snapshot['% CHANGE'] >= pct_range[0]) &
    (filtered_snapshot['% CHANGE'] <= pct_range[1])
]

# ---------------------------------------------------------
# HEADER SECTION (Requirement 1)
# ---------------------------------------------------------
kpi_data = compute_kpis(df)
is_open = is_market_open()
market_status_text = "Market Open" if is_open else "Market Closed"
current_time_str = get_ist_now().strftime("%Y-%m-%d %H:%M:%S")
status_badge = f"""
<div class="{ 'badge-open' if is_open else 'badge-closed' }">
    <span class="status-dot { 'dot-green' if is_open else 'dot-red' }"></span>
    {market_status_text}
</div>
"""

st.markdown(f"""
<div class="header-container">
    <div>
        <h1 class="header-title">⚡ NIFTY 50 Live Market Dashboard</h1>
        <div class="header-subtitle">Real-time Indian Stock Market Analytics & Data Engine</div>
    </div>
    <div style="text-align: right;">
        {status_badge}
        <div style="font-size: 0.8rem; color: #787B86; margin-top: 8px;">
            <b>Live Clock:</b> {current_time_str}<br>
            <b>Last Refresh:</b> {kpi_data.get('latest_timestamp', 'N/A')}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# KPI CARDS (Requirement 2 - 11 Metrics)
# ---------------------------------------------------------
st.markdown("### 📊 Market Overview KPIs")
col1, col2, col3, col4, col5 = st.columns(5)
col6, col7, col8, col9, col10, col11 = st.columns(6)

nifty_change = kpi_data.get('nifty_change', 0.0)
nifty_pchange = kpi_data.get('nifty_pchange', 0.0)
nifty_delta_class = "kpi-delta-pos" if nifty_change >= 0 else "kpi-delta-neg"
nifty_sign = "+" if nifty_change >= 0 else ""

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">NIFTY 50 LTP</div>
        <div class="kpi-value">₹{kpi_data.get('nifty_ltp', 0.0):,.2f}</div>
        <div class="{nifty_delta_class}">{nifty_sign}{nifty_change:,.2f} ({nifty_sign}{nifty_pchange:.2f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">NIFTY Open</div>
        <div class="kpi-value">₹{kpi_data.get('nifty_open', 0.0):,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Day High</div>
        <div class="kpi-value">₹{kpi_data.get('nifty_high', 0.0):,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Day Low</div>
        <div class="kpi-value">₹{kpi_data.get('nifty_low', 0.0):,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Previous Close</div>
        <div class="kpi-value">₹{kpi_data.get('nifty_prev_close', 0.0):,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Volume</div>
        <div class="kpi-value">{kpi_data.get('total_volume', 0):,}</div>
    </div>
    """, unsafe_allow_html=True)

with col7:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Value</div>
        <div class="kpi-value">₹{kpi_data.get('total_value', 0.0):,.1f} Cr</div>
    </div>
    """, unsafe_allow_html=True)

with col8:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Total Stocks</div>
        <div class="kpi-value">{kpi_data.get('num_stocks', 0)}</div>
    </div>
    """, unsafe_allow_html=True)

with col9:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Advancers</div>
        <div class="kpi-value" style="color: #089981;">{kpi_data.get('advancers', 0)}</div>
    </div>
    """, unsafe_allow_html=True)

with col10:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Decliners</div>
        <div class="kpi-value" style="color: #F23645;">{kpi_data.get('decliners', 0)}</div>
    </div>
    """, unsafe_allow_html=True)

avg_change = kpi_data.get('avg_pchange', 0.0)
avg_class = "kpi-delta-pos" if avg_change >= 0 else "kpi-delta-neg"
avg_sign = "+" if avg_change >= 0 else ""

with col11:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Avg % Change</div>
        <div class="kpi-value {avg_class}">{avg_sign}{avg_change:.2f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# TOP GAINERS & TOP LOSERS CARDS (Requirements 6 & 7)
# ---------------------------------------------------------
col_gainer, col_loser = st.columns(2)

with col_gainer:
    st.markdown("### 🟢 Top Gainers")
    top_gainers = stocks_only.sort_values('% CHANGE', ascending=False).head(top_n_filter)
    for _, row in top_gainers.iterrows():
        st.markdown(f"""
        <div class="stock-card gainer-card">
            <div>
                <span class="stock-symbol">{row['SYMBOL']}</span>
                <span class="stock-ltp"> | ₹{row['LTP']:,.2f}</span>
            </div>
            <div class="pct-pill-green">+{row['% CHANGE']:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

with col_loser:
    st.markdown("### 🔴 Top Losers")
    top_losers = stocks_only.sort_values('% CHANGE', ascending=True).head(top_n_filter)
    for _, row in top_losers.iterrows():
        st.markdown(f"""
        <div class="stock-card loser-card">
            <div>
                <span class="stock-symbol">{row['SYMBOL']}</span>
                <span class="stock-ltp"> | ₹{row['LTP']:,.2f}</span>
            </div>
            <div class="pct-pill-red">{row['% CHANGE']:.2f}%</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# LIVE PRICE TREND & STOCK DETAILS (Requirements 5, 16, 17)
# ---------------------------------------------------------
st.markdown(f"### 📈 Stock Analytics: **{selected_stock}**")

col_trend, col_details = st.columns([0.65, 0.35])

with col_trend:
    fig_price = plot_live_price_trend(df, selected_stock)
    st.plotly_chart(fig_price, use_container_width=True)

with col_details:
    st.markdown("#### 📋 Stock Details Panel")
    stock_row = stocks_only[stocks_only['SYMBOL'] == selected_stock]
    if not stock_row.empty:
        r = stock_row.iloc[0]
        st.markdown(f"""
        <div style="background-color: #1E222D; border: 1px solid #2A2E39; border-radius: 12px; padding: 1rem 1.2rem;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2A2E39; padding-bottom: 6px; margin-bottom: 8px;">
                <span style="color: #787B86;">Open</span>
                <span style="font-weight: 600;">₹{r['OPEN']:,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2A2E39; padding-bottom: 6px; margin-bottom: 8px;">
                <span style="color: #787B86;">High</span>
                <span style="font-weight: 600; color: #089981;">₹{r['HIGH']:,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2A2E39; padding-bottom: 6px; margin-bottom: 8px;">
                <span style="color: #787B86;">Low</span>
                <span style="font-weight: 600; color: #F23645;">₹{r['LOW']:,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2A2E39; padding-bottom: 6px; margin-bottom: 8px;">
                <span style="color: #787B86;">Previous Close</span>
                <span style="font-weight: 600;">₹{r['PREV. CLOSE']:,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2A2E39; padding-bottom: 6px; margin-bottom: 8px;">
                <span style="color: #787B86;">52 Week High</span>
                <span style="font-weight: 600;">₹{r.get('52W H', 0.0):,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2A2E39; padding-bottom: 6px; margin-bottom: 8px;">
                <span style="color: #787B86;">52 Week Low</span>
                <span style="font-weight: 600;">₹{r.get('52W L', 0.0):,.2f}</span>
            </div>
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #2A2E39; padding-bottom: 6px; margin-bottom: 8px;">
                <span style="color: #787B86;">30 Day % Change</span>
                <span style="font-weight: 600; color: {'#089981' if r.get('30 D %CHNG', 0) >= 0 else '#F23645'};">{r.get('30 D %CHNG', 0.0):+.2f}%</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span style="color: #787B86;">365 Day % Change</span>
                <span style="font-weight: 600; color: {'#089981' if r.get('365 D %CHNG', 0) >= 0 else '#F23645'};">{r.get('365 D %CHNG', 0.0):+.2f}%</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Technical Indicators & Multi-trend subplots
st.markdown("#### 📐 Technical Indicators & Multi-Trend Analysis")
tab_tech, tab_hist = st.tabs(["📊 Technical Indicators (SMA/EMA)", "📈 Historical Multi-Trend Analysis"])

stock_tech_df = compute_technical_indicators(df, selected_stock)

with tab_tech:
    fig_tech = plot_technical_indicators_chart(stock_tech_df, selected_stock)
    st.plotly_chart(fig_tech, use_container_width=True)

with tab_hist:
    fig_hist = plot_historical_trends(df, selected_stock)
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# MARKET HEATMAP & BREADTH (Requirements 10 & 18)
# ---------------------------------------------------------
col_hm, col_brd = st.columns([0.65, 0.35])

with col_hm:
    st.markdown("### 🗺️ Market Heatmap (Volume Weighted)")
    fig_treemap = plot_market_heatmap(snapshot)
    st.plotly_chart(fig_treemap, use_container_width=True)

with col_brd:
    st.markdown("### ⚖️ Market Breadth")
    fig_donut = plot_market_breadth_donut(kpi_data['advancers'], kpi_data['decliners'], kpi_data['unchanged'])
    st.plotly_chart(fig_donut, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# MARKET VOLUME & VALUE ANALYSIS (Requirements 8 & 9)
# ---------------------------------------------------------
col_vol, col_val = st.columns(2)

with col_vol:
    st.markdown("### 🌊 Highest Traded Volume Stocks")
    fig_vol_bar = plot_highest_volume_stocks(filtered_snapshot, top_n=top_n_filter)
    st.plotly_chart(fig_vol_bar, use_container_width=True)

with col_val:
    st.markdown("### 💰 Highest Traded Value Stocks (Crores)")
    fig_val_bar = plot_highest_value_stocks(filtered_snapshot, top_n=top_n_filter)
    st.plotly_chart(fig_val_bar, use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# DISTRIBUTIONS & ADVANCED CHARTS (Requirements 11, 12, 13, 14)
# ---------------------------------------------------------
st.markdown("### 🔬 Deep Dive Market Analytics")

tab_dist, tab_corr, tab_scat = st.tabs(["📊 Price & Volume Distributions", "🔥 Correlation Heatmap", "🌌 4D Scatter Plot"])

with tab_dist:
    cd1, cd2 = st.columns(2)
    with cd1:
        st.plotly_chart(plot_price_distribution(filtered_snapshot), use_container_width=True)
    with cd2:
        st.plotly_chart(plot_volume_distribution(filtered_snapshot), use_container_width=True)

with tab_corr:
    st.plotly_chart(plot_correlation_heatmap(filtered_snapshot), use_container_width=True)

with tab_scat:
    st.plotly_chart(plot_scatter_volume_price(filtered_snapshot), use_container_width=True)

st.markdown("---")

# ---------------------------------------------------------
# LIVE STOCK TABLE (Requirement 4)
# ---------------------------------------------------------
st.markdown("### 📋 Live NIFTY 50 Stock Table")

table_cols = ['SYMBOL', 'COMPANY', 'LTP', 'CHANGE', '% CHANGE', 'OPEN', 'HIGH', 'LOW', 'PREV. CLOSE', 'VOLUME (shares)', 'VALUE (Crores)']
valid_table_cols = [c for c in table_cols if c in filtered_snapshot.columns]

display_df = filtered_snapshot[valid_table_cols].sort_values('% CHANGE', ascending=False)

st.dataframe(
    display_df,
    column_config={
        "LTP": st.column_config.NumberColumn("LTP (₹)", format="₹%.2f"),
        "CHANGE": st.column_config.NumberColumn("Change (₹)", format="%.2f"),
        "% CHANGE": st.column_config.NumberColumn("% Change", format="%.2f%%"),
        "OPEN": st.column_config.NumberColumn("Open (₹)", format="₹%.2f"),
        "HIGH": st.column_config.NumberColumn("High (₹)", format="₹%.2f"),
        "LOW": st.column_config.NumberColumn("Low (₹)", format="₹%.2f"),
        "PREV. CLOSE": st.column_config.NumberColumn("Prev Close (₹)", format="₹%.2f"),
        "VOLUME (shares)": st.column_config.NumberColumn("Volume", format="%d"),
        "VALUE (Crores)": st.column_config.NumberColumn("Value (Cr)", format="₹%.2f")
    },
    use_container_width=True,
    hide_index=True
)

# Download Filtered Data Button
csv_data = display_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Filtered Data (CSV)",
    data=csv_data,
    file_name=f"nifty50_filtered_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv"
)

# ---------------------------------------------------------
# FOOTER (Requirement 22)
# ---------------------------------------------------------
st.markdown(f"""
<div class="custom-footer">
    <b>Project Name:</b> NIFTY 50 Live Market Dashboard | 
    <b>Developer:</b> Antigravity AI | 
    <b>Current Refresh:</b> {current_time_str}
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# AUTO REFRESH (Requirement 19)
# ---------------------------------------------------------
if auto_refresh:
    time.sleep(30)
    st.rerun()
