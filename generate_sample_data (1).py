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
