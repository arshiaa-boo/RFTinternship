
import os
import re
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ----------------------------------------------------------------
# CONFIG — edit these to fit your own data / categories / budgets
# ----------------------------------------------------------------

DATA_FILE = "transactions.csv"
CHARTS_DIR = "charts"
OUTPUTS_DIR = "outputs"

# keyword -> category. Add/remove keywords freely.
CATEGORY_RULES = {
    "Groceries":        ["grocery", "bazaar", "supermarket", "dmart"],
    "Food & Dining":     ["zomato", "swiggy", "restaurant", "cafe", "dinner", "lunch"],
    "Transport":         ["uber", "ola", "petrol", "fuel", "metro", "cab"],
    "Utilities":         ["electricity", "water bill", "internet", "airtel", "bses", "recharge", "jio"],
    "Rent":              ["rent"],
    "Entertainment":     ["netflix", "spotify", "movie", "pvr", "prime video", "hotstar"],
    "Health & Fitness":  ["pharmacy", "apollo", "gym", "hospital", "doctor"],
    "Shopping":          ["amazon", "flipkart", "myntra", "shopping"],
    "Income":            ["salary", "freelance", "income", "bonus"],
}
DEFAULT_CATEGORY = "Other"

# your monthly budget per category (edit to match your own limits)
MONTHLY_BUDGETS = {
    "Groceries": 6000,
    "Food & Dining": 1800,
    "Transport": 800,
    "Utilities": 3500,
    "Rent": 15000,
    "Entertainment": 700,
    "Health & Fitness": 1200,
    "Shopping": 4000,
    "Other": 1000,
}


# ----------------------------------------------------------------
# 0. Auto-generate sample data if no CSV is found
# ----------------------------------------------------------------

def create_sample_data(path: str):
    """Writes 3 months of realistic sample transactions so the script
    runs immediately even if you haven't supplied your own CSV yet."""
    rows = []
    base_txns = [
        ("Big Bazaar Grocery", -2450), ("Monthly Salary", 65000),
        ("Uber Ride", -320), ("Netflix Subscription", -499),
        ("Electricity Bill BSES", -1850), ("Zomato Order", -540),
        ("Amazon Shopping", -3200), ("Apollo Pharmacy", -680),
        ("Movie Tickets PVR", -900), ("Rent Payment", -15000),
        ("Swiggy Order", -410), ("Gym Membership", -1500),
        ("Mobile Recharge Jio", -599), ("Petrol Pump", -2000),
        ("Big Bazaar Grocery", -1980), ("Spotify Subscription", -119),
        ("Ola Ride", -280), ("Water Bill", -450),
        ("Flipkart Shopping", -2100), ("Restaurant Dinner", -1650),
        ("Internet Bill Airtel", -999),
    ]
    months = ["2026-06", "2026-07", "2026-08"]
    day = 2
    for m_i, month in enumerate(months):
        day = 2
        for desc, amt in base_txns:
            # add small month-to-month variation so trends look realistic
            variation = 1 + (m_i * 0.06) + (np.random.uniform(-0.05, 0.05))
            amount = round(amt * (variation if amt < 0 else 1), 2)
            date = f"{month}-{min(day, 28):02d}"
            rows.append((date, desc, amount))
            day += 1

    df = pd.DataFrame(rows, columns=["date", "description", "amount"])
    df.to_csv(path, index=False)
    print(f"No '{path}' found — generated sample data with {len(df)} transactions.")


# ----------------------------------------------------------------
# 1. Import monthly expense data
# ----------------------------------------------------------------

