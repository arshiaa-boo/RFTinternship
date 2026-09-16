
import argparse
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from analyzer import (
    load_holdings, load_prices, profit_loss_table, best_worst_performers,
    overall_portfolio_return, portfolio_growth_over_time, daily_returns,
    sector_investment, moving_average_predictions_for_portfolio, build_full_report,
)


def plot_portfolio_growth(growth_df, out_path):
    plt.figure(figsize=(10, 5.5))
    plt.plot(growth_df["date"], growth_df["portfolio_value"], color="#2E7D32", linewidth=2)
    plt.fill_between(growth_df["date"], growth_df["portfolio_value"], alpha=0.15, color="#2E7D32")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.title("Portfolio Growth Over Time")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_sector_investment(sector_df, out_path):
    plt.figure(figsize=(7, 7))
    plt.pie(
        sector_df["current_value"], labels=sector_df["sector"], autopct="%1.1f%%",
        startangle=90, colors=plt.cm.Set2.colors,
    )
    plt.title("Sector-wise Investment (Current Value)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def plot_daily_returns(returns_df, out_path):
    plt.figure(figsize=(10, 5))
    colors = ["#4CAF50" if v >= 0 else "#E53935" for v in returns_df["daily_return_pct"]]
    plt.bar(returns_df["date"], returns_df["daily_return_pct"], color=colors)
    plt.axhline(0, color="black", linewidth=0.8)
    plt.xlabel("Date")
    plt.ylabel("Daily Return (%)")
    plt.title("Daily Portfolio Return Analysis")
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def run(holdings_csv, prices_csv, output_dir="output", ma_short=5, ma_long=20):
    os.makedirs(output_dir, exist_ok=True)

    holdings = load_holdings(holdings_csv)
    prices = load_prices(prices_csv)

    # --- Profit / Loss ---
    pl_df = profit_loss_table(holdings, prices)
    print("\n=== Profit / Loss by Stock ===")
    print(pl_df[["symbol", "company", "sector", "quantity", "buy_price",
                  "current_price", "invested_amount", "current_value",
                  "profit_loss", "return_pct"]].to_string(index=False))

    # --- Best / Worst performers ---
    bw = best_worst_performers(pl_df)
    print(f"\n🏆 Best Performer:  {bw['best']['symbol']} ({bw['best']['return_pct']}%)")
    print(f"📉 Worst Performer: {bw['worst']['symbol']} ({bw['worst']['return_pct']}%)")

    # --- Overall return ---
    overall = overall_portfolio_return(pl_df)
    print("\n=== Overall Portfolio Return ===")
    for k, v in overall.items():
        print(f"{k}: {v}")

    # --- Growth & daily returns ---
    growth_df = portfolio_growth_over_time(holdings, prices)
    returns_df = daily_returns(growth_df)

    # --- Sector breakdown ---
    sector_df = sector_investment(pl_df)
    print("\n=== Sector-wise Investment ===")
    print(sector_df.to_string(index=False))

    # --- Bonus: Moving Average trend prediction ---
    ma_df = moving_average_predictions_for_portfolio(
        prices, holdings["symbol"].unique(), short_window=ma_short, long_window=ma_long
    )
    print(f"\n=== Moving Average Trend Prediction (SMA{ma_short} vs SMA{ma_long}) ===")
    print(ma_df.to_string(index=False))

    # --- Charts ---
    plot_portfolio_growth(growth_df, os.path.join(output_dir, "portfolio_growth_chart.png"))
    plot_sector_investment(sector_df, os.path.join(output_dir, "sector_investment_chart.png"))
    plot_daily_returns(returns_df, os.path.join(output_dir, "daily_return_chart.png"))
    print(f"\nCharts saved to '{output_dir}/'")

    # --- Exports ---
    pl_path = os.path.join(output_dir, "profit_loss_by_stock.csv")
    pl_df.to_csv(pl_path, index=False)

    report_df = build_full_report(pl_df, overall, sector_df, ma_df)
    report_path = os.path.join(output_dir, "portfolio_analytics_report.csv")
    report_df.to_csv(report_path, index=False)

    print(f"Per-stock P/L exported to '{pl_path}'")
    print(f"Full analytics report exported to '{report_path}'")

    return pl_df, overall, report_df


def _parse_args():
    p = argparse.ArgumentParser(description="Stock Market Portfolio Analyzer")
    p.add_argument("--holdings", default="portfolio_holdings.csv", help="Path to holdings CSV")
    p.add_argument("--prices", default="stock_prices.csv", help="Path to historical prices CSV")
    p.add_argument("--output_dir", default="output", help="Folder for charts/report")
    p.add_argument("--ma_short", type=int, default=5, help="Short moving-average window (days)")
    p.add_argument("--ma_long", type=int, default=20, help="Long moving-average window (days)")
    return p.parse_args()


if __name__ == "__main__":
    args = _parse_args()
    run(
        holdings_csv=args.holdings,
        prices_csv=args.prices,
        output_dir=args.output_dir,
        ma_short=args.ma_short,
        ma_long=args.ma_long,
    )
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
"""
analyzer.py
-----------
Core analytics engine for the Stock Market Portfolio Analyzer.

Expects two DataFrames:
    holdings_df: symbol, company, sector, quantity, buy_price, buy_date
    prices_df:   date, symbol, close_price   (daily history for each symbol)
"""

import pandas as pd

HOLDINGS_COLUMNS = ["symbol", "company", "sector", "quantity", "buy_price", "buy_date"]
PRICES_COLUMNS = ["date", "symbol", "close_price"]


def load_holdings(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    missing = [c for c in HOLDINGS_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Holdings CSV missing column(s): {missing}. Expected: {HOLDINGS_COLUMNS}")
    df["buy_date"] = pd.to_datetime(df["buy_date"], errors="coerce")
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df["buy_price"] = pd.to_numeric(df["buy_price"], errors="coerce")
    return df


def load_prices(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    missing = [c for c in PRICES_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Prices CSV missing column(s): {missing}. Expected: {PRICES_COLUMNS}")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["close_price"] = pd.to_numeric(df["close_price"], errors="coerce")
    return df.sort_values(["symbol", "date"]).reset_index(drop=True)


def latest_prices(prices_df: pd.DataFrame) -> pd.Series:
    """Most recent close price per symbol."""
    idx = prices_df.groupby("symbol")["date"].idxmax()
    latest = prices_df.loc[idx].set_index("symbol")["close_price"]
    return latest


def profit_loss_table(holdings_df: pd.DataFrame, prices_df: pd.DataFrame) -> pd.DataFrame:
    current = latest_prices(prices_df)
    df = holdings_df.copy()
    df["current_price"] = df["symbol"].map(current)
    df["invested_amount"] = (df["quantity"] * df["buy_price"]).round(2)
    df["current_value"] = (df["quantity"] * df["current_price"]).round(2)
    df["profit_loss"] = (df["current_value"] - df["invested_amount"]).round(2)
    df["return_pct"] = ((df["profit_loss"] / df["invested_amount"]) * 100).round(2)
    return df.sort_values("return_pct", ascending=False).reset_index(drop=True)


def best_worst_performers(pl_df: pd.DataFrame) -> dict:
    if pl_df.empty:
        return {"best": None, "worst": None}
    best = pl_df.iloc[pl_df["return_pct"].idxmax()]
    worst = pl_df.iloc[pl_df["return_pct"].idxmin()]
    return {"best": best, "worst": worst}


def overall_portfolio_return(pl_df: pd.DataFrame) -> dict:
    total_invested = pl_df["invested_amount"].sum()
    total_current = pl_df["current_value"].sum()
    total_pl = total_current - total_invested
    overall_return_pct = (total_pl / total_invested * 100) if total_invested else 0
    return {
        "total_invested": round(total_invested, 2),
        "total_current_value": round(total_current, 2),
        "total_profit_loss": round(total_pl, 2),
        "overall_return_pct": round(overall_return_pct, 2),
    }


def portfolio_growth_over_time(holdings_df: pd.DataFrame, prices_df: pd.DataFrame) -> pd.DataFrame:
    """Total portfolio market value for each date, counting only shares
    already owned by that date (i.e. after each holding's buy_date)."""
    pivot = prices_df.pivot(index="date", columns="symbol", values="close_price").sort_index()
    pivot = pivot.ffill()

    total_value = pd.Series(0.0, index=pivot.index)
    for _, h in holdings_df.iterrows():
        if h["symbol"] not in pivot.columns:
            continue
        owned_mask = pivot.index >= h["buy_date"]
        total_value.loc[owned_mask] += pivot.loc[owned_mask, h["symbol"]] * h["quantity"]

    growth_df = total_value.reset_index()
    growth_df.columns = ["date", "portfolio_value"]
    # Only keep dates from the earliest buy onward (value is 0 before that)
    growth_df = growth_df[growth_df["portfolio_value"] > 0].reset_index(drop=True)
    return growth_df


def daily_returns(growth_df: pd.DataFrame) -> pd.DataFrame:
    df = growth_df.copy()
    df["daily_return_pct"] = df["portfolio_value"].pct_change().mul(100).round(3)
    return df.dropna().reset_index(drop=True)


def sector_investment(pl_df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        pl_df.groupby("sector")
        .agg(invested_amount=("invested_amount", "sum"),
             current_value=("current_value", "sum"),
             profit_loss=("profit_loss", "sum"))
        .reset_index()
        .sort_values("current_value", ascending=False)
    )
    summary[["invested_amount", "current_value", "profit_loss"]] = summary[
        ["invested_amount", "current_value", "profit_loss"]
    ].round(2)
    return summary


def moving_average_prediction(prices_df: pd.DataFrame, symbol: str,
                               short_window: int = 5, long_window: int = 20) -> dict:
    """Simple trend signal: compare a short-term SMA to a long-term SMA.
    Short MA above long MA => bullish (price likely to keep rising).
    Short MA below long MA => bearish (price likely to keep falling).
    This is a classic (and simple) technical-analysis heuristic, not a
    guarantee -- real markets are far more complex."""
    series = prices_df[prices_df["symbol"] == symbol].sort_values("date")["close_price"]
    if len(series) < long_window:
        return {"symbol": symbol, "signal": "Not enough data", "short_ma": None,
                "long_ma": None, "last_price": series.iloc[-1] if len(series) else None}

    short_ma = series.rolling(short_window).mean().iloc[-1]
    long_ma = series.rolling(long_window).mean().iloc[-1]
    last_price = series.iloc[-1]

    diff_pct = ((short_ma - long_ma) / long_ma) * 100
    if diff_pct > 0.5:
        signal = "Uptrend (Bullish)"
    elif diff_pct < -0.5:
        signal = "Downtrend (Bearish)"
    else:
        signal = "Sideways / Neutral"

    return {
        "symbol": symbol,
        "last_price": round(last_price, 2),
        "short_ma": round(short_ma, 2),
        "long_ma": round(long_ma, 2),
        "signal": signal,
        "signal_strength_pct": round(diff_pct, 2),
    }


def moving_average_predictions_for_portfolio(prices_df: pd.DataFrame, symbols,
                                              short_window: int = 5, long_window: int = 20) -> pd.DataFrame:
    rows = [moving_average_prediction(prices_df, s, short_window, long_window) for s in symbols]
    return pd.DataFrame(rows)


def build_full_report(pl_df: pd.DataFrame, overall: dict, sector_df: pd.DataFrame,
                       ma_df: pd.DataFrame) -> pd.DataFrame:
    """Combine everything into one tidy report DataFrame for CSV export."""
    rows = []

    for key, val in overall.items():
        rows.append({"section": "Portfolio Summary", "metric": key, "value": val})

    for _, r in pl_df.iterrows():
        rows.append({"section": "Per-Stock Profit/Loss", "metric": r["symbol"],
                     "value": f"invested {r['invested_amount']}, current {r['current_value']}, "
                              f"P/L {r['profit_loss']} ({r['return_pct']}%)"})

    for _, r in sector_df.iterrows():
        rows.append({"section": "Sector-wise Investment", "metric": r["sector"],
                     "value": f"current value {r['current_value']}, P/L {r['profit_loss']}"})

    for _, r in ma_df.iterrows():
        rows.append({"section": "Moving Average Trend Prediction", "metric": r["symbol"],
                     "value": r["signal"]})

    return pd.DataFrame(rows)
"""
generate_sample_data.py
------------------------
Creates two sample CSVs so the Portfolio Analyzer can be tested
immediately:

    portfolio_holdings.csv  -> what you bought (symbol, sector, qty, buy price/date)
    stock_prices.csv        -> daily closing price history for each symbol

Run once:
    python generate_sample_data.py
"""

import random
import csv
from datetime import datetime, timedelta

random.seed(7)

STOCKS = [
    {"symbol": "AAPL",  "company": "Apple Inc.",        "sector": "Technology",           "start_price": 190},
    {"symbol": "MSFT",  "company": "Microsoft Corp.",    "sector": "Technology",           "start_price": 410},
    {"symbol": "GOOGL", "company": "Alphabet Inc.",      "sector": "Technology",           "start_price": 165},
    {"symbol": "NVDA",  "company": "NVIDIA Corp.",       "sector": "Technology",           "start_price": 120},
    {"symbol": "AMZN",  "company": "Amazon.com Inc.",    "sector": "Consumer Discretionary", "start_price": 178},
    {"symbol": "TSLA",  "company": "Tesla Inc.",         "sector": "Consumer Discretionary", "start_price": 240},
    {"symbol": "META",  "company": "Meta Platforms",     "sector": "Communication Services", "start_price": 480},
    {"symbol": "JPM",   "company": "JPMorgan Chase",     "sector": "Financials",           "start_price": 195},
    {"symbol": "KO",    "company": "Coca-Cola Co.",      "sector": "Consumer Staples",      "start_price": 62},
    {"symbol": "XOM",   "company": "Exxon Mobil Corp.",  "sector": "Energy",               "start_price": 112},
]

NUM_DAYS = 120
# Each stock gets a mild random drift (trend) plus daily noise, so some
# clearly outperform and some clearly underperform - useful for best/worst.
DRIFTS = {
    "AAPL": 0.0010, "MSFT": 0.0014, "GOOGL": 0.0006, "NVDA": 0.0035,
    "AMZN": 0.0008, "TSLA": -0.0015, "META": 0.0012, "JPM": 0.0004,
    "KO": 0.0001, "XOM": -0.0006,
}
VOLATILITY = {
    "AAPL": 0.014, "MSFT": 0.013, "GOOGL": 0.016, "NVDA": 0.030,
    "AMZN": 0.018, "TSLA": 0.035, "META": 0.020, "JPM": 0.012,
    "KO": 0.007, "XOM": 0.015,
}


def generate_price_series(start_price, num_days, drift, volatility):
    prices = [start_price]
    for _ in range(num_days - 1):
        change_pct = random.gauss(drift, volatility)
        new_price = max(1.0, prices[-1] * (1 + change_pct))
        prices.append(round(new_price, 2))
    return prices


def generate_stock_prices(output_path="stock_prices.csv"):
    start_date = datetime.now() - timedelta(days=NUM_DAYS)
    dates = [start_date + timedelta(days=i) for i in range(NUM_DAYS)]

    series_by_symbol = {}
    rows = []
    for stock in STOCKS:
        series = generate_price_series(
            stock["start_price"], NUM_DAYS,
            DRIFTS[stock["symbol"]], VOLATILITY[stock["symbol"]],
        )
        series_by_symbol[stock["symbol"]] = series
        for d, price in zip(dates, series):
            rows.append({
                "date": d.strftime("%Y-%m-%d"),
                "symbol": stock["symbol"],
                "close_price": price,
            })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["date", "symbol", "close_price"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} price rows for {len(STOCKS)} stocks -> {output_path}")
    return dates, series_by_symbol


def generate_holdings(dates, series_by_symbol, output_path="portfolio_holdings.csv"):
    """Pick a subset of stocks, buy them at some point in the past, using
    the SAME price series already generated so buy_price is consistent
    with stock_prices.csv."""
    chosen = random.sample(STOCKS, k=8)
    rows = []
    for stock in chosen:
        buy_day_index = random.randint(0, NUM_DAYS - 20)  # bought a while ago
        buy_date = dates[buy_day_index]
        buy_price = series_by_symbol[stock["symbol"]][buy_day_index]
        quantity = random.randint(10, 80)

        rows.append({
            "symbol": stock["symbol"],
            "company": stock["company"],
            "sector": stock["sector"],
            "quantity": quantity,
            "buy_price": buy_price,
            "buy_date": buy_date.strftime("%Y-%m-%d"),
        })

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["symbol", "company", "sector", "quantity", "buy_price", "buy_date"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows)} holdings -> {output_path}")


if __name__ == "__main__":
    dates, series_by_symbol = generate_stock_prices()
    generate_holdings(dates, series_by_symbol)
