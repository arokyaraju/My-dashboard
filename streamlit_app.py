# trading_dashboard.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="MyTradingCalculator", layout="wide")

# === Tabs ===
tabs = st.tabs(["Position Size Calculator", "Trade Setup Summary", "Trade Journal", "Reports"])

# === Tab 1: Position Size Calculator ===
with tabs[0]:
    st.header("📐 Position Size Calculator")
    capital = st.number_input("Capital", min_value=0.0, value=100000.0)
    risk_per_trade = st.number_input("Risk per Trade (%)", min_value=0.0, value=1.0)
    entry_price = st.number_input("Entry Price", min_value=0.0, value=100.0)
    stop_loss = st.number_input("Stop Loss", min_value=0.01, value=5.0)
    lot_size = st.number_input("Lot Size", min_value=1, value=25)

    risk_amount = capital * risk_per_trade / 100
    qty = risk_amount // stop_loss
    lots = qty // lot_size

    st.success(f"You can trade approximately {int(qty)} quantity ({int(lots)} lots) with ₹{risk_amount:.2f} risk.")

# === Tab 2: Trade Setup Summary ===
with tabs[1]:
    st.header("📋 Trade Setup Summary")
    symbol = st.text_input("Symbol", "NIFTY")
    direction = st.selectbox("Trade Type", ["Call", "Put"])
    strike_price = st.number_input("Strike Price", min_value=0.0, value=20000.0)
    premium = st.number_input("Premium", min_value=0.0, value=100.0)
    target = st.number_input("Target (Points)", min_value=0.0, value=50.0)

    rr_ratio = target / stop_loss if stop_loss > 0 else 0
    st.metric("Risk-Reward Ratio", f"{rr_ratio:.2f}")

# === Tab 3: Trade Journal ===
with tabs[2]:
    st.header("📝 Trade Journal")
    if "journal" not in st.session_state:
        st.session_state.journal = pd.DataFrame(columns=["Date", "Time", "Symbol", "CE/PE", "Strike", "Entry", "Exit", "Points", "PnL", "Remarks"])

    with st.form("Add Trade"):
        cols = st.columns(5)
        date = cols[0].date_input("Date")
        time = cols[1].time_input("Time")
        sym = cols[2].text_input("Symbol")
        option = cols[3].selectbox("CE/PE", ["CE", "PE"])
        strike = cols[4].number_input("Strike Price", value=0.0)
        entry = st.number_input("Entry Price", value=0.0)
        exit = st.number_input("Exit Price", value=0.0)
        remarks = st.text_input("Remarks")
        submitted = st.form_submit_button("Add Trade")
        if submitted:
            points = exit - entry
            pnl = points * lot_size
            new_entry = pd.DataFrame([[date, time, sym, option, strike, entry, exit, points, pnl, remarks]], columns=st.session_state.journal.columns)
            st.session_state.journal = pd.concat([st.session_state.journal, new_entry], ignore_index=True)

    st.dataframe(st.session_state.journal, use_container_width=True)

# === Tab 4: Reports ===
with tabs[3]:
    st.header("📈 Reports")
    if st.session_state.journal.empty:
        st.info("No trades to report yet.")
    else:
        journal = st.session_state.journal
        journal["Date"] = pd.to_datetime(journal["Date"])
        journal["PnL"] = pd.to_numeric(journal["PnL"])
        time_range = st.selectbox("View Report By", ["Daily", "Weekly", "Monthly"])

        if time_range == "Daily":
            report = journal.groupby(journal["Date"].dt.date)["PnL"].sum()
        elif time_range == "Weekly":
            report = journal.groupby(journal["Date"].dt.to_period("W"))["PnL"].sum()
        else:
            report = journal.groupby(journal["Date"].dt.to_period("M"))["PnL"].sum()

        st.bar_chart(report)

        symbol_filter = st.selectbox("Filter by Symbol", ["All"] + sorted(journal["Symbol"].dropna().unique()))
        if symbol_filter != "All":
            filtered = journal[journal["Symbol"] == symbol_filter]
            st.dataframe(filtered)

st.caption("Built with ❤️ in Streamlit")