def load_transactions(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        create_sample_data(path)
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df["amount"] = df["amount"].astype(float)
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df


# ----------------------------------------------------------------
# 2. Categorize expenses automatically
# ----------------------------------------------------------------

def categorize(description: str) -> str:
    text = description.lower()
    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if re.search(re.escape(kw), text):
                return category
    return DEFAULT_CATEGORY


def add_categories(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["category"] = df["description"].apply(categorize)
    df["type"] = df["amount"].apply(lambda a: "Income" if a > 0 else "Expense")
    return df


# ----------------------------------------------------------------
# 3. Calculate monthly savings
# ----------------------------------------------------------------

def monthly_summary(df: pd.DataFrame) -> pd.DataFrame:
    grp = df.groupby("month").apply(
        lambda g: pd.Series({
            "income": g.loc[g["amount"] > 0, "amount"].sum(),
            "expenses": -g.loc[g["amount"] < 0, "amount"].sum(),
        }),
        include_groups=False,
    )
    grp["savings"] = grp["income"] - grp["expenses"]
    grp["savings_rate_%"] = (grp["savings"] / grp["income"] * 100).round(1)
    return grp.reset_index()


# ----------------------------------------------------------------
# 4. Generate budget summary
# ----------------------------------------------------------------

def budget_summary(df: pd.DataFrame) -> pd.DataFrame:
    exp = df[(df["amount"] < 0) & (df["category"] != "Income")].copy()
    exp["amount"] = -exp["amount"]
    n_months = exp["month"].nunique() or 1
    cat_totals = exp.groupby("category")["amount"].sum()

    rows = []
    for cat, total in cat_totals.items():
        avg_monthly = total / n_months
        budget = MONTHLY_BUDGETS.get(cat, 1500)
        rows.append({
            "category": cat,
            "total_spent": round(total, 2),
            "avg_monthly_spent": round(avg_monthly, 2),
            "monthly_budget": budget,
            "status": "Over Budget" if avg_monthly > budget else "Within Budget",
            "variance": round(budget - avg_monthly, 2),
        })
    return pd.DataFrame(rows).sort_values("total_spent", ascending=False).reset_index(drop=True)


# ----------------------------------------------------------------
# 5. Visualize spending trends
# ----------------------------------------------------------------

def make_charts(df: pd.DataFrame, summary: pd.DataFrame, budget: pd.DataFrame, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid")

    # Chart 1: Income vs Expenses vs Savings
    fig, ax = plt.subplots(figsize=(8, 5))
    idx = range(len(summary))
    ax.bar([i - 0.18 for i in idx], summary["income"], 0.35, label="Income", color="#2e7d32")
    ax.bar([i + 0.18 for i in idx], summary["expenses"], 0.35, label="Expenses", color="#c62828")
    ax.plot(idx, summary["savings"], marker="o", color="#1565c0", linewidth=2, label="Savings")
    ax.set_xticks(list(idx))
    ax.set_xticklabels(summary["month"])
    ax.set_ylabel("Amount (Rs)")
    ax.set_title("Monthly Income vs Expenses vs Savings")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "monthly_income_vs_expense.png"), dpi=150)
    plt.close(fig)

    # Chart 2: Spend by category (pie)
    exp = df[(df["amount"] < 0) & (df["category"] != "Income")].copy()
    exp["amount"] = -exp["amount"]
    cat_totals = exp.groupby("category")["amount"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(cat_totals.values, labels=cat_totals.index, autopct="%1.1f%%",
           startangle=90, colors=plt.cm.tab20.colors)
    ax.set_title("Total Spending by Category")
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "spending_by_category.png"), dpi=150)
    plt.close(fig)

    # Chart 3: Budget vs actual
    fig, ax = plt.subplots(figsize=(9, 5))
    idx = range(len(budget))
    ax.bar([i - 0.2 for i in idx], budget["avg_monthly_spent"], 0.4, label="Avg Monthly Spent", color="#ef6c00")
    ax.bar([i + 0.2 for i in idx], budget["monthly_budget"], 0.4, label="Budget", color="#455a64")
    ax.set_xticks(list(idx))
    ax.set_xticklabels(budget["category"], rotation=35, ha="right")
    ax.set_ylabel("Amount (Rs)")
    ax.set_title("Average Monthly Spend vs Budget")
    ax.legend()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "budget_vs_actual.png"), dpi=150)
    plt.close(fig)

    # Chart 4: Daily spending trend
    daily = df[df["amount"] < 0].groupby("date")["amount"].sum().abs()
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(daily.index, daily.values, color="#6a1b9a", linewidth=1.5)
    ax.fill_between(daily.index, daily.values, alpha=0.2, color="#6a1b9a")
    ax.set_title("Daily Spending Trend")
    ax.set_ylabel("Amount (Rs)")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(os.path.join(out_dir, "daily_spending_trend.png"), dpi=150)
    plt.close(fig)

    return ["monthly_income_vs_expense.png", "spending_by_category.png",
            "budget_vs_actual.png", "daily_spending_trend.png"]


# ----------------------------------------------------------------
# Bonus: predict next month's spend per category (linear trend)
# ----------------------------------------------------------------

