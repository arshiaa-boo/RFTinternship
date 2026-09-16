"""
streamlit_app.py
-----------------
Bonus challenge: an interactive Streamlit dashboard for the Stock
Market Portfolio Analyzer.

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyzer import (
    load_holdings, load_prices, profit_loss_table, best_worst_performers,
    overall_portfolio_return, portfolio_growth_over_time, daily_returns,
    sector_investment, moving_average_predictions_for_portfolio, build_full_report,
)

st.set_page_config(page_title="Stock Portfolio Analyzer", layout="wide")
st.title("📈 Stock Market Portfolio Analyzer")
st.caption("Upload your holdings + price history (or use the bundled sample data) "
           "to track profit/loss, sector allocation, and trend predictions.")

# ---------------------------------------------------------------------
# Data source
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("📂 Data Source")
    holdings_file = st.file_uploader("Portfolio holdings CSV", type=["csv"], key="holdings")
    prices_file = st.file_uploader("Stock price history CSV", type=["csv"], key="prices")
    use_sample = st.checkbox("Use bundled sample data", value=(holdings_file is None and prices_file is None))

if holdings_file is not None and prices_file is not None:
    holdings = load_holdings(holdings_file)
    prices = load_prices(prices_file)
elif use_sample:
    holdings = load_holdings("portfolio_holdings.csv")
    prices = load_prices("stock_prices.csv")
else:
    st.info("Upload both CSVs (holdings + prices), or check 'Use bundled sample data'.")
    st.stop()

# ---------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------
with st.sidebar:
    st.header("🔍 Filters")
    all_sectors = sorted(holdings["sector"].dropna().unique().tolist())
    selected_sectors = st.multiselect("Sector", all_sectors, default=all_sectors)

    all_symbols = sorted(holdings["symbol"].dropna().unique().tolist())
    selected_symbols = st.multiselect("Stock symbol", all_symbols, default=all_symbols)

    st.markdown("---")
    st.header("📐 Moving Average Settings")
    ma_short = st.number_input("Short window (days)", min_value=2, max_value=30, value=5)
    ma_long = st.number_input("Long window (days)", min_value=5, max_value=100, value=20)

filtered_holdings = holdings[
    holdings["sector"].isin(selected_sectors) & holdings["symbol"].isin(selected_symbols)
]

if filtered_holdings.empty:
    st.warning("No holdings match the current filters.")
    st.stop()

# ---------------------------------------------------------------------
# Core analysis
# ---------------------------------------------------------------------
pl_df = profit_loss_table(filtered_holdings, prices)
overall = overall_portfolio_return(pl_df)
bw = best_worst_performers(pl_df)
growth_df = portfolio_growth_over_time(filtered_holdings, prices)
returns_df = daily_returns(growth_df)
sector_df = sector_investment(pl_df)
ma_df = moving_average_predictions_for_portfolio(
    prices, filtered_holdings["symbol"].unique(), short_window=ma_short, long_window=ma_long
)

# ---------------------------------------------------------------------
# Top metrics
# ---------------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Invested", f"${overall['total_invested']:,.2f}")
c2.metric("Current Value", f"${overall['total_current_value']:,.2f}")
c3.metric("Profit / Loss", f"${overall['total_profit_loss']:,.2f}",
          delta=f"{overall['overall_return_pct']}%")
c4.metric("Overall Return", f"{overall['overall_return_pct']}%")

c5, c6 = st.columns(2)
c5.success(f"🏆 Best Performer: **{bw['best']['symbol']}** ({bw['best']['return_pct']}%)")
c6.error(f"📉 Worst Performer: **{bw['worst']['symbol']}** ({bw['worst']['return_pct']}%)")

st.markdown("---")

# ---------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------
st.subheader("📈 Portfolio Growth Over Time")
fig, ax = plt.subplots(figsize=(11, 4))
ax.plot(growth_df["date"], growth_df["portfolio_value"], color="#2E7D32", linewidth=2)
ax.fill_between(growth_df["date"], growth_df["portfolio_value"], alpha=0.15, color="#2E7D32")
ax.set_xlabel("Date")
ax.set_ylabel("Portfolio Value ($)")
fig.autofmt_xdate()
st.pyplot(fig)
plt.close(fig)

col1, col2 = st.columns(2)
with col1:
    st.subheader("📊 Sector-wise Investment")
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.pie(sector_df["current_value"], labels=sector_df["sector"], autopct="%1.1f%%",
           startangle=90, colors=plt.cm.Set2.colors)
    st.pyplot(fig)
    plt.close(fig)

with col2:
    st.subheader("📉 Daily Return Analysis")
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    colors = ["#4CAF50" if v >= 0 else "#E53935" for v in returns_df["daily_return_pct"]]
    ax.bar(returns_df["date"], returns_df["daily_return_pct"], color=colors)
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_ylabel("Daily Return (%)")
    fig.autofmt_xdate()
    st.pyplot(fig)
    plt.close(fig)

st.markdown("---")

# ---------------------------------------------------------------------
# Profit/Loss table
# ---------------------------------------------------------------------
st.subheader("💰 Profit / Loss by Stock")
st.dataframe(
    pl_df[["symbol", "company", "sector", "quantity", "buy_price", "current_price",
           "invested_amount", "current_value", "profit_loss", "return_pct"]]
    .style.background_gradient(subset=["return_pct"], cmap="RdYlGn"),
    width="stretch",
)

# ---------------------------------------------------------------------
# Bonus: Moving average prediction
# ---------------------------------------------------------------------
st.subheader(f"🔮 Next-Day Trend Prediction (SMA{ma_short} vs SMA{ma_long})")
st.caption("A simple technical-analysis heuristic: when the short-term average "
           "is above the long-term average, the trend is considered bullish, "
           "and vice versa. This is not financial advice.")


def _signal_color(val):
    if "Bullish" in str(val):
        return "background-color: #C8E6C9"
    if "Bearish" in str(val):
        return "background-color: #FFCDD2"
    return "background-color: #F5F5F5"


st.dataframe(
    ma_df.style.map(_signal_color, subset=["signal"]),
    width="stretch",
)

st.markdown("---")

# ---------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------
report_df = build_full_report(pl_df, overall, sector_df, ma_df)
report_csv = report_df.to_csv(index=False).encode("utf-8")
pl_csv = pl_df.to_csv(index=False).encode("utf-8")

dl1, dl2 = st.columns(2)
dl1.download_button("⬇️ Download Full Analytics Report (CSV)", data=report_csv,
                     file_name="portfolio_analytics_report.csv", mime="text/csv")
dl2.download_button("⬇️ Download Profit/Loss Table (CSV)", data=pl_csv,
                     file_name="profit_loss_by_stock.csv", mime="text/csv")
