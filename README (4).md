# 📈 Stock Market Portfolio Analyzer — Day 28

An end-to-end Python project that reads stock price data and your
portfolio holdings, calculates profit/loss per stock, identifies best
and worst performers, computes overall portfolio return, charts
growth/sector allocation/daily returns, predicts next-day trend with a
moving-average crossover, and exports the full analysis to CSV.
Includes a bonus interactive Streamlit dashboard.

## 📁 Project Structure

```
portfolio_analyzer/
├── generate_sample_data.py     # Creates sample holdings + 120 days of price history
├── analyzer.py                  # Core analytics: P/L, returns, sector, moving average
├── main.py                      # CLI pipeline: analyze -> chart -> export CSV
├── streamlit_app.py             # Bonus: interactive dashboard with filters
├── portfolio_holdings.csv       # Pre-generated sample holdings (8 stocks)
├── stock_prices.csv             # Pre-generated sample price history (120 days, 10 stocks)
├── requirements.txt
└── README.md
```

## 🚀 Setup

```bash
pip install -r requirements.txt
```

Sample data is already included, so everything runs immediately. To
regenerate it (or create a fresh random portfolio):

```bash
python generate_sample_data.py
```

## 📄 Expected CSV formats

**`portfolio_holdings.csv`** — what you own:

| Column | Description |
|---|---|
| `symbol` | Stock ticker, e.g. `AAPL` |
| `company` | Company name |
| `sector` | e.g. `Technology`, `Energy` |
| `quantity` | Shares owned |
| `buy_price` | Price per share when bought |
| `buy_date` | `YYYY-MM-DD` |

**`stock_prices.csv`** — daily price history for every symbol you hold:

| Column | Description |
|---|---|
| `date` | `YYYY-MM-DD` |
| `symbol` | Must match a symbol in holdings |
| `close_price` | Closing price that day |

## ▶️ Run the CLI version

```bash
python main.py --holdings portfolio_holdings.csv --prices stock_prices.csv --output_dir output
```

Prints to console: per-stock profit/loss, best & worst performers,
overall portfolio return, sector breakdown, and moving-average trend
predictions. Writes to `output/`:

- **`portfolio_analytics_report.csv`** — full report, one row per metric
- **`profit_loss_by_stock.csv`** — detailed P/L table
- **`portfolio_growth_chart.png`** — 📈 portfolio value over time
- **`sector_investment_chart.png`** — 📊 sector-wise investment pie chart
- **`daily_return_chart.png`** — 📉 daily return bar chart (green = gain, red = loss)

Adjust the moving-average windows with `--ma_short` / `--ma_long`
(defaults: 5-day and 20-day).

## 🌐 Run the Streamlit dashboard (bonus)

```bash
streamlit run streamlit_app.py
```

In the sidebar you can upload your own holdings + price CSVs (or use
the bundled sample data), filter by sector or stock symbol, and tune
the moving-average windows live. The dashboard shows: portfolio
metrics, best/worst performer callouts, all three required charts, a
color-coded profit/loss table, a color-coded trend-prediction table,
and CSV download buttons.

## 🧮 How things are calculated

- **Profit/Loss** = (current price − buy price) × quantity, using the
  most recent close price in `stock_prices.csv`.
- **Overall portfolio return** = total profit/loss ÷ total invested,
  across all holdings.
- **Portfolio growth over time** — for each date, sums `quantity ×
  close price` for every stock already owned by that date (a stock
  only contributes after its `buy_date`), so the growth line steps up
  each time a new position is added.
- **Sector-wise investment** — current market value grouped by sector.
- **Moving average trend prediction** — a short-window SMA (default 5
  days) vs. a long-window SMA (default 20 days). Short MA meaningfully
  above long MA → "Uptrend (Bullish)"; meaningfully below → "Downtrend
  (Bearish)"; close together → "Sideways / Neutral." This is a classic,
  simple technical-analysis heuristic — **not financial advice**, and
  real markets are influenced by far more than price history.

## ✏️ Customizing

- Add more stocks/sectors by editing the `STOCKS` list in
  `generate_sample_data.py`.
- Change moving-average sensitivity via `--ma_short`/`--ma_long` (CLI)
  or the sidebar number inputs (dashboard).
- Chart styling lives in `main.py` (CLI charts) and `streamlit_app.py`
  (dashboard charts).
