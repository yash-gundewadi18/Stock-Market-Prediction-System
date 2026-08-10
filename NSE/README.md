# NIFTY 50 Live Market Dashboard 📈⚡

A modern, high-performance, dark-themed **Streamlit** dashboard for live Indian Stock Market analytics using NIFTY 50 data.

---

## 🌟 Key Features

1. **Header & Live Status**
   - Live date & clock, last CSV refresh timestamp, and Market Status badge (Open/Closed for Indian IST market hours).

2. **11 KPI Metrics**
   - NIFTY 50 LTP, Open, Day High, Day Low, Previous Close, Total Market Volume, Total Market Value (₹ Crores), Number of Stocks, Advancers count, Decliners count, and Average % Change.

3. **Interactive Sidebar**
   - Stock Ticker Selector, Search Symbol input, Top N slider, Min Volume filter, % Change Range slider, and 30-Second Auto Refresh toggle.

4. **Live Stock Table**
   - Interactive dataframe supporting search, sort, pagination, custom number formatting, and CSV download button.

5. **Live Price Trend & Stock Details**
   - Interactive Plotly price chart for selected ticker alongside a detailed panel showing Open, High, Low, Previous Close, 52-Week High/Low, 30-Day % Change, and 365-Day % Change.

6. **Technical Indicators**
   - Real-time calculations of SMA 20, SMA 50, EMA 20, and Rolling Average Volume with price overlay.

7. **Top Gainers & Losers**
   - Top 10 Gainers (Green styled cards) and Top 10 Losers (Red styled cards).

8. **Market Breadth & Volume/Value Analysis**
   - Market Breadth Donut chart (Advancers vs Decliners vs Unchanged).
   - Horizontal bar charts for Highest Traded Volume and Highest Traded Value (in Crores).

9. **Market Heatmap**
   - Treemap visualization where tile size is proportional to Volume and tile color indicates % Change (Green = Positive, Red = Negative).

10. **Advanced Market Analytics**
    - LTP Price & Volume Distribution histograms, Correlation Heatmap, and 4D Volume-Price Scatter Plot.

11. **Performance & Auto Refresh**
    - Uses `@st.cache_data(ttl=5)` for fast reloading and automatically refreshes every 30 seconds.

---

## 📁 Project Structure

```
d:\NSE/
│
├── app.py                  # Main Streamlit application
├── utils.py                # Data engine, cached loader, KPIs, indicators, & market status
├── charts.py               # Plotly chart builders & dark theme styling
├── main.py                 # Live data streamer appending to CSV
├── data/
│   └── nifty50_live.csv    # Live NIFTY 50 CSV dataset
├── assets/
│   └── style.css           # Custom dark-theme CSS design system
├── requirements.txt        # Project python dependencies
└── README.md               # Documentation
```

---

## 🚀 How to Run Both Services (Collector + Dashboard)

### 🌟 Single Command (Recommended)
To run both the **live data collector (`main.py`)** and the **Streamlit dashboard (`app.py`)** simultaneously in a single terminal:
```bash
python run_all.py
```

---

### 🛠️ Running via Separate Terminals

#### Terminal 1: Live Data Collector
```bash
python main.py
```

#### Terminal 2: Streamlit Dashboard
```bash
streamlit run app.py
```

---

## 🎨 Technology Stack
- **Python 3.10+**
- **Streamlit** (UI Framework)
- **Pandas** & **NumPy** (Data Processing)
- **Plotly Express** & **Graph Objects** (Interactive Data Visualizations)
- **CSS3** (Custom Dark Glassmorphic Design System)
