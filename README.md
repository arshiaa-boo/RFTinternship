# 💰 Smart Expense Tracker & Budget Analyzer
Day 29 — Python Internship Project

## What it does
1. **Import monthly expense data** — loads transactions from a CSV (`date, description, amount`).
2. **Categorize expenses automatically** — keyword-based rules sort each transaction into
   Groceries, Food & Dining, Transport, Utilities, Rent, Entertainment, Health & Fitness,
   Shopping, or Income.
3. **Calculate monthly savings** — income minus expenses, plus a savings-rate %, per month.
4. **Generate budget summary** — compares average monthly spend per category against a
   configurable budget and flags over/under.
5. **Visualize spending trends** — 4 charts: income vs expense vs savings, category pie chart,
   budget vs actual bar chart, and a daily spending trend line.
6. **Export final report** — a text summary (`budget_report.txt`) plus CSVs for the
   categorized transactions, monthly summary, and budget summary.

### Bonus
- **Expense prediction** (`predict_expenses.py`) — fits a simple linear trend to each
  category's monthly totals and forecasts next month's spend.
- **Streamlit dashboard** (`app.py`) — interactive version of the whole pipeline: upload
  your own CSV, filter by month, see live charts, budget table, and predictions.

## Setup
```bash
pip install pandas matplotlib streamlit plotly
```

## Run the core pipeline
```bash
python expense_tracker.py
```
Outputs land in `outputs/` (CSVs + text report) and `charts/` (PNG charts).

## Run the prediction bonus
```bash
python predict_expenses.py
```

## Run the dashboard bonus
```bash
streamlit run app.py
```
Then open the local URL Streamlit prints (usually http://localhost:8501).
Use the sidebar to upload your own transactions CSV, or leave it to use the bundled sample data.

## File structure
```
expense_tracker/
├── data/
│   └── transactions.csv       # sample 3-month transaction history
├── expense_tracker.py         # core pipeline (steps 1-6)
├── predict_expenses.py        # bonus: next-month prediction
├── app.py                     # bonus: Streamlit dashboard
├── outputs/                   # generated CSVs + text report
├── charts/                    # generated PNG charts
└── README.md
```

## Customizing
- **Categories**: edit `CATEGORY_RULES` in `expense_tracker.py` — add keywords per category.
- **Budgets**: edit `MONTHLY_BUDGETS` in `expense_tracker.py`.
- **Your own data**: replace `data/transactions.csv` with your own export (same 3 columns),
  or upload it directly in the Streamlit dashboard.
