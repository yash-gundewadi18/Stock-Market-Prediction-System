import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

# Standard Dark Theme Colors
COLOR_BG = "#1E222D"
COLOR_PAPER = "#1E222D"
COLOR_TEXT = "#E0E3EB"
COLOR_GRID = "#2A2E39"
COLOR_GREEN = "#089981"
COLOR_RED = "#F23645"
COLOR_BLUE = "#2962FF"
COLOR_CYAN = "#00E5FF"
COLOR_YELLOW = "#FFD700"
COLOR_PURPLE = "#BB86FC"

def apply_dark_theme(fig, title=""):
    """
    Applies standard dark theme formatting to Plotly figure.
    """
    fig.update_layout(
        template='plotly_dark',
        title={
            'text': f"<b>{title}</b>",
            'y': 0.95,
            'x': 0.02,
            'xanchor': 'left',
            'yanchor': 'top',
            'font': {'size': 16, 'color': COLOR_TEXT}
        },
        paper_bgcolor=COLOR_PAPER,
        plot_bgcolor=COLOR_BG,
        font={'color': COLOR_TEXT, 'family': 'Inter, sans-serif'},
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_GRID,
            showline=True,
            linecolor=COLOR_GRID
        ),
        yaxis=dict(
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_GRID,
            showline=True,
            linecolor=COLOR_GRID
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color=COLOR_TEXT)
        ),
        hoverlabel=dict(
            bgcolor="#2A2E39",
            font_size=12,
            font_family="Inter, sans-serif"
        )
    )
    return fig


def plot_live_price_trend(df, symbol):
    """
    Plots interactive line chart of LTP over time for selected stock.
    """
    stock_df = df[df['SYMBOL'] == symbol].sort_values('Timestamp').copy()

    if stock_df.empty:
        fig = go.Figure()
        fig.add_annotation(text="No historical data available for selected stock",
                           xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
                           font=dict(size=14, color=COLOR_TEXT))
        return apply_dark_theme(fig, f"Live Price Trend: {symbol}")

    fig = px.line(
        stock_df,
        x='Timestamp',
        y='LTP',
        markers=True,
        title=f"Live Price Trend: {symbol}",
        labels={'LTP': 'Last Traded Price (₹)', 'Timestamp': 'Time'}
    )

    fig.update_traces(
        line=dict(color=COLOR_CYAN, width=3),
        marker=dict(size=8, color=COLOR_BLUE)
    )
    return apply_dark_theme(fig, f"Live Price Trend: {symbol}")


def plot_highest_volume_stocks(df, top_n=10):
    """
    Horizontal bar chart showing top traded stocks by Volume.
    """
    stocks = df[df['SYMBOL'] != 'NIFTY 50'].sort_values('VOLUME (shares)', ascending=False).head(top_n)

    fig = px.bar(
        stocks.sort_values('VOLUME (shares)', ascending=True),
        x='VOLUME (shares)',
        y='SYMBOL',
        orientation='h',
        color='% CHANGE',
        color_continuous_scale=[(0, COLOR_RED), (0.5, '#434651'), (1, COLOR_GREEN)],
        title=f"Highest Volume Stocks (Top {top_n})",
        labels={'VOLUME (shares)': 'Volume (Shares)', 'SYMBOL': 'Stock'}
    )
    fig.update_layout(coloraxis_showscale=False)
    return apply_dark_theme(fig, f"Highest Volume Stocks (Top {top_n})")


def plot_highest_value_stocks(df, top_n=10):
    """
    Horizontal bar chart showing top traded stocks by Traded Value (Crores).
    """
    stocks = df[df['SYMBOL'] != 'NIFTY 50'].sort_values('VALUE (Crores)', ascending=False).head(top_n)

    fig = px.bar(
        stocks.sort_values('VALUE (Crores)', ascending=True),
        x='VALUE (Crores)',
        y='SYMBOL',
        orientation='h',
        color='VALUE (Crores)',
        color_continuous_scale='Viridis',
        title=f"Highest Traded Value Stocks in ₹ Crores (Top {top_n})",
        labels={'VALUE (Crores)': 'Value (₹ Crores)', 'SYMBOL': 'Stock'}
    )
    fig.update_layout(coloraxis_showscale=False)
    return apply_dark_theme(fig, f"Highest Traded Value Stocks (Top {top_n})")


