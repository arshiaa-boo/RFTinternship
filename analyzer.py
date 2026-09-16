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