def predict_next_month(df: pd.DataFrame):
    exp = df[(df["amount"] < 0) & (df["category"] != "Income")].copy()
    exp["amount"] = -exp["amount"]
    monthly_cat = exp.groupby(["month", "category"])["amount"].sum().unstack(fill_value=0).sort_index()

    preds = {}
    for cat in monthly_cat.columns:
        values = monthly_cat[cat]
        if len(values) == 1:
            preds[cat] = float(values.iloc[0])
        else:
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values.values, 1)
            preds[cat] = max(slope * len(values) + intercept, 0)

    pred_df = pd.DataFrame({
        "category": list(preds.keys()),
        "predicted_next_month": [round(v, 2) for v in preds.values()],
    }).sort_values("predicted_next_month", ascending=False).reset_index(drop=True)

    return pred_df, pred_df["predicted_next_month"].sum()


# ----------------------------------------------------------------
# 6. Export final report
# ----------------------------------------------------------------

def export_report(df, summary, budget, pred_df, total_predicted, out_dir):
    os.makedirs(out_dir, exist_ok=True)

    df.to_csv(os.path.join(out_dir, "categorized_transactions.csv"), index=False)
    summary.to_csv(os.path.join(out_dir, "monthly_summary.csv"), index=False)
    budget.to_csv(os.path.join(out_dir, "budget_summary.csv"), index=False)
    pred_df.to_csv(os.path.join(out_dir, "next_month_prediction.csv"), index=False)

    lines = []
    lines.append("=" * 60)
    lines.append("  SMART EXPENSE TRACKER — BUDGET REPORT")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)
    lines.append("")
    lines.append("MONTHLY SUMMARY")
    lines.append("-" * 60)
    for _, row in summary.iterrows():
        lines.append(
            f"{row['month']}: Income Rs{row['income']:,.0f} | "
            f"Expenses Rs{row['expenses']:,.0f} | "
            f"Savings Rs{row['savings']:,.0f} ({row['savings_rate_%']}%)"
        )
    lines.append("")
    lines.append(f"Average savings rate: {summary['savings_rate_%'].mean():.1f}%")
    lines.append("")
    lines.append("BUDGET vs ACTUAL (average monthly)")
    lines.append("-" * 60)
    for _, row in budget.iterrows():
        flag = "[OVER] " if row["status"] == "Over Budget" else "[OK]   "
        lines.append(
            f"{flag}{row['category']:<18} spent Rs{row['avg_monthly_spent']:>8,.0f} "
            f"/ budget Rs{row['monthly_budget']:>8,.0f}  ({row['status']})"
        )
    lines.append("")
    over = budget[budget["status"] == "Over Budget"]
    lines.append("Over budget in: " + ", ".join(over["category"]) if not over.empty
                  else "All categories within budget.")
    lines.append("")
    lines.append("PREDICTED SPEND — NEXT MONTH")
    lines.append("-" * 60)
    for _, row in pred_df.iterrows():
        lines.append(f"{row['category']:<18} Rs{row['predicted_next_month']:>10,.0f}")
    lines.append(f"\nPredicted TOTAL next month: Rs{total_predicted:,.0f}")
    lines.append("")
    lines.append("=" * 60)

    report_text = "\n".join(lines)
    with open(os.path.join(out_dir, "budget_report.txt"), "w") as f:
        f.write(report_text)
    return report_text


# ----------------------------------------------------------------
# MAIN
# ----------------------------------------------------------------

def main():
    print("Step 1/6: Importing transaction data...")
    df = load_transactions(DATA_FILE)
    print(f"  Loaded {len(df)} transactions across {df['month'].nunique()} months.")

    print("Step 2/6: Categorizing expenses...")
    df = add_categories(df)

    print("Step 3/6: Calculating monthly savings...")
    summary = monthly_summary(df)

    print("Step 4/6: Generating budget summary...")
    budget = budget_summary(df)

    print("Step 5/6: Creating visualizations...")
    charts = make_charts(df, summary, budget, CHARTS_DIR)
    print(f"  Saved: {charts}")

    print("Bonus: Predicting next month's spend...")
    pred_df, total_predicted = predict_next_month(df)

    print("Step 6/6: Exporting final report...")
    report_text = export_report(df, summary, budget, pred_df, total_predicted, OUTPUTS_DIR)

    print("\n" + report_text)
    print(f"\nAll files saved in '{OUTPUTS_DIR}/' (reports/CSVs) and '{CHARTS_DIR}/' (charts).")


if __name__ == "__main__":
    main()