def plot_market_breadth_donut(advancers, decliners, unchanged):
    """
    Plotly Donut Chart showing Market Breadth (Advancers, Decliners, Unchanged).
    """
    labels = ['Advancers', 'Decliners', 'Unchanged']
    values = [advancers, decliners, unchanged]
    colors = [COLOR_GREEN, COLOR_RED, '#787B86']

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color='#1E222D', width=2)),
        textinfo='value+percent',
        hoverinfo='label+value+percent',
        textfont=dict(size=14, color='#FFFFFF')
    )])

    fig.add_annotation(
        text=f"Total<br><b>{advancers+decliners+unchanged}</b>",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=14, color=COLOR_TEXT)
    )

    return apply_dark_theme(fig, "Market Breadth Ratio")


def plot_price_distribution(df):
    """
    Histogram of LTP across NIFTY 50 constituents.
    """
    stocks = df[df['SYMBOL'] != 'NIFTY 50']

    fig = px.histogram(
        stocks,
        x='LTP',
        nbins=20,
        title="LTP Price Distribution",
        labels={'LTP': 'Last Traded Price (₹)'},
        color_discrete_sequence=[COLOR_BLUE]
    )
    return apply_dark_theme(fig, "LTP Price Distribution")


def plot_volume_distribution(df):
    """
    Histogram of Trading Volume.
    """
    stocks = df[df['SYMBOL'] != 'NIFTY 50']

    fig = px.histogram(
        stocks,
        x='VOLUME (shares)',
        nbins=20,
        title="Volume Distribution",
        labels={'VOLUME (shares)': 'Volume (Shares)'},
        color_discrete_sequence=[COLOR_PURPLE]
    )
    return apply_dark_theme(fig, "Volume Distribution")


def plot_correlation_heatmap(df):
    """
    Correlation Matrix Heatmap between LTP, CHANGE, % CHANGE, Volume, Value.
    """
    stocks = df[df['SYMBOL'] != 'NIFTY 50']
    cols = ['LTP', 'CHANGE', '% CHANGE', 'VOLUME (shares)', 'VALUE (Crores)']

    valid_cols = [c for c in cols if c in stocks.columns]
    corr = stocks[valid_cols].corr()

    fig = px.imshow(
        corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Correlation Heatmap"
    )
    return apply_dark_theme(fig, "Correlation Heatmap")


def plot_scatter_volume_price(df):
    """
    Scatter Plot: X=Volume, Y=LTP, Color=% Change, Size=Value (Crores).
    """
    stocks = df[df['SYMBOL'] != 'NIFTY 50'].copy()
    stocks['Size_Val'] = stocks['VALUE (Crores)'].clip(lower=1)

    fig = px.scatter(
        stocks,
        x='VOLUME (shares)',
        y='LTP',
        color='% CHANGE',
        size='Size_Val',
        hover_name='SYMBOL',
        hover_data=['COMPANY', 'LTP', '% CHANGE', 'VALUE (Crores)'],
        color_continuous_scale=[(0, COLOR_RED), (0.5, '#787B86'), (1, COLOR_GREEN)],
        title="Volume vs LTP Scatter Plot (Sized by Traded Value)",
        labels={'VOLUME (shares)': 'Volume (Shares)', 'LTP': 'LTP (₹)'}
    )
    return apply_dark_theme(fig, "Volume vs LTP Scatter Plot")


