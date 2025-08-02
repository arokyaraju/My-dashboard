# NOTE: To run this Streamlit app, make sure to install required packages:
# pip install streamlit pandas plotly numpy

try:
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    import numpy as np
except ModuleNotFoundError as e:
    import sys
    sys.exit(f"\n[ERROR] {e}\n\nPlease install the required modules using:\n    pip install streamlit pandas plotly numpy\n")

st.set_page_config(page_title="Trading Dashboard", layout="wide")

st.title("📊 Trading Indicator Dashboard")

# === Sidebar ===
st.sidebar.header("Settings")
ema_length = st.sidebar.number_input("EMA Length", min_value=1, value=9)
smma_length = st.sidebar.number_input("SMMA Length", min_value=1, value=15)
show_crossovers = st.sidebar.checkbox("Show Crossover Signals", value=True)

# === File Upload ===
st.sidebar.header("Upload OHLCV CSV")
file = st.sidebar.file_uploader("Choose a file", type=["csv"])

# === Load Data ===
def load_data():
    if file is not None:
        df = pd.read_csv(file)
    else:
        # Sample data fallback
        df = pd.read_csv("https://raw.githubusercontent.com/plotly/datasets/master/finance-charts-apple.csv")
        df.rename(columns={"AAPL.Open": "Open", "AAPL.High": "High", "AAPL.Low": "Low", "AAPL.Close": "Close"}, inplace=True)
        df["Volume"] = 1000000  # Dummy volume for fallback data
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# === Indicator Functions ===
def calc_indicators(df):
    required_columns = ["Close", "High", "Low", "Volume"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Missing required columns for indicators: {', '.join(missing)}")
        return df

    df["EMA"] = df["Close"].ewm(span=ema_length, adjust=False).mean()
    df["SMMA"] = df["Close"].ewm(alpha=1/smma_length, adjust=False).mean()  # Approximate SMMA
    df["VWAP"] = (df["Volume"] * (df["High"] + df["Low"] + df["Close"]) / 3).cumsum() / df["Volume"].cumsum()
    return df


def find_crossovers(df):
    if "EMA" not in df or "SMMA" not in df or "VWAP" not in df:
        return pd.Series([False]*len(df)), pd.Series([False]*len(df))
    cross_up = (df["EMA"] > df["SMMA"]) & (df["EMA"].shift(1) <= df["SMMA"].shift(1)) & (df["EMA"] > df["VWAP"])
    cross_down = (df["EMA"] < df["SMMA"]) & (df["EMA"].shift(1) >= df["SMMA"].shift(1)) & (df["EMA"] < df["VWAP"])
    return cross_up, cross_down

# === Main Chart Plotting ===
def plot_chart(df, cross_up, cross_down):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
        name='Candles'))

    if "EMA" in df:
        fig.add_trace(go.Scatter(x=df.index, y=df["EMA"], line=dict(color='green', width=1.5), name="EMA"))
    if "SMMA" in df:
        fig.add_trace(go.Scatter(x=df.index, y=df["SMMA"], line=dict(color='orange', width=1.5), name="SMMA"))
    if "VWAP" in df:
        fig.add_trace(go.Scatter(x=df.index, y=df["VWAP"], line=dict(color='blue', width=1.5, dash='dot'), name="VWAP"))

    if show_crossovers:
        fig.add_trace(go.Scatter(
            x=df.index[cross_up], y=df["Close"][cross_up],
            mode='markers', marker=dict(color='green', size=8),
            name='Bullish Crossover'))

        fig.add_trace(go.Scatter(
            x=df.index[cross_down], y=df["Close"][cross_down],
            mode='markers', marker=dict(color='red', size=8),
            name='Bearish Crossunder'))

    fig.update_layout(height=700, xaxis_rangeslider_visible=False, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# === Run App ===
df = load_data()
df = calc_indicators(df)
cross_up, cross_down = find_crossovers(df)
plot_chart(df, cross_up, cross_down)

st.caption("Built with ❤️ using Streamlit")