def plot_historical_trends(df, symbol):
    """
    Displays synchronized subplots for LTP, Volume, and % Change trend over time for selected stock.
    """
    stock_df = df[df['SYMBOL'] == symbol].sort_values('Timestamp').copy()

    if stock_df.empty:
        fig = go.Figure()
        return apply_dark_theme(fig, f"Historical Trends for {symbol}")

    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        subplot_titles=(f"{symbol} - LTP Trend", f"{symbol} - Volume Trend", f"{symbol} - % Change Trend")
    )

    fig.add_trace(
        go.Scatter(x=stock_df['Timestamp'], y=stock_df['LTP'], mode='lines+markers', name='LTP', line=dict(color=COLOR_CYAN, width=2)),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=stock_df['Timestamp'], y=stock_df['VOLUME (shares)'], name='Volume', marker=dict(color=COLOR_BLUE)),
        row=2, col=1
    )

    colors = [COLOR_GREEN if val >= 0 else COLOR_RED for val in stock_df['% CHANGE']]
    fig.add_trace(
        go.Scatter(x=stock_df['Timestamp'], y=stock_df['% CHANGE'], mode='lines+markers', name='% Change', line=dict(color=COLOR_YELLOW), marker=dict(color=colors, size=8)),
        row=3, col=1
    )

    fig.update_layout(height=600, showlegend=False)
    return apply_dark_theme(fig, f"Historical Multi-Trend Analysis: {symbol}")


def plot_technical_indicators_chart(stock_df, symbol):
    """
    Plots LTP along with SMA 20, SMA 50, EMA 20, and Rolling Average Volume overlay.
    """
    if stock_df is None or stock_df.empty:
        fig = go.Figure()
        return apply_dark_theme(fig, f"Technical Indicators: {symbol}")

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.08,
        subplot_titles=(f"{symbol} - Price & Moving Averages", f"{symbol} - Volume & Rolling Avg")
    )

    fig.add_trace(
        go.Scatter(x=stock_df['Timestamp'], y=stock_df['LTP'], mode='lines+markers', name='LTP', line=dict(color='#FFFFFF', width=2)),
        row=1, col=1
    )

    if 'SMA_20' in stock_df.columns:
        fig.add_trace(
            go.Scatter(x=stock_df['Timestamp'], y=stock_df['SMA_20'], mode='lines', name='SMA 20', line=dict(color=COLOR_CYAN, width=1.5, dash='dash')),
            row=1, col=1
        )

    if 'SMA_50' in stock_df.columns:
        fig.add_trace(
            go.Scatter(x=stock_df['Timestamp'], y=stock_df['SMA_50'], mode='lines', name='SMA 50', line=dict(color=COLOR_YELLOW, width=1.5, dash='dot')),
            row=1, col=1
        )

    if 'EMA_20' in stock_df.columns:
        fig.add_trace(
            go.Scatter(x=stock_df['Timestamp'], y=stock_df['EMA_20'], mode='lines', name='EMA 20', line=dict(color=COLOR_PURPLE, width=1.5)),
            row=1, col=1
        )

    fig.add_trace(
        go.Bar(x=stock_df['Timestamp'], y=stock_df['VOLUME (shares)'], name='Volume', marker=dict(color='rgba(41, 98, 255, 0.5)')),
        row=2, col=1
    )

    if 'Rolling_Avg_Vol' in stock_df.columns:
        fig.add_trace(
            go.Scatter(x=stock_df['Timestamp'], y=stock_df['Rolling_Avg_Vol'], mode='lines', name='Rolling Avg Vol', line=dict(color=COLOR_GREEN, width=2)),
            row=2, col=1
        )

    fig.update_layout(height=550)
    return apply_dark_theme(fig, f"Technical Analysis: {symbol}")


def plot_market_heatmap(df):
    """
    Plotly Treemap visualization (Tile size = Volume, Tile color = % CHANGE).
    Green = Positive, Red = Negative.
    """
    stocks = df[df['SYMBOL'] != 'NIFTY 50'].copy()

    stocks['Treemap_Size'] = stocks['VOLUME (shares)'].clip(lower=1)
    stocks['Market'] = 'NIFTY 50'

    fig = px.treemap(
        stocks,
        path=['Market', 'SYMBOL'],
        values='Treemap_Size',
        color='% CHANGE',
        color_continuous_scale=[(0, COLOR_RED), (0.5, '#2A2E39'), (1, COLOR_GREEN)],
        color_continuous_midpoint=0,
        hover_data=['LTP', '% CHANGE', 'VOLUME (shares)', 'VALUE (Crores)'],
        title="NIFTY 50 Market Treemap (Tile Size = Volume, Color = % Change)"
    )

    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{customdata[1]:.2f}%",
        textfont=dict(size=14, color='#FFFFFF')
    )
    return apply_dark_theme(fig, "NIFTY 50 Market Heatmap")
